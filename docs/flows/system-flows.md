---
title: "System Process Flows"
description: "Visual and structural mapping of the AI Workflow Orchestrator operations."
keywords: ["workflows", "process flow", "mermaid", "state machine"]
robots: "index, follow"
---

# System Process Flows

> **Quick Reference**
> - **Primary Flow**: The end-to-end "Mission" lifecycle.
> - **Decision Flow**: The Iterative Debate (Consensus 2.0) mechanism.
> - **Fault Tolerance**: Automatic model failover logic.

## 1. End-to-End Workflow Lifecycle

The global journey from a user's natural language request to a validated execution result.

```mermaid
graph TD
    User([User Request]) --> Memory[Memory Context Load]
    Memory --> Analysis[Analysis Agent: Plan DAG]
    Analysis --> Debate{Iterative Debate Loop}
    Debate -- Rejected --> End[Halt Workflow]
    Debate -- Approved --> Execution[Execution Engine: DAG Runner]
    Execution --> Parallel{Parallel Swarming}
    Parallel --> Agent1[CodingAgent]
    Parallel --> Agent2[CLIAgent]
    Agent1 --> Validation[Validation Agent]
    Agent2 --> Validation
    Validation --> Store[Store Results in Memory]
    Store --> Done([Validated Output Delivered])
```

**Description**: The lifecycle starts with context retrieval from SQLite, followed by DAG generation. The system then enters a mandatory debate gate before swarming specialized agents for task completion.

---

## 2. Iterative Debate (Consensus 2.0)

The reasoning engine that ensures technical feasibility and security.

```mermaid
stateDiagram-v2
    [*] --> Opening
    Opening --> Challenge: Proposal Generated
    Challenge --> Mitigation: Risks Identified
    Mitigation --> Challenge: Plan Revised
    Mitigation --> FinalVote: Risks Handled
    FinalVote --> Aggregation: Votes Cast
    Aggregation --> Approved: Score >= Threshold
    Aggregation --> Rejected: Veto or Low Score
    Approved --> [*]
    Rejected --> [*]
```

**Description**: A state-based transition where the Challenge phase can trigger multiple Mitigation cycles. Veto rights from Security or Critic agents can immediately transition the state to Rejected.

---

## 3. Model Failover Logic

The resilience mechanism implemented in the `ModelRouter`.

```mermaid
sequenceDiagram
    participant Agent
    participant Router as ModelRouter
    participant Primary as Gemini-2.5-Flash
    participant Fallback as Mistral-Large

    Agent->>Router: Execute(Prompt)
    Router->>Primary: Request
    Primary-->>Router: 429 Rate Limit / Error
    Note right of Router: failure_tracking_set(Primary)
    Router->>Router: Switch to Fallback Chain
    Router->>Fallback: Request
    Fallback-->>Router: 200 OK
    Router-->>Agent: Result (Success)
```

**Description**: When the primary model fails, the router logs the failure, sets a cooldown timer, and routes the next attempt to the fallback chain (Flash-Lite -> Flash -> Pro -> Mistral).

---

## See Also
- [Codebase Analysis](../analysis.md)
- [Jobs-to-be-Done](../jtbd/jobs-to-be-done.md)
