---
title: "Jobs-to-be-Done (JTBD)"
description: "Core jobs and desired outcomes for the AI Workflow Orchestrator users."
keywords: ["jtbd", "user goals", "outcomes", "jobs framework"]
robots: "index, follow"
---

# Jobs-to-be-Done (JTBD)

> **Quick Reference**
> - **Core Job**: Delegate complex, multi-step AI reasoning and execution to a reliable system.
> - **Alignment**: Mapping user intent to deterministic system outcomes.

## Alex, the Principal AI Architect

| Job Statement | System Feature | Frequency | Importance |
|---------------|----------------|-----------|------------|
| **When** starting a complex task, **I want** a multi-agent debate, **so I can** ensure the plan is reviewed for security and efficiency before execution. | Iterative Debate Engine | Daily | High |
| **When** a plan is approved, **I want** the system to execute tasks in parallel, **so I can** reduce time-to-delivery without manual intervention. | DAG Execution Engine | Daily | High |
| **When** an error occurs in a long chain, **I want** a full reasoning trace, **so I can** identify exactly which agent or model failed and why. | Execution Tracing | On Error | Critical |

---

## Jordan, the MLOps Specialist

| Job Statement | System Feature | Frequency | Importance |
|---------------|----------------|-----------|------------|
| **When** a model hits a rate limit, **I want** an automatic failover to a fallback model, **so I can** maintain system uptime. | Model Availability Service | High | Critical |
| **When** the system runs multiple swarms, **I want** unified structured logs, **so I can** monitor performance and resource usage at scale. | Structured Logging | Daily | Medium |

---

## Sam, the Kaggle Grandmaster

| Job Statement | System Feature | Frequency | Importance |
|---------------|----------------|-----------|------------|
| **When** competing in a tabular competition, **I want** the system to use "God-Mode" feature engineering from past experiments, **so I can** hit high LB scores faster. | Memory System (Similarity Lookup) | Project-based | High |
| **When** designing an ensemble, **I want** a consensus-based model stacking recommendation, **so I can** choose the most diverse and robust model set. | Multi-Agent Debate (Optimizer) | Weekly | High |

---

## Desired Outcomes
- **Reliability**: 0% silent failures due to malformed JSON.
- **Traceability**: 100% of actions linked to a unique `trace_id`.
- **Efficiency**: Parallel execution of independent tasks in a DAG.

## See Also
- [User Personas](../personas/user-personas.md)
- [Process Flows](../flows/system-flows.md)
