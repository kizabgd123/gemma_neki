import asyncio
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.engine import ExecutionEngine

class MockAgent:
    def __init__(self, name):
        self.name = name
    async def execute(self, context, trace_id):
        print(f"Agent {self.name} executing task {context['task_id']}")
        await asyncio.sleep(0.1)
        return {"status": "success", "agent": self.name, "task_id": context['task_id']}

async def main():
    engine = ExecutionEngine(None)
    agents = {
        "CodingAgent": MockAgent("CodingAgent"),
        "CLIAgent": MockAgent("CLIAgent"),
        "ValidationAgent": MockAgent("ValidationAgent")
    }
    engine.register_agents(agents)

    plan = {
        "tasks": [
            {"id": 1, "agent": "CodingAgent", "params": {}, "depends_on": []},
            {"id": 2, "agent": "CodingAgent", "params": {}, "depends_on": []},
            {"id": 3, "agent": "CLIAgent", "params": {}, "depends_on": [1, 2]},
            {"id": 4, "agent": "ValidationAgent", "params": {}, "depends_on": [3]}
        ]
    }

    print("Starting workflow...")
    results = await engine.execute_workflow("wf_test", plan, "tr_test")
    print("\nWorkflow Results:")
    import json
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
