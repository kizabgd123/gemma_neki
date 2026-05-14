# observability/logger.py

import logging
import json
import os
from datetime import datetime

class OrchestratorLogger:
    def __init__(self, log_file="observability/orchestrator.log"):
        # Osiguraj da direktorijum postoji
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        self.log_file = log_file
        self.logger = logging.getLogger("orchestrator_logger")
        self.logger.setLevel(logging.INFO)

        # File handler za JSON logove
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler za upozorenja i greške
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Čišćenje prethodnih handlera ako postoje
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _log_event(self, event_data):
        event_data["timestamp"] = datetime.now().isoformat()
        self.logger.info(json.dumps(event_data))

    def log_workflow_event(self, event_type, workflow_id, details, trace_id=None):
        self._log_event({
            "event_type": event_type,
            "workflow_id": workflow_id,
            "trace_id": trace_id,
            "details": details
        })

    def log_debate_event(self, event_type, workflow_id, debate_id, details, trace_id=None):
        self._log_event({
            "event_type": event_type,
            "workflow_id": workflow_id,
            "debate_id": debate_id,
            "trace_id": trace_id,
            "details": details
        })

    def log_agent_action(self, agent_name, workflow_id, task_id, action, details, trace_id=None):
        self._log_event({
            "event_type": "AGENT_ACTION",
            "agent_name": agent_name,
            "workflow_id": workflow_id,
            "task_id": task_id,
            "trace_id": trace_id,
            "action": action,
            "details": details
        })

    def log_decision(self, workflow_id, decision_id, decision, reasoning_trace, trace_id=None):
        self._log_event({
            "event_type": "FINAL_DECISION",
            "workflow_id": workflow_id,
            "decision_id": decision_id,
            "trace_id": trace_id,
            "decision": decision,
            "reasoning_trace": reasoning_trace
        })

    def log_execution(self, workflow_id, agent_name, step, details, trace_id=None):
        """Compatibility method for legacy execution logging."""
        self._log_event({
            "event_type": "EXECUTION_TRACE",
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "step": step,
            "details": details,
            "trace_id": trace_id
        })

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

# Global instance for easy access
audit_logger = OrchestratorLogger()
