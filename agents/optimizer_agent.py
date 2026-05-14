from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os

class OptimizerAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="OptimizerAgent", 
            description="Identifies performance improvements and alternative paths.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        solution = context.get("solution")
        critique = context.get("critique")
        security_audit = context.get("security_audit")
        request = context.get("request")
        
        self.log_action(trace_id, "start_optimization", {"request": request, "debate_mode": self.debate_mode})
        
        prompt = self._construct_prompt(request, solution, critique, security_audit)
        
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            result = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "optimization_execution_failed", {"error": str(e)})
            raise
        
        self.log_action(trace_id, "optimization_completed", result)
        return result

    def _construct_prompt(self, request: str, solution: dict, critique: dict, security_audit: dict) -> str:
        return f"""
        Task: Propose optimizations and alternative paths for the solution, considering the critique and security audit.
        
        Request: {request}
        Solution: {json.dumps(solution)}
        Critique: {json.dumps(critique)}
        Security Audit: {json.dumps(security_audit)}
        
        Strictly adhere to the following JSON schema for the output:
        {{
          "optimizations": [
            {{
              "area": "PERFORMANCE | READABILITY | SCALABILITY",
              "suggestion": "string",
              "impact": "string"
            }}
          ],
          "alternative_solutions": ["string"],
          "final_recommendation_adjustment": "string"
        }}
        """

    async def _llm_call_wrapper(self, model: str, prompt: str):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")

        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config={"response_mime_type": "application/json"}
        )
        response = await model_instance.generate_content_async(prompt)
        return response.text
