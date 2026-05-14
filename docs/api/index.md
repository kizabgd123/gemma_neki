---
title: "Agent Contracts (API)"
description: "Reference for internal agent communication contracts and JSON schemas."
keywords: ["api reference", "agent contracts", "schemas", "json-rpc"]
robots: "index, follow"
---

# Agent Contracts Reference

> **Quick Reference**
> - **Interaction Pattern**: Async JSON-RPC
> - **Auth**: Local Environment / API Keys
> - **Primary Format**: Structured JSON

## Overview
This documentation defines the input and output contracts for the specialized agents within the orchestrator. Adhering to these contracts ensures deterministic execution and reliable parsing.

## Available Agent Roles

| Agent | Purpose | Primary Interface |
|-------|---------|-------------------|
| **Analyst** | Workflow Decomposition | `execute(request) ➜ DAG JSON` |
| **Solution** | Technical Implementation | `execute(context) ➜ CODE JSON` |
| **Critic** | Peer Review | `execute(proposal) ➜ AUDIT JSON` |
| **Security** | Vulnerability Scan | `execute(proposal) ➜ RISK JSON` |

---

## Analyst Agent Contract

Generates a Directed Acyclic Graph (DAG) for implementation.

### Request Body
```json
{
  "request": "Implement a logging system."
}
```

### Response Body
**200 OK (Validated Plan)**
```json
{
  "tasks": [
    {
      "id": 1,
      "agent": "CodingAgent",
      "description": "Initialize logger configuration.",
      "params": { "query": "..." },
      "depends_on": []
    }
  ],
  "risks": ["Performance overhead"]
}
```

### Examples

<details>
<summary>Python (Direct Call)</summary>

```python
from agents.analysis_agent import AnalysisAgent

agent = AnalysisAgent(memory_manager, logger)
plan = await agent.execute({"request": "Task..."}, trace_id="tr_123")
```

</details>

---

## Model Router API

Handles model failover and retries.

| Method | Description | Fallback |
|--------|-------------|----------|
| `execute_with_routing` | Runs a completion with auto-retry. | Gemini ➜ Mistral |

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| 429 | Rate Limit | Primary model quota exhausted. |
| 500 | Context Failed | All models in fallback chain failed. |

---

## See Also
- [System Architecture](../architecture.md)
- [Database Schema](../database.md)
