import uuid
import asyncio
from typing import Dict, Any, List
from datetime import datetime

from agents.analysis_agent import AnalysisAgent
from agents.solution_agent import SolutionAgent
from agents.critic_agent import CriticAgent
from agents.security_agent import SecurityAgent
from agents.optimizer_agent import OptimizerAgent
from agents.generation_agent import GenerationAgent
from agents.coding_agent import CodingAgent
from agents.cli_agent import CLIAgent
from agents.validation_agent import ValidationAgent
from agents.model_router import ModelAvailabilityService
from memory.manager import MemoryManager
from debate.engine import DebateEngine
from execution.engine import ExecutionEngine
from observability.logger import OrchestratorLogger

class AIWorkflowOrchestrator:
    def __init__(self, db_path="storage/memory.db", log_file="observability/orchestrator.log"):
        self.logger = OrchestratorLogger(log_file)
        self.memory_manager = MemoryManager(db_path, self.logger)
        self.model_router = ModelAvailabilityService()
        self.debate_engine = DebateEngine(self.memory_manager, self.logger)
        self.execution_engine = ExecutionEngine(self.memory_manager)
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Register agents in execution engine
        self.execution_engine.register_agents({
            "CodingAgent": self.agents["coding"],
            "CLIAgent": self.agents["cli"],
            "ValidationAgent": self.agents["validation"],
            "GenerationAgent": self.agents["generation"],
            "AnalysisAgent": self.agents["analysis"]
        })
        
        # Register debate participants
        self.debate_engine.register_participant("Analyst", self.agents["analysis"])
        self.debate_engine.register_participant("Solution", self.agents["solution"])
        self.debate_engine.register_participant("Critic", self.agents["critic"])
        self.debate_engine.register_participant("Security", self.agents["security"])
        self.debate_engine.register_participant("Optimizer", self.agents["optimizer"])

    def _initialize_agents(self) -> Dict[str, Any]:
        return {
            "analysis": AnalysisAgent(self.memory_manager, self.logger, self.model_router),
            "solution": SolutionAgent(self.memory_manager, self.logger, self.model_router),
            "critic": CriticAgent(self.memory_manager, self.logger, self.model_router),
            "security": SecurityAgent(self.memory_manager, self.logger, self.model_router),
            "optimizer": OptimizerAgent(self.memory_manager, self.logger, self.model_router),
            "generation": GenerationAgent(self.memory_manager, self.logger, self.model_router),
            "coding": CodingAgent(self.memory_manager, self.logger, self.model_router),
            "cli": CLIAgent(self.memory_manager, self.logger, self.model_router),
            "validation": ValidationAgent(self.memory_manager, self.logger, self.model_router)
        }

    async def run_workflow(self, request: str):
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        trace_id = f"tr_{uuid.uuid4().hex[:8]}"
        
        self.logger.log_workflow_event("WORKFLOW_START", workflow_id, {"request": request}, trace_id=trace_id)
        
        try:
            # 1. load_memory_context()
            self.logger.log_workflow_event("LOAD_MEMORY", workflow_id, "Loading context...", trace_id=trace_id)
            
            # 2. classify_request()
            # 3. retrieve_similar_workflows()
            similar_workflows = self.memory_manager.retrieve_similar_workflows(request)
            self.logger.log_workflow_event("CONTEXT_RETRIEVED", workflow_id, {"matches": len(similar_workflows)}, trace_id=trace_id)
            
            # 4. build_initial_plan()
            self.agents["analysis"].set_mode("EXECUTION_MODE", trace_id=trace_id)
            initial_plan = await self.agents["analysis"].execute({"request": request}, trace_id=trace_id)
            
            # 5. EXECUTE DEBATE ENGINE
            debate_results = await self.debate_engine.run_debate(workflow_id, request, trace_id)
            
            # 6. resolve_final_decision_from_debate()
            decision = debate_results["consensus_decision"]
            if "REJECTED" in decision:
                self.logger.error(f"Workflow {workflow_id} rejected by debate engine.")
                return {"status": "REJECTED", "reason": decision, "debate": debate_results}

            # 7. assign_execution_agents() & 8. execute_plan()
            # We use the initial_plan which contains the DAG
            execution_results = await self.execution_engine.execute_workflow(
                workflow_id, 
                initial_plan, 
                trace_id=trace_id
            )
            
            if execution_results.get("status") != "success":
                self.logger.error(f"Workflow {workflow_id} execution failed.")
                return {
                    "workflow_id": workflow_id,
                    "status": "FAILED",
                    "execution_results": execution_results,
                    "trace_id": trace_id
                }

            # 9. validate_results()
            # ValidationAgent can be part of the DAG, but we can also do a final pass
            validation = await self.agents["validation"].execute({
                "params": {"data": execution_results["results"]}
            }, trace_id=trace_id)
            
            # 10. store_all_in_memory()
            self.memory_manager.store_workflow_data(workflow_id, request, status="COMPLETED", metadata=execution_results["results"])
            self.memory_manager.store_decision(f"dec_{workflow_id}", workflow_id, decision, reasoning_trace=debate_results["reasoning_trace"])
            
            # 11. audit log final decision
            self.logger.log_decision(workflow_id, f"dec_{workflow_id}", decision, debate_results["reasoning_trace"], trace_id=trace_id)
            
            final_output = {
                "workflow_id": workflow_id,
                "status": "COMPLETED",
                "decision": decision,
                "output": execution_results,
                "validation": validation,
                "trace_id": trace_id
            }
            self.logger.log_workflow_event("WORKFLOW_END", workflow_id, final_output, trace_id=trace_id)
            return final_output

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            self.logger.log_workflow_event("WORKFLOW_FAILED", workflow_id, {"error": str(e)}, trace_id=trace_id)
            raise
