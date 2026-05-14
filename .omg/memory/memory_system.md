# Memory Management Strategy

## Memory Tiers
- **Sensory (Ephemeral)**: In-session transient variables and tool outputs.
- **Working (Short-term)**: `MEMORY.md` and active context files.
- **Long-term (Persistent)**: SQLite backend (`storage/test_memory.db`) for historical decisions and debate traces.

## Schema Focus
- `debates`: Full history of debate sessions.
- `arguments`: Structured agent positions and counter-arguments.
- `decision_history`: Traceable decision log with `trace_id`.
- `agent_opinion_history`: Long-term tracking of agent behavior and conflict points.

## Retrieval & Search
- Similarity lookup for past workflows and debates.
- Historical decision replay for consistency checking.
