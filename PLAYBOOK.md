# Playbook: Kaggle S6E5 Leaderboard Dominance

## 1. System Audit & Initial State
- **Architecture**: AI Workflow Orchestrator with Memory (SQLite) and Multi-Agent Debate.
- **Initial Goal**: Reach Public LB >= 0.95200 in S6E5 (F1 Pit Stop Prediction).
- **Audit Findings**:
    - Project has robust agentic foundations (`AnalysisAgent`, `CriticAgent`).
    - Memory system tracks past experiments and successful plans.
    - TTS (Piper) implemented for audible reasoning traces.

## 2. Competition Analysis (S6E5)
- **Problem Type**: Binary Classification (PitNextLap).
- **Metric**: ROC AUC.
- **Data Characteristics**: 
    - Temporal (Laps, Tyre Life).
    - Grouped (Race, Year, Driver).
    - Imbalanced (target 1.0 ~20%).

## 3. Feature Engineering Evolution
### Phase 1: Baseline
- Features: `tyre_age_ratio`, `race_progress_sq`, rolling lap times.
- Result: OOF AUC ~0.9398.

### Phase 2: Advanced FE v2 (God Mode)
- **Target Encoding**: OOF-smoothed encoding for `Driver`, `Compound`, `Race`.
- **Interactions**: `tyre_life_compound`, `driver_race`.
- **Normalization**: LapTime normalization per driver/race.
- **Lagged Features**: `prev_laptime`, `prev_pitstop`.
- Result: OOF AUC ~0.9551.

## 4. Model Experiments
| Model | OOF AUC | Notes |
|-------|---------|-------|
| LightGBM | 0.9423 | Fast, strong baseline. |
| CatBoost | 0.9551 | Best single model, handles categorical interactions well. |
| XGBoost | 0.9485 | Robust performance. |
| HGB | 0.9405 | Good diversity for ensemble. |

## 5. Ensemble Strategy
- **Approach**: Stacking (Level 0: LGBM, Cat, XGB, HGB -> Level 1: Logistic Regression).
- **Consensus**: Consensus reached through multi-agent debate (Optimizer recommended adding HGB and tuning meta-learner).
- **Public LB Score**: 0.94722 (Verified).

## 6. Production Handoff
- Final notebook pushed to Kaggle with full audit logs and reproducible pipeline.
- Integration test `gemini-run.py` confirmed system stability.
