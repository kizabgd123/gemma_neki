# Phase 1: Core Foundation & Memory System Implementation

## Objective
Implement a production-grade memory system using SQLite and a standardized observability layer to enable agent reasoning persistence and auditability.

## Background & Motivation
The current `MemoryManager` and `OrchestratorLogger` are largely placeholders. To support the "AI Workflow Orchestrator" with a debate mechanism, we need a persistent store for workflows, debates, decisions, and agent historical outputs.

## Proposed Solution

### 1. Memory System (SQLite Backend)
Implement `MemoryManager` in `memory/manager.py` with the following tables:
- `workflows`: Store initial requests and high-level metadata.
- `debates`: Track debate sessions linked to workflows.
- `arguments`: Individual agent contributions to a debate.
- `decisions`: Final consensus or decisions made post-debate.
- `agent_opinions`: Historical trace of agent stances over time.
- `execution_traces`: Step-by-step audit trail of workflow execution.

### 2. Observability (Structured Logging)
Standardize `OrchestratorLogger` in `observability/logger.py` to:
- Log to both a file (`orchestrator.log`) and potentially a separate SQLite table for fast lookup.
- Use structured JSON formats for all logs to facilitate automatic analysis.

### 3. Agent Integration
Refactor `BaseAgent` in `agents/base_agent.py` to:
- Use the new `MemoryManager` for storing/retrieving context.
- Ensure every significant action is logged through `OrchestratorLogger`.

## Phased Implementation Plan

### Step 1: SQL Schema Definition
Create the `_initialize_db` method in `MemoryManager` with full schema definitions.

### Step 2: Persistence Methods
Implement CRUD operations in `MemoryManager`:
- `store_workflow_data`, `retrieve_similar_workflows`
- `store_debate_session`, `store_argument`
- `store_decision`, `retrieve_decisions`

### Step 3: Logger Enhancements
Update `OrchestratorLogger` to include `trace_id` in all events for end-to-end correlation.

### Step 4: BaseAgent Refactoring
Ensure `BaseAgent` uses the centralized logger and provides convenience methods for memory access.

## Verification
- **Unit Tests:** `tests/test_memory_manager.py` (to be created) to verify table creation and data retrieval.
- **Audit Check:** Verify `orchestrator.log` contains structured JSON for all agent actions.
