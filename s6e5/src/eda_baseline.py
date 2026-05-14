import pandas as pd
import numpy as np
import lightgbm as lgb
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Loading Data
def load_data(data_dir='../data/'):
    train = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    test = pd.read_csv(os.path.join(data_dir, 'test.csv'))
    return train, test

# 2. Feature Engineering
def engineer_features(df):
    # Time-based features
    df['tyre_age_ratio'] = df['TyreLife'] / (df['LapNumber'] + 1)
    df['race_progress_sq'] = df['RaceProgress'] ** 2
    
    # Group-based features (Race, Year, Driver)
    df['pace_diff'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].diff().fillna(0)
    df['rolling_pace'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(3).mean()).fillna(0)
    
    # Cumulative features
    df['cum_deg_ratio'] = df['Cumulative_Degradation'] / (df['LapNumber'] + 1)
    
    # Categorical interaction (Simplified for baseline)
    df['driver_compound'] = df['Driver'] + "_" + df['Compound']
    
    return df

def preprocess(train, test):
    # Combine for encoding
    all_df = pd.concat([train, test], axis=0).reset_index(drop=True)
    
    # Feature engineering
    all_df = engineer_features(all_df)
    
    # Label encoding for categorical
    cat_features = ['Driver', 'Compound', 'Race', 'driver_compound']
    for col in cat_features:
        all_df[col] = pd.factorize(all_df[col])[0]
    
    # Split back
    train_processed = all_df[:len(train)].copy()
    test_processed = all_df[len(train):].copy()
    
    return train_processed, test_processed

# 3. Model Training
def train_model(X, y, X_test, cat_features, n_splits=5):
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'verbosity': -1,
        'boosting_type': 'gbdt',
        'random_state': 42,
        'learning_rate': 0.05,
        'num_leaves': 31,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5
    }

    for fold, (train_idx, val_idx) in enumerate(folds.split(X, y)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        dtrain = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features)
        dval = lgb.Dataset(X_val, label=y_val, reference=dtrain, categorical_feature=cat_features)
        
        model = lgb.train(
            params,
            dtrain,
            valid_sets=[dtrain, dval],
            num_boost_round=1000,
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=100)
            ]
        )
        
        oof_preds[val_idx] = model.predict(X_val, num_iteration=model.best_iteration)
        test_preds += model.predict(X_test, num_iteration=model.best_iteration) / n_splits
        
        print(f"Fold {fold+1} AUC: {roc_auc_score(y_val, oof_preds[val_idx]):.5f}")

    overall_auc = roc_auc_score(y, oof_preds)
    print(f"\nOverall OOF AUC: {overall_auc:.5f}")
    
    return oof_preds, test_preds, overall_auc

def main():
    print("--- Starting S6E5 Baseline ---")
    train, test = load_data('../data/')
    
    # Basic EDA stats
    print(f"Train columns: {train.columns.tolist()}")
    print(f"Target distribution: {train['PitNextLap'].value_counts(normalize=True)}")
    
    train_proc, test_processed = preprocess(train, test)
    
    drop_cols = ['id', 'PitNextLap']
    features = [col for col in train_proc.columns if col not in drop_cols]
    cat_features = ['Driver', 'Compound', 'Race', 'driver_compound']
    
    X = train_proc[features]
    y = train['PitNextLap']
    X_test = test_processed[features]
    
    oof, test_preds, score = train_model(X, y, X_test, cat_features)
    
    # Save submission
    submission = pd.read_csv('../data/sample_submission.csv')
    submission['PitNextLap'] = test_preds
    submission.to_csv('submission_baseline.csv', index=False)
    print("\nSubmission saved to submission_baseline.csv")
    
    # Save metrics
    with open('metrics.json', 'w') as f:
        json.dump({'oof_auc': score}, f)

if __name__ == "__main__":
    main()
