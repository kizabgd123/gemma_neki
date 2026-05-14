from agents.base_agent import BaseAgent
import json
import google.generativeai as genai
import os
from typing import Any, Dict, List, Optional

class CriticAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None, debate_mode: bool = False):
        super().__init__(
            name="CriticAgent", 
            description="Challenges solutions and identifies edge cases.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger,
            debate_mode=debate_mode
        )

    async def execute(self, context: dict, trace_id: str):
        """
        In debate mode, the execute method uses the LLM to provide a structured critique.
        """
        proposal = context.get("proposal")
        criteria = context.get("criteria", {})
        
        self.log_action(trace_id, "start_critique", {"proposal": proposal, "debate_mode": self.debate_mode})
        
        if not self.debate_mode:
            # Fallback to legacy verification logic if not in debate mode
            return self.verify(str(proposal), criteria)

        prompt = self._construct_debate_prompt(proposal, criteria)
        
        try:
            raw_response = await self.model_router.execute_with_routing(
                self._llm_call_wrapper,
                prompt=prompt,
                context_type="standard"
            )
            critique = self.parse_json_robust(raw_response)
        except Exception as e:
            self.log_action(trace_id, "critique_execution_failed", {"error": str(e)})
            raise
            
        self.log_action(trace_id, "critique_generated", critique)
        return critique

    def verify(self, output: str, criteria: dict) -> dict:
        """Legacy verification logic."""
        # Simplified verification logic: 
        # Check if output contains required keywords from criteria
        confidence = 0.0
        if "action_items" in output:
            confidence += 0.5
        if "date" in output:
            confidence += 0.4
        
        # Artificial limit to test re-dispatch (rework)
        status = "success" if confidence >= 0.9 else "fail"
        return {"confidence": confidence, "status": status, "summary": f"Verification {status}"}

    def _construct_debate_prompt(self, proposal: Any, criteria: dict) -> str:
        criteria_str = json.dumps(criteria)
        return f"""
        Task: Provide a structured critique of the following proposal.
        Identify logical flaws, missing edge cases, and potential security concerns.
        
        Proposal: {json.dumps(proposal)}
        
        Specific Criteria to check:
        {criteria_str}
        
        Strictly adhere to the following JSON schema for the output:
        {{
          "logical_flaws": ["string"],
          "missing_edge_cases": ["string"],
          "security_concerns": ["string"],
          "improvement_suggestions": ["string"],
          "overall_confidence_score": "float (0.0 to 1.0)"
        }}
        """

    async def _llm_call_wrapper(self, model: str, prompt: str):
        """SDK integration."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")

        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config={"response_mime_type": "application/json"}
        )

        import asyncio
        response = await model_instance.generate_content_async(prompt)
        return response.text
