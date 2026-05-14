# Design Specification: MistralAI Fallback Integration

## 1. ModelAvailabilityService Changes
- **New Dependency:** `mistralai` SDK.
- **Fallback Chain Update:** `self.fallback_chain` now includes `["mistral-large-latest"]` as the ultimate fallback.
- **Execution Logic:** 
    - The `execute_with_routing` method will catch exceptions.
    - If no Gemini models succeed, it attempts a call to `MistralClient` (if `MISTRAL_API_KEY` is present).

## 2. Mistral Client Integration
- Implement `_mistral_llm_call_wrapper` to match the required LLM call interface for the router.
- Use the `MistralClient` SDK (async `chat` method).

## 3. Configuration & Security
- **API Key:** Must be set as `MISTRAL_API_KEY` in the environment.
- **Error Handling:** Ensure 429/503 errors from Mistral are handled and logged.
