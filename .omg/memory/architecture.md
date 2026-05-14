# Architecture & Core Concepts

## System Goal
Construct a complete AI Workflow Orchestrator with memory integration and multi-agent debate mechanisms.

## Core Modules
- `orchestrator/`: Workflow coordination.
- `agents/`: Specialized agent implementations (Analysis, Solution, Critic, Security, Optimizer).
- `debate/`: The reasoning engine for conflict resolution and consensus.
- `memory/`: Long-term learning using SQLite backend.
- `observability/`: Execution tracing and logging.

## Architectural Constraints
- Production-grade, deterministic, and traceable.
- Memory-integrated debate (previous decisions influence current ones).
