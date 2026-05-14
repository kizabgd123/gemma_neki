# Design Document: Phase 2 - Multi-Agent Debate System

## Context Anchor
| Dimension | Content |
|-----------|---------|
| WHY | Improve AI decision making quality through structured team-based reasoning and critical challenge. |
| WHO | AI Agents (Analyst, Solution, Critic, Security, Optimizer) and System Orchestrator. |
| RISK | 1. Agent context drift during long debates. 2. Failure to reach consensus. 3. Increased token costs per decision. |
| SUCCESS | 1. Documented structured arguments for each debate. 2. Automated risk detection by Security/Critic agents. 3. Consensus-based final decisions stored in memory. |
| SCOPE | Implementation of specific agents and a central debate engine using the Phase 1 foundation. |

## 1. Overview
This design implements a multi-agent reasoning loop where specialized agents debate a proposal before final execution.

## 2. Architecture Options

### Option A: Minimal Changes (Sequential Python Loop)
- Use current `DebateEngine` with minimal refactoring.
- Agents are called in a strict synchronous sequence.
- Pros: Simple, fast to implement.
- Cons: Rigid, no parallel evaluation.

### Option B: Clean Architecture (Async Event-Driven)
- Decouple agent communication using an event-based approach.
- Support parallel reasoning from Critic and Security agents.
- Pros: Scalable, efficient resource usage.
- Cons: Higher implementation complexity.

### Option C: Pragmatic Balance (Managed Async Queue)
- Centralized `DebateEngine` managing an async pipeline.
- Synchronous context setting (Analyst) followed by parallel critique/security checks.
- Consensus aggregation as a final gated step.
- Pros: Good boundaries, handles parallel I/O, maintainable.
- Cons: Moderate effort.

## 3. Selected Option
**Option C: Pragmatic Balance** is recommended to leverage the async nature of LLM calls while maintaining a clear, auditable reasoning chain.

## 4. Implementation Details
- `AnalysisAgent`: Update to return structured JSON proposals.
- `CriticAgent`: Update to identify flaws in JSON proposals.
- New Agents: `SolutionAgent`, `SecurityAgent`, `OptimizerAgent`.
- `DebateEngine`: Orchestrate the flow and persist to `MemoryManager`.

## 5. Session Guide
- `agents/analysis_agent.py`
- `agents/critic_agent.py`
- `agents/solution_agent.py`
- `agents/security_agent.py`
- `agents/optimizer_agent.py`
- `debate/engine.py`
