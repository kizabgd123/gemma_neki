# PDCA Plan: ModelRouter & AnalysisAgent Refactoring

## 1. Executive Summary
Refactoring the system to improve robustness. Specifically: 1) Verify fallback logic in `ModelRouter` upon 429 (Rate Limit) errors, and 2) Implement exponential backoff for `AnalysisAgent` LLM calls.

## 2. Problem Statement
- `ModelRouter` fallback behavior needs empirical verification under stress (429 errors).
- `AnalysisAgent` lacks automatic retries, leading to task failure on transient API errors.

## 3. Solution
- Create a unit test with mocking for `ModelRouter` to simulate 429 responses.
- Implement `tenacity` or custom exponential backoff logic in `AnalysisAgent`.

## 4. Value Delivered
| Problem | Solution | Function UX Effect | Core Value |
| :--- | :--- | :--- | :--- |
| Unverified fallback | Mock testing 429 | Resilient model routing | Reliability |
| Fragile LLM calls | Exponential backoff | Automated transient failure recovery | Robustness |

## 5. Phases
1. **ModelRouter Mock Test:** Create mock tests in `agents/test_model_router.py`.
2. **AnalysisAgent Retry:** Refactor `agents/analysis_agent.py` to add backoff logic.
3. **Verification:** Run tests to confirm fallback and retry mechanisms.

## 6. Acceptance Criteria
- [ ] ModelRouter fallback on 429 is verified via mock tests.
- [ ] AnalysisAgent successfully retries on transient errors with exponential backoff.
