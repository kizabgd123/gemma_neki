import os
import json
import time
import asyncio
from observability.logger import audit_logger

class ModelAvailabilityService:
    def __init__(self, config_path="settings.json"):
        self.base_dir = "/home/kizabgd/.gemini/antigravity/brain/memoriJADA"
        self.config_path = os.path.join(self.base_dir, config_path)
        # Default fallback chain as described (Flash-Lite -> Flash -> Pro -> Mistral)
        self.fallback_chain = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "mistral-large-latest"]
        self.failed_models = {}  # model_name: timestamp of failure
        self.cooldown_period = 300  # 5 minutes
        self.max_retries = 2

    def resolve_model(self, override_model: str = None) -> str:
        """Determines the model to use based on precedence."""
        if override_model:
            return override_model
            
        env_model = os.getenv("GEMINI_MODEL")
        if env_model:
            return env_model
            
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get("model", {}).get("name", "auto")
            except (json.JSONDecodeError, KeyError, IOError):
                pass
                
        return "auto"

    def _is_healthy(self, model: str) -> bool:
        if model not in self.failed_models:
            return True
        
        last_failure = self.failed_models[model]
        if time.time() - last_failure > self.cooldown_period:
            # Cooldown expired, try again
            return True
        return False

    def _call_mistral(self, prompt, **kwargs):
        """Production implementation using Mistral AI SDK."""
        from mistralai.client import Mistral
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY is not set.")
        
        client = Mistral(api_key=api_key)
        
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def execute_with_routing(self, func, context_type="standard", **kwargs):
        """Handles model execution with automatic fallback, retries, and routing policy."""
        requested_model = self.resolve_model(kwargs.get("model"))
        
        # Build the effective fallback list for this call
        if requested_model == "auto" or context_type == "utility":
            chain = self.fallback_chain
        else:
            # Put requested model first, then the rest of the chain
            chain = [requested_model] + [m for m in self.fallback_chain if m != requested_model]

        last_error = None
        for model in chain:
            if not self._is_healthy(model):
                continue
            
            for attempt in range(self.max_retries + 1):
                try:
                    kwargs['model'] = model
                    if model == "mistral-large-latest":
                        # Mistral call is currently sync, but we treat it as part of async routing
                        return self._call_mistral(kwargs.get('prompt', ''))
                    
                    return await func(**kwargs)
                except Exception as e:
                    last_error = e
                    is_transient = "rate limit" in str(e).lower() or "timeout" in str(e).lower()
                    
                    audit_logger.log_execution("SYSTEM", "ModelRouter", "model_attempt_failed", 
                                             {"model": model, "attempt": attempt + 1, "error": str(e), "is_transient": is_transient})
                    
                    if is_transient and attempt < self.max_retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    # Mark model as failed for a while
                    self.failed_models[model] = time.time()
                    break # Move to next model in chain

        raise RuntimeError(f"Model routing failed. Last error: {str(last_error)}")
