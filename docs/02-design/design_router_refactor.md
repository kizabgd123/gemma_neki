# Design Specification: ModelRouter & AnalysisAgent Refactoring

## 1. ModelRouter Fallback Mocking
- **Mechanism:** Use `unittest.mock` to patch the execution function and raise a `RuntimeError` or custom Exception simulating a 429 status code.
- **Verification:** Assert that the router iterates to the next model in `fallback_chain` upon receiving the simulated 429.

## 2. AnalysisAgent Exponential Backoff
- **Implementation:** Utilize a decorator-based approach for retries to keep the `execute` method clean.
- **Backoff Strategy:** Initial delay 1s, backoff factor 2, maximum retries 3.
- **Exception Handling:** Only retry on transient API errors (e.g., 429, 503, 504).
