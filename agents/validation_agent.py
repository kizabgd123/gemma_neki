from agents.base_agent import BaseAgent

class ValidationAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None):
        super().__init__(
            name="ValidationAgent", 
            description="Performs quality checks and verifies task outcomes.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger
        )

    async def execute(self, context: dict, trace_id: str):
        """
        Performs quality checks on data provided in context.
        Can handle single task results or a dictionary of DAG results.
        """
        data_to_validate = context.get("params", {}).get("data")
        self.log_action(trace_id, "starting_validation", {"data_summary": str(data_to_validate)[:100]})

        # Memory integration: retrieve past execution patterns to identify recurring issues
        history = self.get_relevant_history(str(data_to_validate))
        
        issues = []
        if data_to_validate is None:
            issues.append("Validation failed: No data provided.")
        
        # If validating a collection of DAG results
        if isinstance(data_to_validate, dict):
            for task_id, task_result in data_to_validate.items():
                if isinstance(task_result, dict) and task_result.get("status") in ["failure", "error", "blocked"]:
                    issues.append(f"Task {task_id} failed with status '{task_result.get('status')}': {task_result.get('error', 'Unknown error')}")
        
        # Simple heuristic check for 'error' in string representations
        elif isinstance(data_to_validate, str) and ("error" in data_to_validate.lower() or "exception" in data_to_validate.lower()):
            issues.append("String data contains error/exception keywords.")

        is_valid = len(issues) == 0
        
        result = {
            "is_valid": is_valid,
            "issues": issues,
            "history_consulted": len(history) > 0,
            "match_history_count": len(history)
        }
        
        self.log_action(trace_id, "validation_completed", result)
        return result