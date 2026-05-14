# Design Specification: Report-Bot 2026

## 1. System Components

### 1.1 Intent & Modality Dispatcher
- **Responsibility:** Identify input modality (audio, video, text) and intent (report, research, synthesis).
- **Implementation:** Gemini Nano locally running on the CLI to minimize latency.
- **Output:** JSON schema dispatch instruction.

### 1.2 Agent Mesh (Worker Layer)
- **Specialization:** Agents are configured with specific `tool_sets`.
- **Communication:** Async message queue (Redis-lite or in-memory) for inter-agent communication.

### 1.3 Plan-Act-Verify Engine
- **Workflow:** 
    1. **Plan:** Decompose task into DAG.
    2. **Act:** Worker agents execute specific DAG nodes.
    3. **Verify:** Critic model checks output quality against acceptance criteria defined in phase 1.
    4. **Loop:** If Verify < 0.9, re-dispatch to Worker.

## 2. Tool Schema (Example)
All tools must adhere to the following schema for discoverability:
```json
{
  "name": "string",
  "description": "string",
  "parameters": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  }
}
```

## 3. Data Flow
Input (Video/Audio) -> [Dispatcher] -> [Planner] -> [Worker Mesh] -> [Critic] -> Output (PDF/Report)

## 4. Security & Compliance
- **PII Handling:** All PII must be redacted before sending to external model APIs.
- **Tracing:** Every action logged with unique `trace_id` in SQLite.
- **Access Control:** Agent access to local file system limited by project directory.
