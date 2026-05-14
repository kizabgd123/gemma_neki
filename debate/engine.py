# debate/engine.py

import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime

class DebateEngine:
    def __init__(self, memory_manager, logger):
        self.memory_manager = memory_manager
        self.logger = logger
        self.participants = {}
        self.debate_history = []

    def register_participant(self, role: str, agent_instance):
        self.participants[role] = agent_instance

    async def run_debate(self, workflow_id: str, request: str, trace_id: str):
        debate_id = f"deb_{trace_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.logger.log_debate_event("DEBATE_START", workflow_id, debate_id, {"request": request}, trace_id=trace_id)
        
        # Load similar past debates to influence weighting
        past_debates = self.memory_manager.get_similar_debates(request)
        
        arguments = []
        reasoning_trace = []
        
        # --- Round 1: Opening ---
        self.logger.info("Debate Round 1: Opening", extra={"trace_id": trace_id})
        analysis_context = await self._execute_step("Analyst", {"request": request}, trace_id, arguments, reasoning_trace)
        solution_proposal = await self._execute_step("Solution", {"request": request, "analysis": analysis_context}, trace_id, arguments, reasoning_trace)
        
        # --- Round 2: Challenge ---
        self.logger.info("Debate Round 2: Challenge", extra={"trace_id": trace_id})
        critique = await self._execute_step("Critic", {"request": request, "proposal": solution_proposal}, trace_id, arguments, reasoning_trace)
        security_audit = await self._execute_step("Security", {"request": request, "solution": solution_proposal}, trace_id, arguments, reasoning_trace)
        
        # --- Round 3: Mitigation (Iterative Loop) ---
        max_iterations = 2
        iteration = 0
        while iteration < max_iterations:
            high_risks = [r for r in security_audit.get("security_risks", []) if r.get("severity") == "HIGH"]
            major_flaws = [f for f in critique.get("logical_flaws", []) if critique.get("overall_confidence_score", 1.0) < 0.6]
            
            if not high_risks and not major_flaws:
                break
            
            iteration += 1
            self.logger.info(f"Debate Round 3: Mitigation Iteration {iteration}", extra={"trace_id": trace_id})
            
            feedback = {
                "security_feedback": security_audit,
                "critic_feedback": critique,
                "iteration": iteration
            }
            
            solution_proposal = await self._execute_step("Solution", {
                "request": request, 
                "analysis": analysis_context, 
                "feedback": feedback,
                "previous_proposal": solution_proposal
            }, trace_id, arguments, reasoning_trace)
            
            # Re-challenge
            critique = await self._execute_step("Critic", {"request": request, "proposal": solution_proposal}, trace_id, arguments, reasoning_trace)
            security_audit = await self._execute_step("Security", {"request": request, "solution": solution_proposal}, trace_id, arguments, reasoning_trace)

        # --- Round 4: Final Vote & Optimization ---
        self.logger.info("Debate Round 4: Final Vote & Optimization", extra={"trace_id": trace_id})
        optimization = await self._execute_step("Optimizer", {
            "request": request, 
            "solution": solution_proposal, 
            "critique": critique, 
            "security_audit": security_audit
        }, trace_id, arguments, reasoning_trace)

        # Collect Final Votes
        votes = {}
        for role in ["Analyst", "Solution", "Critic", "Security", "Optimizer"]:
            vote_data = await self._collect_vote(role, {
                "request": request,
                "final_solution": solution_proposal,
                "critique": critique,
                "security_audit": security_audit,
                "optimization": optimization
            }, trace_id)
            votes[role] = vote_data
            self.memory_manager.store_agent_opinion(role, workflow_id, vote_data.get("reason"), vote_data.get("vote"), vote_data.get("confidence"))

        # --- Round 5: Aggregation ---
        final_decision_data = self._aggregate_results_v2(votes, security_audit, critique)
        
        debate_result = {
            "debate_id": debate_id,
            "workflow_id": workflow_id,
            "structured_arguments": arguments,
            "final_proposal": solution_proposal,
            "votes": votes,
            "consensus_decision": final_decision_data["decision"],
            "confidence_score": final_decision_data["confidence"],
            "conflict_points": final_decision_data["conflicts"],
            "reasoning_trace": reasoning_trace,
            "iterations": iteration
        }
        
        # Store in memory
        self.memory_manager.store_debate_session(debate_id, workflow_id, status="CLOSED", final_consensus=json.dumps(debate_result))
        for arg in arguments:
            self.memory_manager.store_argument(debate_id, arg["agent"], json.dumps(arg["output"]), arg.get("confidence", 0.9))
        
        self.logger.log_debate_event("DEBATE_END", workflow_id, debate_id, debate_result, trace_id=trace_id)
        return debate_result

    async def _execute_step(self, role: str, context: dict, trace_id: str, arguments: list, trace: list):
        agent = self.participants.get(role)
        if not agent:
            self.logger.error(f"Required participant {role} missing for debate.")
            raise RuntimeError(f"Missing {role} Agent")
        
        agent.set_mode("DEBATE_MODE", trace_id=trace_id)
        output = await agent.execute(context, trace_id=trace_id)
        
        arguments.append({"agent": role, "output": output})
        trace.append({"step": len(trace) + 1, "agent": role, "action": f"{role} input provided"})
        return output

    async def _collect_vote(self, role: str, context: dict, trace_id: str) -> Dict[str, Any]:
        agent = self.participants.get(role)
        prompt = f"""
        Final Vote Round. Based on the debate, provide your structured VOTE.
        Request: {context['request']}
        Solution: {json.dumps(context['final_solution'])}
        Critique: {json.dumps(context['critique'])}
        Security: {json.dumps(context['security_audit'])}
        Optimization: {json.dumps(context['optimization'])}
        
        Provide output in JSON:
        {{
            "vote": "Approved" | "Rejected",
            "confidence": 0.0 - 1.0,
            "reason": "short explanation"
        }}
        """
        # We use a direct LLM call via the agent to get the vote
        # This is a bit of a shortcut, ideally agents have a .vote() method
        try:
            # We wrap it in a pseudo-context to trigger the JSON parsing
            raw_vote = await agent.model_router.execute_with_routing(
                agent._llm_call_wrapper,
                prompt=prompt,
                context_type="debate"
            )
            return agent.parse_json_robust(raw_vote)
        except Exception as e:
            self.logger.error(f"Agent {role} failed to vote: {str(e)}")
            return {"vote": "Rejected", "confidence": 0.0, "reason": f"Voting failure: {str(e)}"}

    def _aggregate_results_v2(self, votes, security_audit, critique):
        conflicts = []
        
        # 1. Veto Check
        # Security Veto
        high_risks = [r for r in security_audit.get("security_risks", []) if r.get("severity") == "HIGH"]
        if high_risks and votes["Security"]["vote"] == "Rejected" and votes["Security"]["confidence"] == 1.0:
            return {
                "decision": "REJECTED: Security Veto (High severity risks detected with absolute confidence)",
                "confidence": 1.0,
                "conflicts": [f"Security Veto: {r['risk']}" for r in high_risks]
            }
        
        # Critic Veto
        if critique.get("overall_confidence_score", 1.0) < 0.2 and votes["Critic"]["vote"] == "Rejected" and votes["Critic"]["confidence"] == 1.0:
             return {
                "decision": "REJECTED: Critic Veto (Fundamental logic flaws detected with absolute confidence)",
                "confidence": 1.0,
                "conflicts": ["Critic Veto: Absolute lack of confidence in solution logic"]
            }

        # 2. Weighted Voting
        total_weight = 0
        weighted_score = 0
        
        for role, vote_data in votes.items():
            reliability = self.memory_manager.get_agent_reliability(role)
            weight = reliability * vote_data.get("confidence", 0.5)
            
            vote_val = 1 if vote_data.get("vote") == "Approved" else 0
            weighted_score += vote_val * weight
            total_weight += weight
            
            if vote_data.get("vote") == "Rejected":
                conflicts.append(f"{role} rejected: {vote_data.get('reason')}")

        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        if final_score > 0.7:
            decision = "APPROVED: Strong consensus reached."
        elif final_score > 0.4:
            decision = "CONDITIONALLY APPROVED: Moderate consensus, address conflicts."
        else:
            decision = "REJECTED: Majority of weighted opinions are negative."
            
        return {
            "decision": decision,
            "confidence": final_score,
            "conflicts": conflicts
        }
