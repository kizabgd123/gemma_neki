import pandas as pd
import numpy as np
import lightgbm as lgb
from catboost import CatBoostClassifier, Pool
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder
import os
import gc
import json

def load_data(data_dir='../data/'):
    train = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    test = pd.read_csv(os.path.join(data_dir, 'test.csv'))
    return train, test

def target_encode(train, test, columns, target, n_splits=5):
    train_encoded = train.copy()
    test_encoded = test.copy()
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    for col in columns:
        col_name = f"{col}_te"
        train_encoded[col_name] = 0
        for train_idx, val_idx in kf.split(train, train[target]):
            means = train.iloc[train_idx].groupby(col)[target].mean()
            train_encoded.loc[val_idx, col_name] = train_encoded.loc[val_idx, col].map(means)
        test_encoded[col_name] = test_encoded[col].map(train.groupby(col)[target].mean())
        global_mean = train[target].mean()
        train_encoded[col_name] = train_encoded[col_name].fillna(global_mean)
        test_encoded[col_name] = test_encoded[col_name].fillna(global_mean)
    return train_encoded, test_encoded

def engineer_features(df):
    # Time and Tyre
    df['tyre_age_ratio'] = df['TyreLife'] / (df['LapNumber'] + 1)
    df['race_progress_sq'] = df['RaceProgress'] ** 2
    df['lap_stint_ratio'] = df['LapNumber'] / (df['Stint'] + 1)
    
    # Pace Analysis
    df['pace_diff'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].diff().fillna(0)
    df['pace_trend_3'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(3).mean()).fillna(0)
    df['pace_trend_5'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(5).mean()).fillna(0)
    
    # Degradation
    df['cum_deg_ratio'] = df['Cumulative_Degradation'] / (df['LapNumber'] + 1)
    df['deg_per_lap'] = df.groupby(['Race', 'Year', 'Driver', 'Stint'])['Cumulative_Degradation'].diff().fillna(0)
    
    # Contextual Stats
    df['driver_avg_laptime'] = df.groupby(['Driver', 'Race'])['LapTime (s)'].transform('mean')
    df['driver_std_laptime'] = df.groupby(['Driver', 'Race'])['LapTime (s)'].transform('std')
    df['laptime_norm'] = (df['LapTime (s)'] - df['driver_avg_laptime']) / (df['driver_std_laptime'] + 1e-6)
    
    # Stint dynamics
    df['stint_lap_count'] = df.groupby(['Race', 'Year', 'Driver', 'Stint']).cumcount()
    
    # Interactions
    df['tyre_life_compound'] = df['TyreLife'].astype(str) + "_" + df['Compound']
    df['driver_race'] = df['Driver'] + "_" + df['Race']
    df['compound_race'] = df['Compound'] + "_" + df['Race']
    
    return df

def run_god_mode():
    print("--- God-Mode: AI Workflow Orchestrator S6E5 ---")
    train, test = load_data('../data/')
    
    train_proc = engineer_features(train)
    test_proc = engineer_features(test)
    
    te_cols = ['Driver', 'Compound', 'Race', 'tyre_life_compound', 'driver_race', 'compound_race']
    train_proc, test_proc = target_encode(train_proc, test_proc, te_cols, 'PitNextLap')
    
    all_df = pd.concat([train_proc, test_proc], axis=0).reset_index(drop=True)
    le = LabelEncoder()
    for col in te_cols:
        all_df[col] = le.fit_transform(all_df[col].astype(str))
        
    X = all_df[:len(train)].drop(['id', 'PitNextLap'], axis=1)
    y = train['PitNextLap']
    X_test = all_df[len(train):].drop(['id', 'PitNextLap'], axis=1)
    
    # Use GroupKFold by (Race, Year) for better generalization
    groups = train['Race'] + "_" + train['Year'].astype(str)
    gkf = GroupKFold(n_splits=5)
    
    oof_cat = np.zeros(len(X))
    test_cat = np.zeros(len(X_test))
    
    print("\nTraining God-Mode CatBoost...")
    cat_params = {
        'iterations': 3000,
        'learning_rate': 0.03,
        'depth': 7,
        'l2_leaf_reg': 10,
        'bootstrap_type': 'Bernoulli',
        'subsample': 0.8,
        'eval_metric': 'AUC',
        'random_seed': 42,
        'verbose': 500,
        'early_stopping_rounds': 100
    }
    
    for fold, (ti, vi) in enumerate(gkf.split(X, y, groups=groups)):
        X_train, X_val = X.iloc[ti], X.iloc[vi]
        y_train, y_val = y.iloc[ti], y.iloc[vi]
        
        model = CatBoostClassifier(**cat_params)
        model.fit(X_train, y_train, eval_set=(X_val, y_val))
        
        oof_cat[vi] = model.predict_proba(X_val)[:, 1]
        test_cat += model.predict_proba(X_test)[:, 1] / 5
        print(f"Fold {fold+1} AUC: {roc_auc_score(y_val, oof_cat[vi]):.5f}")
        
    final_score = roc_auc_score(y, oof_cat)
    print(f"\nGod-Mode OOF AUC: {final_score:.5f}")
    
    # Save artifacts
    submission = pd.read_csv('../data/sample_submission.csv')
    submission['PitNextLap'] = test_cat
    submission.to_csv('submission_god_mode.csv', index=False)
    
    with open('god_mode_metrics.json', 'w') as f:
        json.dump({'oof_auc': final_score}, f)
    
    print("God-Mode artifacts saved.")

if __name__ == "__main__":
    run_god_mode()
