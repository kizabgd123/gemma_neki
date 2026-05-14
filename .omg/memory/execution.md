# Execution & Workflow Tracing

## Orchestration Flow
1. **Context Load**: Initialize memory and retrieve similar patterns.
2. **Intent Classification**: Map user request to workflow templates.
3. **Planning**: Construct initial DAG of tasks.
4. **Debate Loop**: Run multi-agent reasoning for high-impact decisions.
5. **Execution**: Parallel/sequential task dispatch via `ExecutionEngine`.
6. **Validation**: Result verification by `ValidationAgent`.
7. **Closure**: Store traces and audit logs.

## Observability Standards
- `OrchestratorLogger` for system-wide tracing.
- Mandatory `trace_id` for all events.
- Audit logs stored in `.bkit/audit/` and SQLite.
