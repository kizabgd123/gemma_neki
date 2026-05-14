import asyncio
import os
import json
import pytest
from agents.analysis_agent import AnalysisAgent
from agents.critic_agent import CriticAgent
from memory.manager import MemoryManager
from agents.model_router import ModelAvailabilityService
from observability.logger import audit_logger

@pytest.mark.asyncio
async def test_debate_modes():
    # 1. Setup
    db_path = "storage/test_memory.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    memory_manager = MemoryManager(db_path=db_path, logger=audit_logger)
    model_router = ModelAvailabilityService()
    trace_id = "test_trace_debate"
    
    # 2. Initialize agents in debate mode
    analysis_agent = AnalysisAgent(memory_manager=memory_manager, logger=audit_logger, model_router=model_router, debate_mode=True)
    critic_agent = CriticAgent(memory_manager=memory_manager, logger=audit_logger, model_router=model_router, debate_mode=True)
    
    assert analysis_agent.debate_mode is True
    assert critic_agent.debate_mode is True
    
    # 3. Test AnalysisAgent in debate mode
    request = "Implement a secure authentication system using JWT."
    context = {"request": request}
    
    print("\n[*] Running AnalysisAgent in debate mode...")
    proposal = await analysis_agent.execute(context, trace_id)
    
    print(f"Proposal generated: {json.dumps(proposal, indent=2)}")
    
    # Verify AnalysisAgent output structure for debate mode
    assert "proposal" in proposal
    assert "assumptions" in proposal
    assert "potential_risks" in proposal
    assert "alternative_approaches" in proposal
    
    # 4. Test CriticAgent in debate mode
    print("\n[*] Running CriticAgent in debate mode...")
    critique_context = {
        "proposal": proposal,
        "criteria": {"security": "Check for JWT secret leakage and algorithm strength."}
    }
    critique = await critic_agent.execute(critique_context, trace_id)
    
    print(f"Critique generated: {json.dumps(critique, indent=2)}")
    
    # Verify CriticAgent output structure for debate mode
    assert "logical_flaws" in critique
    assert "missing_edge_cases" in critique
    assert "security_concerns" in critique
    assert "improvement_suggestions" in critique
    assert "overall_confidence_score" in critique
    
    # 5. Verify Memory Traces
    with memory_manager._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM execution_traces WHERE trace_id = ?", (trace_id,))
        traces = cursor.fetchall()
        
        # Check for specific debate-mode related logs
        step_names = [t["step_name"] for f, t in enumerate(traces)]
        assert "AnalysisAgent:start_debate_analysis" in step_names
        assert "AnalysisAgent:proposal_generated" in step_names
        assert "CriticAgent:start_critique" in step_names
        assert "CriticAgent:critique_generated" in step_names

    print("\n[+] All debate mode tests passed!")

if __name__ == "__main__":
    asyncio.run(test_debate_modes())
