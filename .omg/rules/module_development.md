---
description: Standardized development rules for memoriJADA modules.
globs: ["agents/*.py", "debate/*.py", "execution/*.py", "memory/*.py"]
---

# Module Development Rules

- **Determinism**: Ensure agent actions and debate resolutions are deterministic where possible.
- **Traceability**: Every step MUST have a `trace_id`.
- **Auditability**: All decisions and arguments must be logged to the audit/execution tracing layer.
- **Rollback**: Designs must support potential rollback states.
