import asyncio
from observability.logger import audit_logger

class ExecutionEngine:
    def __init__(self, memory_manager, agents=None):
        self.memory_manager = memory_manager
        self.agents = agents or {}

    def register_agents(self, agents_dict):
        self.agents.update(agents_dict)

    async def execute_workflow(self, workflow_id, plan, trace_id=None):
        """
        Executes a plan defined as a DAG.
        Plan structure:
        {
            "tasks": [
                {"id": "task1", "agent": "CodingAgent", "params": {...}, "depends_on": []},
                {"id": "task2", "agent": "CLIAgent", "params": {...}, "depends_on": ["task1"]},
            ]
        }
        """
        audit_logger.log_workflow_event("WORKFLOW_START", workflow_id, {"plan_size": len(plan.get("tasks", []))}, trace_id)
        
        tasks = plan.get("tasks", [])
        results = {}
        # Simple dependency tracker
        completed_tasks = set()
        
        # We'll use a loop to find and execute tasks whose dependencies are met
        while len(completed_tasks) < len(tasks):
            ready_tasks = [
                t for t in tasks 
                if str(t["id"]) not in completed_tasks and all(str(dep) in completed_tasks for dep in t.get("depends_on", []))
            ]
            
            if not ready_tasks:
                if len(completed_tasks) < len(tasks):
                    error_msg = f"Deadlock or missing dependency detected in workflow plan. Completed: {completed_tasks}, Remaining: {[t['id'] for t in tasks if str(t['id']) not in completed_tasks]}"
                    audit_logger.error(error_msg)
                    return {"status": "error", "error": error_msg, "results": results}
                break

            # Execute ready tasks in parallel
            execution_group = []
            for task in ready_tasks:
                execution_group.append(self._execute_single_task(workflow_id, task, results, trace_id))
            
            group_results = await asyncio.gather(*execution_group)
            
            for task_id, task_result in group_results:
                results[str(task_id)] = task_result
                completed_tasks.add(str(task_id))
                if task_result.get("status") in ["failure", "error", "blocked"]:
                    audit_logger.log_workflow_event("WORKFLOW_HALTED", workflow_id, {"task_id": task_id, "reason": "task_failed"}, trace_id)
                    # For now, we stop the whole workflow on any task failure
                    return {"status": "failed", "failed_task": task_id, "results": results}

        audit_logger.log_workflow_event("WORKFLOW_COMPLETE", workflow_id, {"status": "success"}, trace_id)
        return {"status": "success", "results": results}

    async def _execute_single_task(self, workflow_id, task, all_results, trace_id):
        task_id = task["id"]
        agent_name = task["agent"]
        params = task.get("params", {})
        
        # Inject results of dependencies if needed (e.g., params might reference them)
        context = {
            "workflow_id": workflow_id,
            "task_id": str(task_id),
            "params": params,
            "dependency_results": {str(dep): all_results[str(dep)] for dep in task.get("depends_on", [])}
        }

        agent = self.agents.get(agent_name)
        if not agent:
            error_result = {"status": "error", "error": f"Agent '{agent_name}' not found."}
            audit_logger.log_execution(workflow_id, agent_name, task_id, error_result, trace_id)
            return task_id, error_result

        audit_logger.log_execution(workflow_id, agent_name, task_id, {"status": "starting"}, trace_id)
        
        try:
            # Most agents have 'execute(context, trace_id)' signature
            result = await agent.execute(context, trace_id)
            audit_logger.log_execution(workflow_id, agent_name, task_id, {"status": "finished", "result_summary": str(result)[:100]}, trace_id)
            return task_id, result
        except Exception as e:
            error_result = {"status": "error", "error": str(e)}
            audit_logger.log_execution(workflow_id, agent_name, task_id, error_result, trace_id)
            return task_id, error_result
