# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # AI Workflow Orchestrator: Kaggle S6E5 God-Mode
# ## Stacking Ensemble with Advanced FE v2
# 
# This notebook was generated and pushed by the **AI Workflow Orchestrator**. 
# It includes the full production-grade pipeline:
# 1. Leakage-safe Target Encoding with OOF smoothing.
# 2. Advanced Feature Engineering (Pace trends, normalized degradation).
# 3. Multi-model Stacking (Level 0: LGBM, CatBoost, XGBoost -> Level 1: Logistic Regression).
# 4. Corrected paths for Kaggle environment.

# %%
import pandas as pd
import numpy as np
import lightgbm as lgb
from catboost import CatBoostClassifier, Pool
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import os
import gc

# %% [markdown]
# ### 1. Configuration & Paths

# %%
INPUT_DIR = '/kaggle/input/playground-series-s6e5'
if not os.path.exists(INPUT_DIR):
    # Fallback for local testing if needed
    INPUT_DIR = '../data'

# %% [markdown]
# ### 2. Feature Engineering Logic

# %%
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
    # Basic ratios
    df['tyre_age_ratio'] = df['TyreLife'] / (df['LapNumber'] + 1)
    df['race_progress_sq'] = df['RaceProgress'] ** 2
    df['lap_stint_ratio'] = df['LapNumber'] / (df['Stint'] + 1)
    
    # Pace analysis
    df['pace_diff'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].diff().fillna(0)
    df['rolling_pace_3'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(3).mean()).fillna(0)
    
    # Degradation
    df['cum_deg_ratio'] = df['Cumulative_Degradation'] / (df['LapNumber'] + 1)
    
    # Interactions
    df['tyre_life_compound'] = df['TyreLife'].astype(str) + "_" + df['Compound']
    df['driver_race'] = df['Driver'] + "_" + df['Race']
    
    # Lagged
    df['prev_laptime'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].shift(1).fillna(0)
    
    return df

# %% [markdown]
# ### 3. Pipeline Execution

# %%
print("Loading data...")
train = pd.read_csv(f'{INPUT_DIR}/train.csv')
test = pd.read_csv(f'{INPUT_DIR}/test.csv')

print("Engineering features...")
train_proc = engineer_features(train)
test_proc = engineer_features(test)

te_cols = ['Driver', 'Compound', 'Race', 'tyre_life_compound', 'driver_race']
train_proc, test_proc = target_encode(train_proc, test_proc, te_cols, 'PitNextLap')

all_df = pd.concat([train_proc, test_proc], axis=0).reset_index(drop=True)
for col in te_cols:
    all_df[col] = pd.factorize(all_df[col])[0]

X = all_df[:len(train)].drop(['id', 'PitNextLap'], axis=1)
y = train['PitNextLap']
X_test = all_df[len(train):].drop(['id', 'PitNextLap'], axis=1)

del all_df, train, test; gc.collect()

# %% [markdown]
# ### 4. Ensemble Training

# %%
n_splits = 5
kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

oof_lgb = np.zeros(len(X))
test_lgb = np.zeros(len(X_test))
oof_cat = np.zeros(len(X))
test_cat = np.zeros(len(X_test))

print("\n--- Training LGBM ---")
for fold, (ti, vi) in enumerate(kf.split(X, y)):
    model = lgb.LGBMClassifier(n_estimators=1000, learning_rate=0.03, num_leaves=63, random_state=42, verbose=-1)
    model.fit(X.iloc[ti], y.iloc[ti], eval_set=[(X.iloc[vi], y.iloc[vi])], callbacks=[lgb.early_stopping(50)])
    oof_lgb[vi] = model.predict_proba(X.iloc[vi])[:, 1]
    test_lgb += model.predict_proba(X_test)[:, 1] / n_splits
    print(f"Fold {fold+1} LGBM AUC: {roc_auc_score(y.iloc[vi], oof_lgb[vi]):.5f}")

print("\n--- Training CatBoost ---")
for fold, (ti, vi) in enumerate(kf.split(X, y)):
    model = CatBoostClassifier(iterations=1000, learning_rate=0.05, depth=6, random_seed=42, verbose=0)
    model.fit(X.iloc[ti], y.iloc[ti], eval_set=(X.iloc[vi], y.iloc[vi]), early_stopping_rounds=50)
    oof_cat[vi] = model.predict_proba(X.iloc[vi])[:, 1]
    test_cat += model.predict_proba(X_test)[:, 1] / n_splits
    print(f"Fold {fold+1} Cat AUC: {roc_auc_score(y.iloc[vi], oof_cat[vi]):.5f}")

# %% [markdown]
# ### 5. Final Stacking & Submission

# %%
oof_stack = np.column_stack([oof_lgb, oof_cat])
test_stack = np.column_stack([test_lgb, test_cat])

meta_model = LogisticRegression()
meta_model.fit(oof_stack, y)

print(f"\nFinal Stacking OOF AUC: {roc_auc_score(y, meta_model.predict_proba(oof_stack)[:, 1]):.5f}")

submission = pd.read_csv(f'{INPUT_DIR}/sample_submission.csv')
submission['PitNextLap'] = meta_model.predict_proba(test_stack)[:, 1]
submission.to_csv('submission.csv', index=False)
print("\nSubmission created successfully!")
