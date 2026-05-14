import pandas as pd
import numpy as np
import os
from sklearn.model_selection import StratifiedKFold

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
        # OOF encoding for train
        train_encoded[col_name] = 0
        for train_idx, val_idx in kf.split(train, train[target]):
            # Use only train_idx to calculate means for val_idx
            means = train.iloc[train_idx].groupby(col)[target].mean()
            train_encoded.loc[val_idx, col_name] = train_encoded.loc[val_idx, col].map(means)
        
        # Mean encoding for test
        test_encoded[col_name] = test_encoded[col].map(train.groupby(col)[target].mean())
        
        # Fill NaNs with global mean
        global_mean = train[target].mean()
        train_encoded[col_name] = train_encoded[col_name].fillna(global_mean)
        test_encoded[col_name] = test_encoded[col_name].fillna(global_mean)
        
    return train_encoded, test_encoded

def engineer_features(df):
    # Time-based features
    df['tyre_age_ratio'] = df['TyreLife'] / (df['LapNumber'] + 1)
    df['race_progress_sq'] = df['RaceProgress'] ** 2
    df['lap_stint_ratio'] = df['LapNumber'] / (df['Stint'] + 1)
    
    # Pace and Performance
    df['pace_diff'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].diff().fillna(0)
    df['rolling_pace_3'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(3).mean()).fillna(0)
    df['rolling_pace_5'] = df.groupby(['Race', 'Year', 'Driver'])['pace_diff'].transform(lambda x: x.rolling(5).mean()).fillna(0)
    
    # Cumulative degradation normalized by lap
    df['cum_deg_ratio'] = df['Cumulative_Degradation'] / (df['LapNumber'] + 1)
    
    # Interaction Features
    df['tyre_life_compound'] = df['TyreLife'].astype(str) + "_" + df['Compound']
    df['driver_race'] = df['Driver'] + "_" + df['Race']
    
    # Statistical features per Driver/Race
    df['driver_avg_laptime'] = df.groupby(['Driver', 'Race'])['LapTime (s)'].transform('mean')
    df['driver_std_laptime'] = df.groupby(['Driver', 'Race'])['LapTime (s)'].transform('std')
    df['laptime_norm'] = (df['LapTime (s)'] - df['driver_avg_laptime']) / (df['driver_std_laptime'] + 1e-6)
    
    # Delta Features
    df['pos_change_ratio'] = df['Position_Change'] / (df['Position'] + 1)
    
    # Lagged features
    df['prev_laptime'] = df.groupby(['Race', 'Year', 'Driver'])['LapTime (s)'].shift(1).fillna(0)
    df['prev_pitstop'] = df.groupby(['Race', 'Year', 'Driver'])['PitStop'].shift(1).fillna(0)
    
    return df

def apply_fe(train, test):
    # Initial engineering
    train_proc = engineer_features(train)
    test_proc = engineer_features(test)
    
    # Target encoding
    te_cols = ['Driver', 'Compound', 'Race', 'tyre_life_compound', 'driver_race']
    train_proc, test_proc = target_encode(train_proc, test_proc, te_cols, 'PitNextLap')
    
    # Combine for categorical label encoding
    all_df = pd.concat([train_proc, test_proc], axis=0).reset_index(drop=True)
    cat_features = ['Driver', 'Compound', 'Race', 'tyre_life_compound', 'driver_race']
    for col in cat_features:
        all_df[col] = pd.factorize(all_df[col])[0]
        
    # Split back
    train_final = all_df[:len(train)].copy()
    test_final = all_df[len(train):].copy()
    
    return train_final, test_final, cat_features

if __name__ == "__main__":
    train, test = load_data('../data/')
    train_proc, test_proc, cat_features = apply_fe(train, test)
    print(f"Features created. New shape: {train_proc.shape}")
    train_proc.to_parquet('train_fe_v2.parquet', index=False)
    test_proc.to_parquet('test_fe_v2.parquet', index=False)
    print("Saved FE v2 data to parquet.")
