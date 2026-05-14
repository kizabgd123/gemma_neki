import os
from agents.base_agent import BaseAgent

class CodingAgent(BaseAgent):
    def __init__(self, memory_manager, logger, model_router=None):
        super().__init__(
            name="CodingAgent", 
            description="Specialized in file modifications and code implementation.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger
        )
        # In a production environment, this should be pulled from core.config
        self.workspace = "/home/kizabgd/.gemini/antigravity/brain/memoriJADA"

    async def execute(self, context: dict, trace_id: str):
        filepath = context.get("filepath")
        content = context.get("content", "")
        action = context.get("action", "write")  # Supported actions: write, append

        self.log_action(trace_id, "start_coding_task", {"filepath": filepath, "action": action})

        # Consult historical patterns for similar file modifications
        history = self.get_relevant_history(filepath)
        
        full_path = os.path.join(self.workspace, filepath)

        # Capture state for potential rollback
        existed = os.path.exists(full_path)
        old_content = None
        if existed:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            except Exception:
                pass

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            mode = 'w' if action == "write" else 'a'
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "status": "success", 
                "filepath": filepath, 
                "history_consulted": len(history) > 0,
                "rollback_data": {
                    "type": "file_write",
                    "path": full_path,
                    "existed": existed,
                    "old_content": old_content
                }
            }
            self.log_action(trace_id, "coding_task_completed", result)
            return result
        except Exception as e:
            error_details = {"error": str(e), "filepath": filepath}
            self.log_action(trace_id, "coding_task_failed", error_details)
            return {"status": "failure", "error": str(e)}