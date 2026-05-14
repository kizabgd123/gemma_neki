---
title: "Data Flow"
description: "Data processing patterns, serialization, and external integration flows."
keywords: ["data flow", "integration", "serialization", "api"]
robots: "index, follow"
---

# Data Flow

> **Quick Reference**
> - **Pattern**: Request-Response + State Machine (Consensus)
> - **Protocol**: JSON-RPC (internal agent communication)
> - **Serialization**: JSON (standard) / Markdown-wrapped JSON (robust)

## End-to-End Data Flow

The flow of data from raw user intent to persisted validated state.

```mermaid
graph TB
    Input["📥 User Request (String)"] --> Parse["⚙️ Analysis (DAG JSON)"]
    Parse --> Reasoning["⚖️ Debate Logic (Argument Map)"]
    Reasoning --> Transform["🛠️ Execution (Task Results)"]
    Transform --> Persistence["🗄️ Memory (SQLite)"]
    Persistence --> Output["📤 Final Artifacts"]
```

## Main Workflows

### Task Result Injection

When executing a DAG, results from upstream tasks are injected into downstream task parameters to enable data-driven swarming.

```mermaid
sequenceDiagram
    participant E as Execution Engine
    participant A1 as Task 1 (Coding)
    participant A2 as Task 2 (CLI)

    E->>A1: Execute(context)
    A1-->>E: { "status": "success", "file_path": "auth.py" }
    Note over E: Inject results into Task 2
    E->>A2: Execute(context + Task 1 results)
    Note right of A2: Uses 'auth.py' for testing
    A2-->>E: { "status": "success", "test_report": "..." }
```

1. **Execution Engine** identifies Task 1 as ready.
2. **CodingAgent** completes Task 1 and returns a structured dictionary.
3. **Execution Engine** maps Task 1 output to Task 2 input based on the DAG dependencies `(execution/engine.py:75)`.
4. **CLIAgent** receives the context and performs actions on the newly created artifacts.

---

## External Integrations

| Service | Protocol | Direction | Data | Rate Limit |
|---------|----------|-----------|------|------------|
| **Google Vertex AI** | HTTPS (SDK) | Outbound | Prompts/Completion | ~20 RPM (Free Tier) |
| **Mistral AI** | HTTPS (SDK) | Outbound | Prompts/Completion | ~10 RPM |
| **Kaggle API** | HTTPS (CLI) | Outbound | Notebooks/Submissions | Per Kaggle limits |

## Reasoning Traces

The `reasoning_trace` column in the `decisions` table provides a chronological dump of how the system arrived at a conclusion.

| Step | Action | Origin | Sample Payload |
|------|--------|--------|----------------|
| 1 | `start_analysis` | AnalysisAgent | `{"request": "..."}` |
| 2 | `start_challenge` | CriticAgent | `{"logical_flaws": [...]}` |
| 3 | `start_mitigation` | SolutionAgent | `{"revised_plan": "..."}` |

---

## See Also
- [System Architecture](architecture.md)
- [Database Schema](database.md)
