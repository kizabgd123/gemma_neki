---
title: "CLI Help"
description: "Command-line interface reference for the AI Workflow Orchestrator."
keywords: ["cli", "help", "commands", "arguments"]
robots: "index, follow"
---

# CLI Help

> **Quick Reference**
> - **Entrypoint**: `gemini-run.py`
> - **Primary Argument**: `request` (string)
> - **Output**: Validated plan or execution results

## Commands

### `python3 gemini-run.py "[request]"`

Executes a complete agentic workflow for the given request.

**Arguments:**
- `request`: The natural language instruction for the orchestrator.

**Options:**
- `--db-path`: Path to the SQLite memory database (Default: `storage/memory.db`).
- `--log-file`: Path to the orchestrator log (Default: `observability/orchestrator.log`).

## Workflow Outputs

When you run a command, the system outputs status updates for each phase:
1. **[LOAD_MEMORY]**: Context retrieval.
2. **[DEBATE_START]**: Reasoning rounds.
3. **[EXECUTION_START]**: DAG task processing.
4. **[WORKFLOW_END]**: Final results and audit.

## Troubleshooting

### Error: `429 Resource Exhausted`
This means the primary model (Gemini) has reached its quota. The system will automatically attempt fallback to Mistral. No action needed unless both fail.

### Error: `JSONDecodeError`
Commonly caused by malformed LLM responses. The system uses a multi-pass robust parser to mitigate this. If it persists, try refining your prompt for clarity.

---

## See Also
- [Deployment Guide](./deployment.md)
- [Workflow Management](./sop/workflow-management.md)
