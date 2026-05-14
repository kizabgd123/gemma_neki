from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os
import asyncio

class AnalysisAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="AnalysisAgent", 
            description="Generates problem structure and identifies risks.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        request = context.get("request")
        action_name = "start_debate_analysis" if self.debate_mode else "start_analysis"
        self.log_action(trace_id, action_name, {"request": request, "debate_mode": self.debate_mode})
        
        # Retrieve similar workflows to learn from past decompositions
        history = self.get_relevant_history(request)
        
        # Retrieve previously successful plans to inform the current decomposition
        best_plans = self.memory_manager.get_best_plans(request)
        prompt = self._construct_prompt(request, history, best_plans)
        
        # Use the model router to execute the LLM call with resilient fallback
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            result = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "analysis_execution_failed", {"error": str(e)})
            raise
        
        result_name = "proposal_generated" if self.debate_mode else "plan_generated"
        self.log_action(trace_id, result_name, result)
        return result

    def _construct_prompt(self, request: str, history: list, best_plans: list) -> str:
        """Constructs a prompt for the LLM based on user request and past memory."""
        history_context = "\n".join([str(h) for h in history])
        plans_context = "\n".join([json.dumps(p) for p in best_plans])
        
        if self.debate_mode:
            return f"""
            Task: Generate a critique-able proposal for the following request.
            Focus on identifying risks, assumptions, and potential alternative paths.
            Strictly adhere to the following JSON schema for the output:
            {{
              "proposal": "string",
              "assumptions": ["string"],
              "potential_risks": ["string"],
              "alternative_approaches": ["string"]
            }}

            Request: {request}
            
            Reference History:
            {history_context}

            Successfully Executed Past Plans for similar tasks:
            {plans_context}
            """
        
        return f"""
        Task: Decompose the following request into a swarming agent execution plan (DAG).
        Strictly adhere to the following JSON schema for the output:
        {{
          "tasks": [
            {{
              "id": "integer",
              "agent": "CodingAgent | CLIAgent | ValidationAgent",
              "description": "string",
              "depends_on": "list of integers",
              "params": "object"
            }}
          ],
          "risks": ["string"]
        }}

        Request: {request}
        
        Reference History:
        {history_context}

        Successfully Executed Past Plans for similar tasks:
        {plans_context}
        """

    async def _llm_call_wrapper(self, model: str, prompt: str):
        """
        Actual SDK integration using Google Generative AI with exponential backoff.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")

        genai.configure(api_key=api_key)

        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config={"response_mime_type": "application/json"}
        )

        max_retries = 3  # Maximum number of retry attempts
        backoff_factor = 2
        delay = 1  # Initial delay in seconds

        for attempt in range(max_retries + 1):
            try:
                response = await model_instance.generate_content_async(prompt)
                return response.text
            except Exception as e:
                # Check for transient errors (429, 503, 504)
                is_transient = any(err_code in str(e) for err_code in ["429", "503", "504"])
                
                if is_transient and attempt < max_retries:
                    self.logger.warning(
                        f"Transient error on {model}: {e}. "
                        f"Retrying in {delay}s (Attempt {attempt + 1}/{max_retries})..."
                    )
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
                else:
                    # Log failure and re-raise to allow ModelRouter to trigger fallback
                    self.logger.error(f"LLM call failed for {model} after {attempt} retries: {e}")
                    raise e