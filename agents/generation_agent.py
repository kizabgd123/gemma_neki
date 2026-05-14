from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os

class GenerationAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="GenerationAgent", 
            description="Generates final outputs, reports, and code blocks.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        decision = context.get("decision")
        request = context.get("request")
        
        self.log_action(trace_id, "start_generation", {"request": request, "debate_mode": self.debate_mode})
        
        prompt = self._construct_prompt(request, decision)
        
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            # Generation agent might return structured or unstructured data depending on need
            # Here we assume a JSON response describing the generated artifacts
            result = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "generation_execution_failed", {"error": str(e)})
            raise
        
        self.log_action(trace_id, "generation_completed", result)
        return result

    def _construct_prompt(self, request: str, decision: dict) -> str:
        return f"""
        Task: Based on the final decision, generate the required outputs for the user request.
        
        Request: {request}
        Final Decision: {json.dumps(decision)}
        
        Output should be a JSON object containing the generated content:
        {{
          "artifacts": [
            {{
              "name": "string",
              "type": "CODE | DOCUMENTATION | DATA",
              "content": "string"
            }}
          ],
          "summary": "string"
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
