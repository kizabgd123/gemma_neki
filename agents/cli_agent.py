import subprocess
from agents.base_agent import BaseAgent

class CLIAgent(BaseAgent):
    # Whitelist of allowed commands to ensure system safety
    ALLOWED_COMMANDS = {
        "ls", "pwd", "mkdir", "touch", "cat", "grep", 
        "pytest", "python", "pip", "git", "echo", "cd"
    }

    def __init__(self, memory_manager, logger, model_router=None):
        super().__init__(
            name="CLIAgent", 
            description="Executes system commands within a security whitelist.",
            model_router=model_router, 
            memory_manager=memory_manager, 
            logger=logger
        )

    def is_safe(self, command: str) -> bool:
        if not command:
            return False
        # Extract the base command (e.g., 'ls' from 'ls -la')
        base_cmd = command.split()[0]
        return base_cmd in self.ALLOWED_COMMANDS

    async def execute(self, context: dict, trace_id: str):
        command = context.get("command")
        self.log_action(trace_id, "cli_execution_request", {"command": command})

        if not self.is_safe(command):
            error_msg = f"Security Violation: Command '{command}' is not whitelisted."
            self.log_action(trace_id, "security_block", {"error": error_msg})
            return {"status": "blocked", "error": error_msg}

        try:
            # Execute the command and capture output
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result_data = {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            }
            self.log_action(trace_id, "cli_execution_finished", result_data)
            return {"status": "success" if process.returncode == 0 else "failure", "details": result_data}
        except Exception as e:
            self.log_action(trace_id, "cli_execution_error", {"error": str(e)})
            return {"status": "error", "error": str(e)}