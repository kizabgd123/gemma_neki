import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.base_agent import BaseAgent
from memory.manager import MemoryManager
from observability.logger import audit_logger

class MockAgent(BaseAgent):
    async def execute(self, context: dict, trace_id: str):
        self.log_action(trace_id, "test_action", {"key": "value"})

class TestBaseAgentLogging(unittest.TestCase):
    def setUp(self):
        # Use a separate test database
        self.db_path = "storage/test_memory.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.memory_manager = MemoryManager(db_path=self.db_path)
        self.agent = MockAgent("TestAgent", self.memory_manager)

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_log_action_persistence(self):
        """Verify that log_action persists data correctly to the MemoryManager."""
        trace_id = "test-trace-logging"
        action = "process_data"
        details = {"status": "success", "items": 5}
        
        # Call log_action
        self.agent.log_action(trace_id, action, details, level="info")
        
        # Verify persistence in MemoryManager SQLite DB
        with self.memory_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM execution_traces WHERE workflow_id = ?", (trace_id,))
            trace = cursor.fetchone()
            
            self.assertIsNotNone(trace, "Trace should be persisted in database")
            self.assertEqual(trace["workflow_id"], trace_id)
            # Action should be formatted as {agent_name}:{action}
            self.assertEqual(trace["action"], "TestAgent:process_data")
            # Details should be converted to string for 'result' column
            self.assertEqual(trace["result"], str(details))

    def test_log_action_levels(self):
        """Verify that log_action calls the correct AuditLogger levels."""
        trace_id = "test-trace-levels"
        
        # Test debug level through assertLogs
        with self.assertLogs('AIWorkflowOrchestrator.Audit', level='DEBUG') as cm:
            self.agent.log_action(trace_id, "debug_action", "debug details", level="debug")
            # cm.output contains the formatted log messages
            self.assertTrue(any("debug_action" in output for output in cm.output))
            self.assertTrue(any("DEBUG" in output for output in cm.output))

        # Test error level
        with self.assertLogs('AIWorkflowOrchestrator.Audit', level='ERROR') as cm:
            self.agent.log_action(trace_id, "error_action", "critical error", level="error")
            self.assertTrue(any("error_action" in output for output in cm.output))
            self.assertTrue(any("ERROR" in output for output in cm.output))

if __name__ == "__main__":
    unittest.main()
