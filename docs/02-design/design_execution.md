# Design Specification: Report-Bot-Execution

## 1. Orchestration Engine Architecture
The orchestration engine will reside in `execution/engine.py` and interact with agents via a unified interface.

### 1.1 DAG Task Decomposer
- **Structure:** `List[TaskNode]`
- **TaskNode:** `{id: str, dependencies: List[str], agent: str, action: str}`
- **Execution:** Topological sort ensures tasks with no unmet dependencies run first.

### 1.2 Execution Controller
- **Loop:** `while ready_tasks:`
    1. Dispatch worker to task node.
    2. Await `(result, status)`.
    3. If status == 'success': Mark task done, trigger verification.
    4. If status == 'fail': Log to `observability/`, trigger self-correction.

### 1.3 Plan-Act-Verify Integration
- **Verification Hook:** After a task completes, dispatch to `CriticAgent`.
- **Self-Correction:** If `CriticAgent` reports `confidence < 0.9`, the Orchestrator updates node status to `pending_rework` and re-queues.

## 2. State & Traceability
- Every execution state change is persisted to SQLite using the `MemoryManager`.
- Each task node must have an associated `trace_id` for auditing.

## 3. Security
- Agents operate in an isolated namespace; they cannot access node state outside their `TaskNode`.
- Output of every task is scanned for PII before passing to the next dependency.
