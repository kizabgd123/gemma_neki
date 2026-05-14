import pandas as pd
import numpy as np
import lightgbm as lgb
from catboost import CatBoostClassifier, Pool
from xgboost import XGBClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import RidgeClassifier, LogisticRegression
import os
import json
import gc

def load_fe_data():
    train = pd.read_parquet('train_fe_v2.parquet')
    test = pd.read_parquet('test_fe_v2.parquet')
    return train, test

def train_lgb(X, y, X_test, cat_features, n_splits=5, seed=42):
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'verbosity': -1,
        'boosting_type': 'gbdt',
        'random_state': seed,
        'learning_rate': 0.02,
        'num_leaves': 127,
        'feature_fraction': 0.7,
        'bagging_fraction': 0.7,
        'bagging_freq': 5,
        'max_depth': -1,
        'min_data_in_leaf': 50
    }

    for fold, (train_idx, val_idx) in enumerate(folds.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        dtrain = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features)
        dval = lgb.Dataset(X_val, label=y_val, reference=dtrain, categorical_feature=cat_features)
        
        model = lgb.train(params, dtrain, valid_sets=[dtrain, dval], num_boost_round=3000, callbacks=[lgb.early_stopping(100), lgb.log_evaluation(500)])
        
        oof_preds[val_idx] = model.predict(X_val, num_iteration=model.best_iteration)
        test_preds += model.predict(X_test, num_iteration=model.best_iteration) / n_splits
        
    return oof_preds, test_preds, roc_auc_score(y, oof_preds)

def train_cat(X, y, X_test, cat_features, n_splits=5, seed=42):
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    
    params = {
        'loss_function': 'Logloss', 'eval_metric': 'AUC', 'random_seed': seed,
        'learning_rate': 0.03, 'iterations': 3000, 'depth': 8, 'l2_leaf_reg': 5,
        'bootstrap_type': 'Bayesian', 'bagging_temperature': 1, 'task_type': 'CPU', 'verbose': 500
    }

    for fold, (train_idx, val_idx) in enumerate(folds.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        train_pool = Pool(X_train, y_train, cat_features=cat_features)
        val_pool = Pool(X_val, y_val, cat_features=cat_features)
        model = CatBoostClassifier(**params)
        model.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        oof_preds[val_idx] = model.predict_proba(X_val)[:, 1]
        test_preds += model.predict_proba(X_test)[:, 1] / n_splits
        
    return oof_preds, test_preds, roc_auc_score(y, oof_preds)

def train_xgb(X, y, X_test, n_splits=5, seed=42):
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    
    params = {
        'objective': 'binary:logistic', 'eval_metric': 'auc', 'random_state': seed,
        'learning_rate': 0.03, 'max_depth': 8, 'subsample': 0.8, 'colsample_bytree': 0.8,
        'n_estimators': 3000, 'early_stopping_rounds': 100, 'verbosity': 1
    }

    for fold, (train_idx, val_idx) in enumerate(folds.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model = XGBClassifier(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=500)
        oof_preds[val_idx] = model.predict_proba(X_val)[:, 1]
        test_preds += model.predict_proba(X_test)[:, 1] / n_splits
        
    return oof_preds, test_preds, roc_auc_score(y, oof_preds)

def train_hgb(X, y, X_test, n_splits=5, seed=42):
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    
    for fold, (train_idx, val_idx) in enumerate(folds.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model = HistGradientBoostingClassifier(max_iter=1000, learning_rate=0.05, max_depth=10, random_state=seed)
        model.fit(X_train, y_train)
        oof_preds[val_idx] = model.predict_proba(X_val)[:, 1]
        test_preds += model.predict_proba(X_test)[:, 1] / n_splits
        
    return oof_preds, test_preds, roc_auc_score(y, oof_preds)

def main():
    print("--- Starting S6E5 Super Ensemble Training ---")
    train, test = load_fe_data()
    drop_cols = ['id', 'PitNextLap']
    features = [col for col in train.columns if col not in drop_cols]
    cat_features = ['Driver', 'Compound', 'Race', 'tyre_life_compound', 'driver_race']
    
    X = train[features]
    y = train['PitNextLap']
    X_test = test[features]
    
    print(f"Features: {len(features)}")
    
    oof_lgb, test_lgb, score_lgb = train_lgb(X, y, X_test, cat_features)
    print(f"LGBM AUC: {score_lgb:.5f}")
    
    oof_cat, test_cat, score_cat = train_cat(X, y, X_test, cat_features)
    print(f"CatBoost AUC: {score_cat:.5f}")
    
    oof_xgb, test_xgb, score_xgb = train_xgb(X, y, X_test)
    print(f"XGBoost AUC: {score_xgb:.5f}")
    
    oof_hgb, test_hgb, score_hgb = train_hgb(X, y, X_test)
    print(f"HGB AUC: {score_hgb:.5f}")
    
    # Stacking
    oof_stack = np.column_stack([oof_lgb, oof_cat, oof_xgb, oof_hgb])
    test_stack = np.column_stack([test_lgb, test_cat, test_xgb, test_hgb])
    
    # Use Ridge for stacking meta-learner
    meta_model = LogisticRegression()
    meta_model.fit(oof_stack, y)
    
    test_preds = meta_model.predict_proba(test_stack)[:, 1]
    oof_preds_final = meta_model.predict_proba(oof_stack)[:, 1]
    
    score_stack = roc_auc_score(y, oof_preds_final)
    print(f"\nFinal Stacking AUC: {score_stack:.5f}")
    
    submission = pd.read_csv('../data/sample_submission.csv')
    submission['PitNextLap'] = test_preds
    submission.to_csv('submission_super_ensemble.csv', index=False)
    print("\nSubmission saved to submission_super_ensemble.csv")

if __name__ == "__main__":
    main()
