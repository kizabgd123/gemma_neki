# memory/manager.py
import sqlite3
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="storage/memory.db", logger=None):
        self.db_path = db_path
        self.logger = logger
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Workflows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    request TEXT NOT NULL,
                    status TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Debates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debates (
                    debate_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    status TEXT,
                    final_consensus TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                )
            """)

            # Arguments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arguments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debate_id TEXT,
                    agent_name TEXT NOT NULL,
                    argument TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(debate_id) REFERENCES debates(debate_id)
                )
            """)

            # Decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    decision TEXT NOT NULL,
                    reasoning_trace TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                )
            """)

            # Agent Opinions History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_opinions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    workflow_id TEXT,
                    opinion TEXT,
                    stance TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Execution Traces
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    workflow_id TEXT,
                    step_name TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Plans table (added for get_best_plans)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    plan_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    plan_json TEXT NOT NULL,
                    success_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                )
            """)
            conn.commit()

    def store_workflow_data(self, workflow_id, request, status="PENDING", metadata=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO workflows (workflow_id, request, status, metadata) VALUES (?, ?, ?, ?)",
                (workflow_id, request, status, json.dumps(metadata) if metadata else None)
            )
            conn.commit()

    def store_agent_opinion(self, agent_name, workflow_id, opinion, stance, confidence):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agent_opinions (agent_name, workflow_id, opinion, stance, confidence) VALUES (?, ?, ?, ?, ?)",
                (agent_name, workflow_id, json.dumps(opinion) if isinstance(opinion, dict) else opinion, stance, confidence)
            )
            conn.commit()

    def get_agent_reliability(self, agent_name):
        """Calculates a reliability score based on historical successful workflows."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Join agent_opinions with plans/workflows to see how many 'Approved' stances led to high success scores
            cursor.execute("""
                SELECT AVG(p.success_score) FROM agent_opinions ao
                JOIN plans p ON ao.workflow_id = p.workflow_id
                WHERE ao.agent_name = ? AND ao.stance = 'Approved'
            """, (agent_name,))
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0.8  # Default high reliability for new agents

    def retrieve_similar_workflows(self, query):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Basic similarity lookup
            cursor.execute("SELECT * FROM workflows WHERE request LIKE ? LIMIT 5", (f'%{query}%',))
            return cursor.fetchall()

    def get_best_plans(self, request):
        """Retrieve successful plans for similar requests."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.plan_json FROM plans p
                JOIN workflows w ON p.workflow_id = w.workflow_id
                WHERE w.request LIKE ? AND p.success_score > 0.8
                ORDER BY p.success_score DESC LIMIT 3
            """, (f'%{request}%',))
            rows = cursor.fetchall()
            return [json.loads(row[0]) for row in rows]

    def store_debate_session(self, debate_id, workflow_id, status="OPEN", final_consensus=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO debates (debate_id, workflow_id, status, final_consensus) VALUES (?, ?, ?, ?)",
                (debate_id, workflow_id, status, final_consensus)
            )
            conn.commit()

    def store_argument(self, debate_id, agent_name, argument, confidence_score=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO arguments (debate_id, agent_name, argument, confidence_score) VALUES (?, ?, ?, ?)",
                (debate_id, agent_name, argument, confidence_score)
            )
            conn.commit()

    def store_decision(self, decision_id, workflow_id, decision, reasoning_trace=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO decisions (decision_id, workflow_id, decision, reasoning_trace) VALUES (?, ?, ?, ?)",
                (decision_id, workflow_id, decision, json.dumps(reasoning_trace) if reasoning_trace else None)
            )
            conn.commit()

    def log_execution_trace(self, trace_id, workflow_id, step_name, details):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO execution_traces (trace_id, workflow_id, step_name, details) VALUES (?, ?, ?, ?)",
                (trace_id, workflow_id, step_name, json.dumps(details) if isinstance(details, dict) else details)
            )
            conn.commit()

    def get_similar_debates(self, context_query):
        """Retrieve historical debate contexts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Basic implementation
            cursor.execute("""
                SELECT d.debate_id, d.final_consensus, w.request FROM debates d
                JOIN workflows w ON d.workflow_id = w.workflow_id
                WHERE w.request LIKE ? LIMIT 3
            """, (f'%{context_query}%',))
            return cursor.fetchall()

