import json
import sys
import os

# Add parent directory to sys.path to import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.base_agent import BaseAgent

class MockLogger:
    def error(self, msg): print(f"ERROR: {msg}")
    def log_agent_action(self, *args, **kwargs): pass

agent = BaseAgent("Test", "Test", None, None, MockLogger())

test_cases = [
    '{"a": 1}',
    '```json\n{"b": 2}\n```',
    'Some text before\n```json\n{"c": 3}\n```\nSome text after',
    '{"d": 4,}', # Trailing comma
    '{"e": "unescaped\nnewline"}', # Unescaped newline
    'Plain text with JSON inside: {"f": 5} and more text.'
]

for i, test in enumerate(test_cases):
    try:
        result = agent.parse_json_robust(test)
        print(f"Test {i} success: {result}")
    except Exception as e:
        print(f"Test {i} failed: {e}")
