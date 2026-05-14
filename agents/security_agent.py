from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os

class SecurityAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="SecurityAgent", 
            description="Evaluates security risks, data privacy, and compliance.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        solution = context.get("solution")
        request = context.get("request")
        
        self.log_action(trace_id, "start_security_audit", {"request": request, "debate_mode": self.debate_mode})
        
        prompt = self._construct_prompt(request, solution)
        
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            result = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "security_execution_failed", {"error": str(e)})
            raise
        
        self.log_action(trace_id, "security_audit_completed", result)
        return result

    def _construct_prompt(self, request: str, solution: dict) -> str:
        return f"""
        Task: Perform a security audit on the following proposed solution.
        Identify potential vulnerabilities, data leakage risks, and permission issues.
        
        Request: {request}
        Proposed Solution: {json.dumps(solution)}
        
        Strictly adhere to the following JSON schema for the output:
        {{
          "security_risks": [
            {{
              "risk": "string",
              "severity": "LOW | MEDIUM | HIGH",
              "mitigation": "string"
            }}
          ],
          "compliance_issues": ["string"],
          "is_secure": "boolean"
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
