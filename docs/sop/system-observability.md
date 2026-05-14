---
title: "System Observability"
description: "How to monitor, trace, and audit the orchestrator swarm."
keywords: ["logging", "tracing", "audit", "trace_id", "failover"]
robots: "index, follow"
---

# System Observability

> **Quick Reference**
> - **Who**: Jordan the MLOps Specialist
> - **Where**: `observability/orchestrator.log` and SQLite
> - **Time**: ~5-10 minutes for investigation
> - **Key Tool**: `grep` and SQL queries

## Prerequisites

- [ ] Access to the `storage/` and `observability/` directories
- [ ] Basic knowledge of SQL

## Step-by-Step Guide

### Step 1: Trace a Workflow

1. Each mission is assigned a unique `trace_id` (e.g., `tr_a1b2c3d4`).
2. Search for all events related to a specific trace in the log:

   ```bash
   grep "tr_a1b2c3d4" observability/orchestrator.log
   ```

3. Look for the `event_type` field to identify the lifecycle stage:
   - `WORKFLOW_START`
   - `AGENT_ACTION`
   - `FINAL_DECISION`

### Step 2: Audit Agent Reliability

1. The system tracks how often agents are overridden or vetoed.
2. Query the `agent_opinions` table to see current reliability scores:

   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('storage/memory.db'); print(conn.execute('SELECT agent_name, AVG(confidence) FROM agent_opinions GROUP BY agent_name').fetchall())"
   ```

### Step 3: Inspect Model Failover

1. If you suspect high latency or model errors, check for fallback events.
2. Search for "Switching to fallback model" in the logs.

:::info
Model routing includes a 5-minute cooldown period for unhealthy models `(agents/model_router.py:15)`.
:::

## Expected Results

- ✅ Every agent action is timestamped and logged with a trace ID.
- ✅ Failures are captured with full stack traces or error payloads.
- ✅ Multi-pass JSON parsing attempts are logged for debugging.

## Troubleshooting

<details>
<summary>🔴 Error: JSON logs are unreadable</summary>

**Cause**: Log rotation or corrupted writes.

**Solution**:
1. Use a JSON formatter like `jq` to prettify the output:
   ```bash
   tail -f observability/orchestrator.log | jq .
   ```

</details>

## FAQ

<details>
<summary>Q: Where can I see the full reasoning trace?</summary>

**A**: It is stored in the `decisions` table as a JSON blob in the `reasoning_trace` column. (memory/manager.py:145)

</details>

---

## Related
- [Workflow Management](./workflow-management.md)
- [Database Schema](../database.md)
