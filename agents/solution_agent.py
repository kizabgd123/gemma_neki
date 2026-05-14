from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os

class SolutionAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="SolutionAgent", 
            description="Proposes optimal implementation strategies.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        proposal = context.get("analysis", {}).get("proposal")
        request = context.get("request")
        feedback = context.get("feedback")
        previous_proposal = context.get("previous_proposal")
        
        self.log_action(trace_id, "start_solution_proposal", {
            "request": request, 
            "debate_mode": self.debate_mode,
            "has_feedback": feedback is not None
        })
        
        prompt = self._construct_prompt(request, proposal, feedback, previous_proposal)
        
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            result = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "solution_execution_failed", {"error": str(e)})
            raise
        
        self.log_action(trace_id, "solution_proposed", result)
        return result

    def _construct_prompt(self, request: str, analysis_proposal: str, feedback: dict = None, previous_proposal: dict = None) -> str:
        base_prompt = f"""
        Task: Propose a detailed solution for the following request.
        Focus on efficiency, technical feasibility, and implementation details.
        
        Request: {request}
        Initial Analysis: {analysis_proposal}
        """

        if feedback:
            base_prompt += f"""
            --- FEEDBACK FROM PREVIOUS ROUND ---
            Previous Proposal: {json.dumps(previous_proposal)}
            Security Issues: {json.dumps(feedback.get('security_feedback'))}
            Criticism: {json.dumps(feedback.get('critic_feedback'))}
            Iteration: {feedback.get('iteration')}
            
            Please revise the solution to address the identified security risks and logical flaws.
            """

        base_prompt += """
        Strictly adhere to the following JSON schema for the output:
        {
          "solution": "string",
          "implementation_steps": ["string"],
          "technical_stack": ["string"],
          "estimated_effort": "string",
          "mitigation_plan": "string (optional, explain how you addressed feedback)"
        }
        """
        return base_prompt

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
