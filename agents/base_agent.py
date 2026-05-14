# agents/base_agent.py
import json
import re

class BaseAgent:
    def __init__(self, name, description, model_router, memory_manager, logger, debate_mode=False):
        self.name = name
        self.description = description
        self.model_router = model_router
        self.memory_manager = memory_manager
        self.logger = logger
        self.debate_mode = debate_mode
        self.mode = "DEBATE_MODE" if debate_mode else "EXECUTION_MODE"

    def set_mode(self, mode, trace_id=None):
        if mode in ["EXECUTION_MODE", "DEBATE_MODE"]:
            self.mode = mode
            self.debate_mode = (mode == "DEBATE_MODE")
            self.logger.log_agent_action(self.name, None, None, "mode_set", {"new_mode": mode}, trace_id=trace_id)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def log_action(self, trace_id, action, details, workflow_id=None, task_id=None):
        """Helper for structured logging within agent subclasses."""
        self.logger.log_agent_action(
            agent_name=self.name,
            workflow_id=workflow_id,
            task_id=task_id,
            action=action,
            details=details,
            trace_id=trace_id
        )
        if self.memory_manager:
            self.memory_manager.log_execution_trace(
                trace_id=trace_id,
                workflow_id=workflow_id or trace_id,
                step_name=f"{self.name}:{action}",
                details=details
            )

    def get_relevant_history(self, query):
        """Retrieve historical context from memory."""
        return self.memory_manager.retrieve_similar_workflows(query)

    async def execute(self, context, trace_id):
        if self.mode != "EXECUTION_MODE":
            self.logger.warning(f"Agent {self.name} is not in EXECUTION_MODE. Current mode: {self.mode}")
            return f"Agent {self.name} cannot execute in {self.mode}."
        
        workflow_id = context.get("workflow_id")
        task_id = context.get("task_id")
        
        self.log_action(trace_id, "execute_start", {"context": context}, workflow_id, task_id)
        # Actual implementation logic will be in subclasses
        result = f"Agent {self.name} executed task based on context."
        self.log_action(trace_id, "execute_end", {"result": result}, workflow_id, task_id)
        return result

    async def debate(self, context, workflow_id=None, debate_id=None, trace_id=None):
        if self.mode != "DEBATE_MODE":
            self.logger.warning(f"Agent {self.name} is not in DEBATE_MODE. Current mode: {self.mode}")
            return f"Agent {self.name} cannot debate in {self.mode}."
        
        self.log_action(trace_id, "debate_start", {"context": context}, workflow_id, debate_id)
        # Actual debate logic will be in subclasses
        argument = f"Agent {self.name} argues based on context: {context}"
        self.log_action(trace_id, "debate_end", {"argument": argument}, workflow_id, debate_id)
        return argument

    def parse_json_robust(self, text):
        """Attempts to parse JSON from LLM response, handling common issues like markdown blocks or unescaped characters."""
        if not text:
            return None

        # Pass 1: Try direct parsing
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Pass 2: Extract from markdown code blocks
        json_blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        for block in json_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                # Try to clean common issues in the block
                cleaned_block = self._clean_json_string(block)
                try:
                    return json.loads(cleaned_block)
                except json.JSONDecodeError:
                    continue

        # Pass 3: Brute-force extraction of anything that looks like a JSON object or array
        # This finds the first { or [ and the last } or ]
        match = re.search(r'([\{\[].*[\}\]])', text, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # Try cleaning the candidate
                cleaned_candidate = self._clean_json_string(candidate)
                try:
                    return json.loads(cleaned_candidate)
                except json.JSONDecodeError:
                    pass

        self.logger.error(f"Failed to parse JSON from agent {self.name}. Text snippet: {text[:200]}...")
        raise ValueError(f"Agent {self.name} returned invalid JSON format.")

    def _clean_json_string(self, s):
        """Cleans common LLM JSON hallucinations."""
        # Remove unescaped newlines in strings
        # This is tricky because some newlines ARE part of the JSON structure
        # We only want to escape newlines that are inside double quotes
        
        # Simple fix for unescaped backslashes that are not part of valid escape sequences
        # Actually, let's focus on unescaped control characters
        s = s.replace('\n', ' ').replace('\r', ' ')
        
        # Remove trailing commas before closing braces/brackets
        s = re.sub(r',\s*([\}\]])', r'\1', s)
        
        return s
