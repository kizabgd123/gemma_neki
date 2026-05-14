---
id: e5f6g7h8
title: "High-Performance Ensemble Training"
status: Todo
priority: High
order: 20
created: 2026-05-13
updated: 2026-05-13
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Build a model that achieves ROC AUC >= 0.95200 on the Public Leaderboard.

## Solution
Train an ensemble of GBDT models (LightGBM, XGBoost, CatBoost) using StratifiedKFold cross-validation. Use Optuna for hyperparameter tuning. Implement a stacking or weighted blending strategy.

## Implementation Details
- Implement training loop for LGBM, XGB, and CatBoost.
- Optimize hyperparameters using Optuna.
- Create a stacking ensemble.
- Validate performance using OOF (Out-Of-Fold) scores.
