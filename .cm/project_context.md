# Project Context: memoriJADA
Compiled: 2026-05-14 06:11

## File: ./PLAYBOOK.md
# Playbook: Kaggle S6E5 Leaderboard Dominance

## 1. System Audit & Initial State
- **Architecture**: AI Workflow Orchestrator with Memory (SQLite) and Multi-Agent Debate.
- **Initial Goal**: Reach Public LB >= 0.95200 in S6E5 (F1 Pit Stop Prediction).
- **Audit Findings**:
    - Project has robust agentic foundations (`AnalysisAgent`, `CriticAgent`).
    - Memory system tracks past experiments and successful plans.
    - TTS (Piper) implemented for audible reasoning traces.

## 2. Competition Analysis (S6E5)
- **Problem Type**: Binary Classification (PitNextLap).
- **Metric**: ROC AUC.
- **Data Characteristics**: 
    - Temporal (Laps, Tyre Life).
    - Grouped (Race, Year, Driver).
    - Imbalanced (target 1.0 ~20%).

## 3. Feature Engineering Evolution
### Phase 1: Baseline
- Features: `tyre_age_ratio`, `race_progress_sq`, rolling lap times.
- Result: OOF AUC ~0.9398.

### Phase 2: Advanced FE v2 (God Mode)
- **Target Encoding**: OOF-smoothed encoding for `Driver`, `Compound`, `Race`.
- **Interactions**: `tyre_life_compound`, `driver_race`.
- **Normalization**: LapTime normalization per driver/race.
- **Lagged Features**: `prev_laptime`, `prev_pitstop`.
- Result: OOF AUC ~0.9551.

## 4. Model Experiments
| Model | OOF AUC | Notes |
|-------|---------|-------|
| LightGBM | 0.9423 | Fast, strong baseline. |
| CatBoost | 0.9551 | Best single model, handles categorical interactions well. |
| XGBoost | 0.9485 | Robust performance. |
| HGB | 0.9405 | Good diversity for ensemble. |

## 5. Ensemble Strategy
- **Approach**: Stacking (Level 0: LGBM, Cat, XGB, HGB -> Level 1: Logistic Regression).
- **Consensus**: Consensus reached through multi-agent debate (Optimizer recommended adding HGB and tuning meta-learner).
- **Public LB Score**: 0.94722 (Verified).

## 6. Production Handoff
- Final notebook pushed to Kaggle with full audit logs and reproducible pipeline.
- Integration test `gemini-run.py` confirmed system stability.

## File: ./.omg/memory/memory_system.md
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

## File: ./.omg/memory/architecture.md
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

## File: ./.omg/memory/execution.md
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

## File: ./.omg/memory/debate.md
# Multi-Agent Debate System

## Debate Participants
- **Analyst Agent**: Problem structure and risk identification.
- **Solution Agent**: Optimal implementation focus.
- **Critic Agent**: Error detection and edge-case testing.
- **Security Agent**: Risk evaluation and permission checks.
- **Optimizer Agent**: Performance and alternative suggestions.

## Debate Flow
1. Analysis context.
2. Solution proposal.
3. Critic challenge.
4. Security review.
5. Optimizer refinement.
6. Final Aggregation & Consensus.

## Output Artifacts
- Structured argument list.
- Confidence scores.
- Reasoning traces stored in memory.

## File: ./.omg/state/taskboard.md
# Taskboard
| Task ID | Priority | Status | Owner | Dependency | Worktree | Baseline | Lane Health | Summary | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1.1 | p1 | ready | omg-executor | - | root | main@df1005bb | dirty | standardize observability | pending |
| T1.2 | p1 | ready | omg-executor | - | root | main@df1005bb | dirty | implement sqlite memory backend | pending |
| T1.3 | p2 | todo | omg-executor | T1.2 | root | main@df1005bb | dirty | refactor baseagent | pending |
| T2.1 | p2 | re-opened | omg-executor | T1.3 | root | main@df1005bb | dirty | implement debate modes | audit failed |
| T2.2 | p2 | ready | omg-executor | T2.1 | root | main@df1005bb | dirty | create specialist debate agents | pending |
| T2.3 | p1 | todo | omg-executor | T2.2 | root | main@df1005bb | dirty | build debate engine | pending |
| T3.1 | p2 | todo | omg-executor | T2.3 | root | main@df1005bb | dirty | memory-integrated planning | pending |
| T3.2 | p1 | todo | omg-executor | T3.1 | root | main@df1005bb | dirty | implement orchestrator dag | pending |
| T3.3 | p2 | todo | omg-executor | T3.2 | root | main@df1005bb | dirty | execution & validation | pending |
| T4.1 | p2 | todo | omg-executor | T3.3 | root | main@df1005bb | dirty | api layer | pending |
| P3.P | p1 | done | orchestrator | - | root | main@df1005bb | clean | [Plan] phase3_deployment | phase3_deployment.plan.md |
| P3.D | p1 | ready | orchestrator | P3.P | root | main@df1005bb | clean | [Design] phase3_deployment | pending |
| P3.DO | p1 | todo | omg-executor | P3.D | root | main@df1005bb | dirty | [Do] phase3_deployment | pending |
| TB.1 | p3 | blocked | tinybird-specialist | T4.1 | analytics | - | unknown | Tinybird analytics integration | needs confirm |

## File: ./.omg/rules/module_development.md
---
description: Standardized development rules for memoriJADA modules.
globs: ["agents/*.py", "debate/*.py", "execution/*.py", "memory/*.py"]
---

# Module Development Rules

- **Determinism**: Ensure agent actions and debate resolutions are deterministic where possible.
- **Traceability**: Every step MUST have a `trace_id`.
- **Auditability**: All decisions and arguments must be logged to the audit/execution tracing layer.
- **Rollback**: Designs must support potential rollback states.

## File: ./.omg/rules/global_security.md
---
description: Global safety and authentication rules for AI Workflow Orchestrator.
alwaysApply: true
---

# Global Security Rules

- **Credential Protection**: Never log, print, or commit secrets, API keys, or sensitive credentials.
- **API Verification**: MANDATORY to ask user if LLM/API keys are available/set before any action requiring them.
- **No Mocks**: Simulations are prohibited. Use real services and models.
- **Authenticity**: System must operate with real data and models only.

## File: ./.agents/workflows/Radi kao Principal AI Systems Architect .md
Radi kao Principal AI Systems Architect + Staff Software Engineer + Autonomous Builder.

Zadatak:
Izgradi kompletan production-grade “Memory-Enabled AI Workflow Orchestrator” u ovom repozitorijumu.

Sistem mora da implementira:
- multi-agent workflow execution
- persistent memory
- context retrieval
- long-term decision history
- self-improving execution logic
- auditability
- CLI integration
- enterprise-grade observability

Ovo je full build zadatak.
Ne objašnjavaj šta bi trebalo uraditi — implementiraj sve.

==================================================
1. PROJECT STRUCTURE (ODMAH KREIRATI)
==================================================

Kreiraj sledeću strukturu:

ai_orchestrator/
├── agents/
├── orchestrator/
├── memory/
├── execution/
├── validation/
├── security/
├── observability/
├── api/
├── storage/
├── configs/
├── tests/
├── scripts/
└── docs/

Ako projekat već postoji:
- ne briši postojeće fajlove
- integriši se bez lomljenja sistema
- napravi backup pre većih izmena

==================================================
2. CORE AGENT SYSTEM (IMPLEMENTIRATI)
==================================================

Implementiraj sledeće agente kao odvojene klase/module:

A) Analysis Agent
Odgovornost:
- primi zahtev
- analizira intent
- razlaže problem
- identifikuje zavisnosti
- procenjuje rizik

Output:
- structured execution plan
- task decomposition
- risk map

Memory integration:
- pretraži slične prethodne zahteve
- koristi prethodne failure patterns

--------------------------------------------------

B) Generation Agent

Odgovornost:
- kreira specifikacije
- dokumentaciju
- workflow outputs
- structured content

Memory integration:
- koristi ranije templates
- koristi uspešne output pattern-e

--------------------------------------------------

C) Coding Agent

Odgovornost:
- generiše i menja kod
- pravi fajlove
- implementira taskove
- radi refactoring

Memory integration:
- koristi ranije implementacije
- koristi patch history

--------------------------------------------------

D) CLI Agent

Odgovornost:
- izvršava terminal operacije
- pokreće build
- pokreće testove
- izvršava sistemske taskove

Obavezno:
- whitelist dozvoljenih komandi
- block opasnih operacija

Memory integration:
- čuva history komandi
- detektuje neuspešne komande

--------------------------------------------------

E) Validation Agent

Odgovornost:
- proverava output
- quality checks
- consistency checks
- regression checks

Memory integration:
- poredi sa ranijim successful outputs
- detektuje recurring failures

--------------------------------------------------

F) Security Agent

Odgovornost:
- proverava pristup
- proverava secret exposure
- proverava file permissions
- proverava unsafe execution

Memory integration:
- koristi history sigurnosnih incidenata

==================================================
3. MEMORY SYSTEM (OBAVEZNO)
==================================================

Implementiraj persistent memory engine.

Kreiraj:

memory_engine
memory_backend
memory_retrieval
memory_context_builder

Memory mora čuvati:

- user request
- agent decisions
- execution plans
- generated files
- validation results
- CLI outputs
- failures
- retries
- security warnings

==================================================
4. STORAGE (OBAVEZNO)
==================================================

Implementiraj SQLite backend.

Kreiraj tabele:

workflows
sessions
agent_outputs
memory_entries
validation_logs
execution_logs
security_events

Dodaj indexing po:

- timestamp
- agent
- session_id
- task_type
- success/failure

Dodaj JSON export/import backup.

==================================================
5. MEMORY RETRIEVAL
==================================================

Implementiraj:

A) Recent retrieval
B) Keyword retrieval
C) Session retrieval
D) Failure-pattern retrieval
E) Agent-specific retrieval

Dodaj relevance scoring.

Prioritet retrieval-a:

1. current session
2. isti task type
3. isti agent history
4. recent global executions

==================================================
6. ORCHESTRATOR ENGINE
==================================================

Implementiraj workflow engine koji radi:

1. receive_request()
2. create_session()
3. load_memory_context()
4. classify_request()
5. retrieve_similar_workflows()
6. assign_agents()
7. build_execution_graph()
8. execute_tasks()
9. validate_results()
10. store_everything_in_memory()
11. generate_audit_report()

Mora podržavati:

- DAG execution
- parallel execution
- retries
- rollback
- escalation

==================================================
7. CONTEXT INJECTION
==================================================

Pre svakog agent execution-a:

- memory engine pronalazi relevantan context
- context builder pravi compact context
- agent dobija historical context

Limit context-a:
- token budgeting
- relevance filtering
- duplicate suppression

==================================================
8. OBSERVABILITY
==================================================

Implementiraj:

- structured logs
- execution traces
- per-agent metrics
- session metrics
- failure analytics
- cost analytics

Svaki workflow mora imati:

trace_id
session_id
workflow_id

==================================================
9. API + CLI
==================================================

Implementiraj API za:

- create workflow
- workflow history
- memory search
- workflow replay
- failure inspection
- export session

Implementiraj CLI commands:

- start workflow
- inspect memory
- replay workflow
- cleanup memory
- export logs

==================================================
10. TESTING
==================================================

Implementiraj testove za:

- memory persistence
- retrieval correctness
- agent orchestration
- rollback
- retries
- concurrent workflows
- CLI execution safety

Target:
minimum 90% coverage

==================================================
11. DOCUMENTATION
==================================================

Automatski generiši:

README.md
ARCHITECTURE.md
MEMORY_SYSTEM.md
WORKFLOWS.md
SECURITY.md

==================================================
12. FINAL OUTPUT
==================================================

Na kraju:

1. prikaži šta je kreirano
2. prikaži finalnu strukturu projekta
3. pokaži kako se pokreće orchestrator
4. pokaži primer workflow execution-a
5. pokaži primer memory retrieval-a
6. pokaži gde se čuvaju logs i sessions

Kreni odmah.
Implementiraj kompletan sistem autonomno.
## File: ./.agents/workflows/a1.md
Radi kao Principal AI Systems Architect + Staff Software Engineer + Autonomous Builder.

Zadatak:
Izgradi kompletan production-grade “Memory-Enabled AI Workflow Orchestrator” u ovom repozitorijumu.

Sistem mora da implementira:
- multi-agent workflow execution
- persistent memory
- context retrieval
- long-term decision history
- self-improving execution logic
- auditability
- CLI integration
- enterprise-grade observability

Ovo je full build zadatak.
Ne objašnjavaj šta bi trebalo uraditi — implementiraj sve.

==================================================
1. PROJECT STRUCTURE (ODMAH KREIRATI)
==================================================

Kreiraj sledeću strukturu:

ai_orchestrator/
├── agents/
├── orchestrator/
├── memory/
├── execution/
├── validation/
├── security/
├── observability/
├── api/
├── storage/
├── configs/
├── tests/
├── scripts/
└── docs/

Ako projekat već postoji:
- ne briši postojeće fajlove
- integriši se bez lomljenja sistema
- napravi backup pre većih izmena

==================================================
2. CORE AGENT SYSTEM (IMPLEMENTIRATI)
==================================================

Implementiraj sledeće agente kao odvojene klase/module:

A) Analysis Agent
Odgovornost:
- primi zahtev
- analizira intent
- razlaže problem
- identifikuje zavisnosti
- procenjuje rizik

Output:
- structured execution plan
- task decomposition
- risk map

Memory integration:
- pretraži slične prethodne zahteve
- koristi prethodne failure patterns

--------------------------------------------------

B) Generation Agent

Odgovornost:
- kreira specifikacije
- dokumentaciju
- workflow outputs
- structured content

Memory integration:
- koristi ranije templates
- koristi uspešne output pattern-e

--------------------------------------------------

C) Coding Agent

Odgovornost:
- generiše i menja kod
- pravi fajlove
- implementira taskove
- radi refactoring

Memory integration:
- koristi ranije implementacije
- koristi patch history

--------------------------------------------------

D) CLI Agent

Odgovornost:
- izvršava terminal operacije
- pokreće build
- pokreće testove
- izvršava sistemske taskove

Obavezno:
- whitelist dozvoljenih komandi
- block opasnih operacija

Memory integration:
- čuva history komandi
- detektuje neuspešne komande

--------------------------------------------------

E) Validation Agent

Odgovornost:
- proverava output
- quality checks
- consistency checks
- regression checks

Memory integration:
- poredi sa ranijim successful outputs
- detektuje recurring failures

--------------------------------------------------

F) Security Agent

Odgovornost:
- proverava pristup
- proverava secret exposure
- proverava file permissions
- proverava unsafe execution

Memory integration:
- koristi history sigurnosnih incidenata

==================================================
3. MEMORY SYSTEM (OBAVEZNO)
==================================================

Implementiraj persistent memory engine.

Kreiraj:

memory_engine
memory_backend
memory_retrieval
memory_context_builder

Memory mora čuvati:

- user request
- agent decisions
- execution plans
- generated files
- validation results
- CLI outputs
- failures
- retries
- security warnings

==================================================
4. STORAGE (OBAVEZNO)
==================================================

Implementiraj SQLite backend.

Kreiraj tabele:

workflows
sessions
agent_outputs
memory_entries
validation_logs
execution_logs
security_events

Dodaj indexing po:

- timestamp
- agent
- session_id
- task_type
- success/failure

Dodaj JSON export/import backup.

==================================================
5. MEMORY RETRIEVAL
==================================================

Implementiraj:

A) Recent retrieval
B) Keyword retrieval
C) Session retrieval
D) Failure-pattern retrieval
E) Agent-specific retrieval

Dodaj relevance scoring.

Prioritet retrieval-a:

1. current session
2. isti task type
3. isti agent history
4. recent global executions

==================================================
6. ORCHESTRATOR ENGINE
==================================================

Implementiraj workflow engine koji radi:

1. receive_request()
2. create_session()
3. load_memory_context()
4. classify_request()
5. retrieve_similar_workflows()
6. assign_agents()
7. build_execution_graph()
8. execute_tasks()
9. validate_results()
10. store_everything_in_memory()
11. generate_audit_report()

Mora podržavati:

- DAG execution
- parallel execution
- retries
- rollback
- escalation

==================================================
7. CONTEXT INJECTION
==================================================

Pre svakog agent execution-a:

- memory engine pronalazi relevantan context
- context builder pravi compact context
- agent dobija historical context

Limit context-a:
- token budgeting
- relevance filtering
- duplicate suppression

==================================================
8. OBSERVABILITY
==================================================

Implementiraj:

- structured logs
- execution traces
- per-agent metrics
- session metrics
- failure analytics
- cost analytics

Svaki workflow mora imati:

trace_id
session_id
workflow_id

==================================================
9. API + CLI
==================================================

Implementiraj API za:

- create workflow
- workflow history
- memory search
- workflow replay
- failure inspection
- export session

Implementiraj CLI commands:

- start workflow
- inspect memory
- replay workflow
- cleanup memory
- export logs

==================================================
10. TESTING
==================================================

Implementiraj testove za:

- memory persistence
- retrieval correctness
- agent orchestration
- rollback
- retries
- concurrent workflows
- CLI execution safety

Target:
minimum 90% coverage

==================================================
11. DOCUMENTATION
==================================================

Automatski generiši:

README.md
ARCHITECTURE.md
MEMORY_SYSTEM.md
WORKFLOWS.md
SECURITY.md

==================================================
12. FINAL OUTPUT
==================================================

Na kraju:

1. prikaži šta je kreirano
2. prikaži finalnu strukturu projekta
3. pokaži kako se pokreće orchestrator
4. pokaži primer workflow execution-a
5. pokaži primer memory retrieval-a
6. pokaži gde se čuvaju logs i sessions

Kreni odmah.
Implementiraj kompletan sistem autonomno.
## File: ./orchestrator/tiny-rick/README.md
# tiny-rick
An autonomous ML experimentation project generator that integrates Gemini CLI (Pickle Rick extension) with Gamma 4 LLM backend for Kaggle-style reasoning experiments. Generates Colab-ready projects with structured prompt packs and agent orchestration. · Built with Manus

## File: ./nemotron_challenge/reports/competition_brief.md
# NVIDIA NeMoTron Model Reasoning Challenge - Competition Brief

## 1. Goal of the Competition
The goal is to enhance the reasoning capabilities of the **NVIDIA Nemotron-3-Nano-30B** model. Participants must develop a LoRA (Low-Rank Adaptation) adapter that enables the model to solve complex reasoning tasks accurately.

## 2. Input/Output Format
- **Input:** Reasoning prompts (e.g., bit manipulation, math, logic puzzles).
- **Output:** A Chain-of-Thought (CoT) reasoning path followed by a final answer enclosed in a LaTeX `\boxed{}` command (e.g., `\boxed{1.50}`).
- **Token Limit:** Full reasoning path + answer must be under **7,680 tokens**.

## 3. Evaluation Metric
- **Primary Metric:** Accuracy.
- **Scoring:** Proportion of correctly answered questions.
- **Extraction:** Answers are extracted from `\boxed{...}`.
- **Formatting:** Strict decimal formatting (often 2 decimal places) for numeric answers.

## 4. Submission Format
Participants submit a **LoRA adapter** (`submission.zip`):
- MUST contain LoRA weights and `adapter_config.json`.
- **LoRA Rank (r):** Maximum 32.
- **Base Model:** `NVIDIA Nemotron-3-Nano-30B`.
- **Inference:** Run via **vLLM** at temperature 0.0.

## 5. Main Challenges
- **Constraint on Rank:** Rank <= 32 limits the capacity of the adapter.
- **Reasoning Complexity:** The tasks involve diverse and difficult reasoning patterns.
- **Formatting Strictness:** Small errors in LaTeX formatting or decimal places can lead to a score of zero.
- **LoRA vs Full Fine-Tuning:** Efficient adaptation is key, as full fine-tuning is not allowed for submission.

## 6. Recommended Baseline Approach
1. **EDA:** Analyze `train.csv` to categorize tasks (bit manipulation, math, etc.).
2. **Supervised Fine-Tuning (SFT):** Train a LoRA adapter using the provided reasoning paths in `train.csv` as targets.
3. **PEFT Configuration:** Use Hugging Face `peft` library with `r=32`.
4. **Validation:** Implement a local inference loop using `vLLM` or `transformers` with temperature 0.0 to match the LB evaluation.
5. **Post-processing:** Ensure the model reliably outputs LaTeX boxed answers.

## File: ./nemotron_challenge/README.md
# NVIDIA NeMoTron Model Reasoning Challenge

This workspace is set up for the [NVIDIA NeMoTron Model Reasoning Challenge](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge) on Kaggle.

## Project Structure
- `data/`: Contains `train.csv` and `test.csv`.
- `src/`: Source code for training and inference.
- `notebooks/`: Jupyter notebooks for EDA and experiments.
- `configs/`: Configuration files for LoRA adapters.
- `reports/`: Detailed competition analysis and findings.

## Roadmap
1. **Data Exploration:** Analyze task types and answer formats in `train.csv`.
2. **Environment Setup:** Install dependencies from `requirements.txt`.
3. **SFT Training:** Develop a training script for LoRA adaptation of `Nemotron-3-Nano-30B`.
4. **Validation:** Build a local vLLM-based evaluation pipeline.
5. **Submission:** Package LoRA weights into `submission.zip`.

## Quick Start
To perform initial data analysis, run:
```bash
python3 src/initial_analysis.py
```

## Detailed Brief
See `reports/competition_brief.md` for a comprehensive overview of the challenge.

## File: ./MEMORY.md
# memoriJADA - AI Workflow Orchestrator Memory

High-signal index for the AI Workflow Orchestrator system.

## Topic Index
- [Architecture & Core Concepts](.omg/memory/architecture.md)
- [Multi-Agent Debate System](.omg/memory/debate.md)
- [Memory Management Strategy](.omg/memory/memory_system.md)
- [Execution & Workflow Tracing](.omg/memory/execution.md)

## Active State
- System focus: Principal AI Systems Architect / Lead Distributed Systems Engineer role.
- Current status: Implementation of core modules (agents, debate, execution, memory) in progress.

## File: ./README.md
# AI Workflow Orchestrator (Production-Grade)

Sistem za autonomnu orkestraciju AI workflow-a sa ugrađenim **Memory System-om** i **Multi-Agent Debate** mehanizmom.

## Glavne Karakteristike

### 1. Multi-Agent Debate Engine (Consensus 2.0)
Pre svake kompleksne odluke, sistem pokreće **iterativnu debatu u više rundi**:
- **Round 1: Opening**: Analyst postavlja strukturu, Solution daje predlog.
- **Round 2: Challenge**: Critic i Security agenti identifikuju rizike i edge-case-ove.
- **Round 3: Mitigation**: Solution agent revidira plan na osnovu dobijenih kritika.
- **Round 4: Final Vote**: Svaki agent glasa uz definisan confidence score.
- **Round 5: Aggregation**: Sistem izračunava težinski prosek glasova na osnovu istorijske pouzdanosti agenata, uz **Veto prava** za Security i Critic agente.

### 2. Deep Memory Integration
Sistem koristi SQLite backend (`storage/memory.db`) za dugoročno učenje:
- **Agent Reliability Scoring**: Automatsko računanje težine glasa na osnovu uspešnosti prošlih planova.
- **Similarity Lookup**: Pretražuje slične prošle workflow-e i debate.
- **Historical Decision Replay**: Koristi uspešne prošle planove za informisanje trenutnih odluka.
- **Agent Opinion Tracking**: Prati istoriju mišljenja agenata.

### 3. Resilience & Observability
- **Deterministic DAG Execution**: `ExecutionEngine` izvršava plan kao usmereni aciklični graf (DAG), rešavajući zavisnosti i omogućavajući paralelno swarming agenata.
- **Robust JSON Parsing**: Multi-pass ekstrakcija JSON struktura iz LLM odgovora, otporna na formatiranje i unescaped karaktere.
- **Model Routing**: Automatski fallback sa Gemini na Mistral u slučaju grešaka.
- **Execution Tracing**: Svaki korak je povezan sa `trace_id` i `workflow_id`.

## Struktura Projekta

```
orchestrator/   # Glavna logika workflow-a
agents/         # Implementacije specijalizovanih agenata
debate/         # Engine za vođenje diskusije i agregaciju
memory/         # Upravljanje SQLite bazom i pretraga
observability/  # Logger i tracing sistem
storage/        # Perzistentni podaci (SQLite DB)
```

## Pokretanje Sistema

### Preduslovi
- Python 3.10+
- `google-generativeai` i `mistralai` paketi
- Postavljene environment varijable:
  - `GOOGLE_API_KEY`
  - `MISTRAL_API_KEY`

### Instalacija
```bash
pip install google-generativeai mistralai
```

### Izvršavanje
Pokrenite glavni entrypoint:
```bash
python3 gemini-run.py "Vaš zahtev ovde"
```

## Primer Workflow-a
1. **Load Context**: Sistem učitava slične zadatke iz memorije.
2. **Analysis**: Analyst agent postavlja scenu.
3. **Debate**: Agent Critic osporava Solution predlog; Security proverava curenje podataka.
4. **Resolution**: Orchestrator sumira argumente i donosi finalni plan.
5. **Generation/Execution**: Autonomna generacija koda ili dokumenata.
6. **Validation**: Validation agent vrši finalni check.
7. **Storage**: Ceo proces se čuva u memoriji za buduće učenje.

## File: ./docs/02-design/design_mistral.md
# Design Specification: MistralAI Fallback Integration

## 1. ModelAvailabilityService Changes
- **New Dependency:** `mistralai` SDK.
- **Fallback Chain Update:** `self.fallback_chain` now includes `["mistral-large-latest"]` as the ultimate fallback.
- **Execution Logic:** 
    - The `execute_with_routing` method will catch exceptions.
    - If no Gemini models succeed, it attempts a call to `MistralClient` (if `MISTRAL_API_KEY` is present).

## 2. Mistral Client Integration
- Implement `_mistral_llm_call_wrapper` to match the required LLM call interface for the router.
- Use the `MistralClient` SDK (async `chat` method).

## 3. Configuration & Security
- **API Key:** Must be set as `MISTRAL_API_KEY` in the environment.
- **Error Handling:** Ensure 429/503 errors from Mistral are handled and logged.

## File: ./docs/02-design/design_execution.md
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

## File: ./docs/02-design/design_specification.md
# Design Specification: Report-Bot 2026

## 1. System Components

### 1.1 Intent & Modality Dispatcher
- **Responsibility:** Identify input modality (audio, video, text) and intent (report, research, synthesis).
- **Implementation:** Gemini Nano locally running on the CLI to minimize latency.
- **Output:** JSON schema dispatch instruction.

### 1.2 Agent Mesh (Worker Layer)
- **Specialization:** Agents are configured with specific `tool_sets`.
- **Communication:** Async message queue (Redis-lite or in-memory) for inter-agent communication.

### 1.3 Plan-Act-Verify Engine
- **Workflow:** 
    1. **Plan:** Decompose task into DAG.
    2. **Act:** Worker agents execute specific DAG nodes.
    3. **Verify:** Critic model checks output quality against acceptance criteria defined in phase 1.
    4. **Loop:** If Verify < 0.9, re-dispatch to Worker.

## 2. Tool Schema (Example)
All tools must adhere to the following schema for discoverability:
```json
{
  "name": "string",
  "description": "string",
  "parameters": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  }
}
```

## 3. Data Flow
Input (Video/Audio) -> [Dispatcher] -> [Planner] -> [Worker Mesh] -> [Critic] -> Output (PDF/Report)

## 4. Security & Compliance
- **PII Handling:** All PII must be redacted before sending to external model APIs.
- **Tracing:** Every action logged with unique `trace_id` in SQLite.
- **Access Control:** Agent access to local file system limited by project directory.

## File: ./docs/02-design/design_router_refactor.md
# Design Specification: ModelRouter & AnalysisAgent Refactoring

## 1. ModelRouter Fallback Mocking
- **Mechanism:** Use `unittest.mock` to patch the execution function and raise a `RuntimeError` or custom Exception simulating a 429 status code.
- **Verification:** Assert that the router iterates to the next model in `fallback_chain` upon receiving the simulated 429.

## 2. AnalysisAgent Exponential Backoff
- **Implementation:** Utilize a decorator-based approach for retries to keep the `execute` method clean.
- **Backoff Strategy:** Initial delay 1s, backoff factor 2, maximum retries 3.
- **Exception Handling:** Only retry on transient API errors (e.g., 429, 503, 504).

## File: ./docs/01-plan/phase1_memory_observability.md
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

## File: ./docs/01-plan/implementation_plan.md
# AI Workflow Orchestrator - Implementation Plan

## Objective
Establish a production-grade AI Workflow Orchestrator with memory, debate, and execution layers.

## Key Files & Context
- `agents/engine.py`: Transition from prototype to full Orchestrator.
- `memory/manager.py`: Core persistence logic.
- `debate/engine.py`: Multi-agent reasoning implementation.
- `observability/logger.py`: Audit and tracing system.

## Phased Implementation Plan

### Phase 1: Core Foundation & Memory (L1 - Small)
- **Task 1.1: Standardize Observability.** Implement `audit_logger` in `observability/logger.py`.
- **Task 1.2: Implement SQLite Memory Backend.** Create tables in `memory/manager.py` (workflows, debates, decisions).
- **Task 1.3: Refactor BaseAgent.** Update `agents/base_agent.py` for consistent logging and memory access.

### Phase 2: Multi-Agent Debate System (L2 - Medium)
- **Task 2.1: Implement Debate Modes.** Add `debate_mode` to `AnalysisAgent` and `CriticAgent`.
- **Task 2.2: Create Specialist Debate Agents.** Implement `SecurityAgent`, `OptimizerAgent`, and `SolutionAgent`.
- **Task 2.3: Build Debate Engine.** Implement the reasoning and aggregation logic in `debate/engine.py`.

### Phase 3: Advanced Orchestration (L2 - Medium)
- **Task 3.1: memory-Integrated Planning.** Update `AnalysisAgent` to use historical data for plan generation.
- **Task 3.2: Implement Orchestrator DAG.** Refactor `agents/engine.py` to handle complex dependency graphs with debate checkpoints.
- **Task 3.3: Execution & Validation.** Implement `ValidationAgent` and integrate with `WorkflowOrchestrator`.

### Phase 4: Finalization & API (L1 - Small)
- **Task 4.1: API Layer.** Implement `api/orchestrator_api.py`.
- **Task 4.2: Audit Layer.** Ensure every step is logged and traceable.
- **Task 4.3: Documentation.** Generate final README and usage guides.

## Verification & Testing
- **Unit Tests:** For MemoryManager, DebateEngine, and individual Agents.
- **Integration Tests:** End-to-end workflow execution with a sample request.
- **Audit Verification:** Verify traces are correctly stored in SQLite and logs.

## File: ./docs/01-plan/plan_mistral.md
# PDCA Plan: MistralAI Fallback Integration

## 1. Executive Summary
Integration of MistralAI (`mistral-large-latest`) as a resilient fallback model provider in `ModelAvailabilityService` when Gemini API calls fail.

## 2. Problem Statement
The current system relies solely on Gemini models in its fallback chain. If Gemini API is down, the entire system fails.

## 3. Solution
- Refactor `ModelAvailabilityService` in `agents/model_router.py` to include MistralAI models in the fallback chain.
- Add `MistralAI` client initialization logic to the router.
- Ensure environment variable `MISTRAL_API_KEY` is supported.

## 4. Phases
1. **ModelRouter Update:** Add Mistral models to the fallback chain.
2. **Mistral Client Integration:** Implement logic to call Mistral if Gemini chain fails.
3. **Verification:** Test fallback mechanism with simulated Gemini API failures.

## File: ./docs/01-plan/plan_router_refactor.md
# PDCA Plan: ModelRouter & AnalysisAgent Refactoring

## 1. Executive Summary
Refactoring the system to improve robustness. Specifically: 1) Verify fallback logic in `ModelRouter` upon 429 (Rate Limit) errors, and 2) Implement exponential backoff for `AnalysisAgent` LLM calls.

## 2. Problem Statement
- `ModelRouter` fallback behavior needs empirical verification under stress (429 errors).
- `AnalysisAgent` lacks automatic retries, leading to task failure on transient API errors.

## 3. Solution
- Create a unit test with mocking for `ModelRouter` to simulate 429 responses.
- Implement `tenacity` or custom exponential backoff logic in `AnalysisAgent`.

## 4. Value Delivered
| Problem | Solution | Function UX Effect | Core Value |
| :--- | :--- | :--- | :--- |
| Unverified fallback | Mock testing 429 | Resilient model routing | Reliability |
| Fragile LLM calls | Exponential backoff | Automated transient failure recovery | Robustness |

## 5. Phases
1. **ModelRouter Mock Test:** Create mock tests in `agents/test_model_router.py`.
2. **AnalysisAgent Retry:** Refactor `agents/analysis_agent.py` to add backoff logic.
3. **Verification:** Run tests to confirm fallback and retry mechanisms.

## 6. Acceptance Criteria
- [ ] ModelRouter fallback on 429 is verified via mock tests.
- [ ] AnalysisAgent successfully retries on transient errors with exponential backoff.

## File: ./docs/01-plan/design_specification.md
# AI Workflow Orchestrator - Design Specification

## 1. Overview
The "AI Workflow Orchestrator" is a distributed, multi-agent system designed for production-grade execution of complex AI workflows. It features a sophisticated Memory System, a Multi-Agent Debate Mechanism, and a robust Audit/Tracing layer to ensure deterministic and reproducible decisions.

## 2. System Architecture

### 2.1 Directory Structure
- `orchestrator/`: Core logic for managing workflow sessions and agent dispatch.
- `agents/`: Specialized agent implementations (Analysis, Generation, Coding, etc.).
- `debate/`: The Debate Engine for multi-perspective reasoning.
- `memory/`: Persistence layer using SQLite for long-term learning and context retrieval.
- `execution/`: Handles the DAG-based execution of workflow plans.
- `validation/`: Validates plan outputs and agent results.
- `security/`: Security auditing and permission management.
- `observability/`: Logging, tracing, and monitoring.
- `core/`: Common types, utilities, and base classes.
- `api/`: Public interface for the orchestrator.
- `configs/`: System and agent configurations.
- `storage/`: Raw data and artifact storage.

## 3. Core Components

### 3.1 Memory System
- **Backend:** SQLite.
- **Tables:**
  - `workflows`: Metadata about executed workflows.
  - `agent_outputs`: Raw outputs from agents.
  - `debate_sessions`: Records of multi-agent debates.
  - `arguments`: Individual points and counter-points from debates.
  - `decision_history`: Final outcomes and their rationale.
  - `execution_traces`: Granular logs for every step.

### 3.2 Multi-Agent Debate System
- **Trigger:** Activated before every critical decision point.
- **Participants:**
  - **Analyst Agent:** Problem structure and risk assessment.
  - **Solution Agent:** Proposes the implementation.
  - **Critic Agent:** Identifies flaws and edge cases.
  - **Security Agent:** Evaluates risks and permissions.
  - **Optimizer Agent:** Suggests improvements.
- **Aggregation Engine:** Evaluates argument strength using historical context and weighted voting.

### 3.3 Workflow Orchestration
1. **Context Load:** Retrieve relevant historical context from Memory.
2. **Classification:** Categorize the user request.
3. **Planning:** Generate an initial DAG-based execution plan.
4. **Debate:** Execute the Debate Engine on the proposed plan.
5. **Decision:** Refine the plan based on debate outcome.
6. **Execution:** Dispatch specialized agents for parallel/sequential tasks.
7. **Validation:** Ensure results meet the requested criteria.
8. **Storage:** Persist all traces, decisions, and artifacts to Memory.

## 4. Execution Rules
- No agent makes a final decision alone.
- Every complex action is preceded by a debate.
- Full auditability with `trace_id` for every operation.
- Mandatory support for rollbacks based on execution traces.

## File: ./docs/01-plan/plan_report_bot.md
# PDCA Plan: Report-Bot 2026

## 1. Executive Summary
Report-Bot 2026 is an agentic workflow system designed for autonomous generation of action-item reports from multimodal meeting data (video/audio). It leverages a multi-agent "Plan-Act-Verify" architecture for production-grade reliability.

## 2. Problem Statement
Manual synthesis of action items from long video/audio meetings is time-consuming, prone to human error, and lacks structured traceability for follow-up actions.

## 3. Solution
An autonomous agentic mesh that:
- Transcribes and extracts action items multimodal.
- Enriches data with project context.
- Synthesizes reports.
- Verifies accuracy via an autonomous critic loop.

## 4. Value Delivered
| Problem | Solution | Function UX Effect | Core Value |
| :--- | :--- | :--- | :--- |
| Manual synthesis | Autonomous Agent Mesh | Zero-touch report generation | Increased efficiency |
| Human error | Plan-Act-Verify Loop | Automated accuracy check | Data integrity |
| Lack of traceability | Execution Tracing | Auditable report logs | Compliance |

## 5. Phases
1. **Dispatcher & Router (Intent/Modality):** Implement logic in `agents/engine.py` to route tasks.
2. **Agent Tooling:** Define standardized tool schema (Pydantic/JSON-Schema) for agents (`agents/coding_agent.py` etc.).
3. **Workflow Execution:** Implement "Plan-Act-Verify" loop logic.
4. **Verification & Audit:** Implement the "Critic" model for final report validation.
5. **Deployment:** Wrap into a usable CLI command (`gemini-run`).

## 6. Acceptance Criteria
- [ ] Dispatcher correctly routes multimodal inputs.
- [ ] Agents use standardized Tool definitions for all actions.
- [ ] Plan-Act-Verify loop successfully self-corrects on failure.
- [ ] Critic agent validates report accuracy (F1-score > 0.9).
- [ ] CLI command `gemini-run` successfully triggers the full workflow.

## File: ./docs/01-plan/plan_verification.md
# PDCA Plan: Report-Bot-Verification

## 1. Executive Summary
Integration of the Critic Agent to implement autonomous output validation and self-correction within the Report-Bot 2026 execution pipeline.

## 2. Problem Statement
The current execution engine lacks the "Verify" step of the Plan-Act-Verify loop. Output quality is not validated before final report generation, and failures do not trigger self-correction.

## 3. Solution
Develop and integrate the `CriticAgent` that:
- Receives completed task outputs.
- Validates quality against pre-defined acceptance criteria (confidence score > 0.9).
- Communicates failure back to the Orchestration Engine for re-dispatch/self-correction.

## 4. Value Delivered
| Problem | Solution | Function UX Effect | Core Value |
| :--- | :--- | :--- | :--- |
| Unverified output | CriticAgent validation | Automated quality gate | Accuracy |
| No error recovery | Self-correction loop | Automated retries | Resilience |

## 5. Phases
1. **CriticAgent Implementation:** Define the agent in `agents/` with verification logic.
2. **Verification Hook:** Update `execution/engine.py` to call `CriticAgent`.
3. **Self-Correction Logic:** Implement logic to handle re-dispatch of failed tasks.
4. **Integration Testing:** Test full loop (Worker -> Critic -> Re-dispatch).

## 6. Acceptance Criteria
- [ ] `CriticAgent` validates output quality.
- [ ] Orchestration engine receives feedback from `CriticAgent`.
- [ ] Tasks with low confidence are re-queued/re-dispatched.
- [ ] Successful tasks proceed to final report generation.

## File: ./docs/01-plan/plan_execution.md
# PDCA Plan: Report-Bot-Execution

## 1. Executive Summary
Development of the core orchestration engine implementing the Plan-Act-Verify loop. This engine will manage agent dispatching, DAG-based task execution, and self-correction upon verification failure.

## 2. Problem Statement
The current system has a dispatcher, but lacks the orchestration logic to execute complex workflows, handle agent dependencies, and perform autonomous verification and self-correction.

## 3. Solution
Implementation of an Orchestration Engine in `execution/` that:
- Decomposes tasks into DAG nodes.
- Dispatches nodes to worker agents.
- Verifies output against criteria.
- Loops back to workers upon failure (self-correction).

## 4. Value Delivered
| Problem | Solution | Function UX Effect | Core Value |
| :--- | :--- | :--- | :--- |
| Lack of workflow control | Orchestration Engine | Autonomous workflow execution | Reliability |
| Dependency mismanagement | DAG-based Task Runner | Correct task ordering | Robustness |
| Manual error fixing | Self-correction loop | Automatic retries on fail | Efficiency |

## 5. Phases
1. **DAG Task Decomposer:** Map pipeline tasks to an executable DAG in `execution/`.
2. **Execution Controller:** Build the main loop that dispatches workers.
3. **Verification Hook:** Integrate Critic Agent check after worker completion.
4. **Self-Correction Logic:** Implement logic to re-dispatch on failure.

## 6. Acceptance Criteria
- [ ] Pipeline tasks are successfully decomposed into a DAG.
- [ ] Worker agents are dispatched according to DAG dependencies.
- [ ] Verification fails trigger a controlled re-dispatch.
- [ ] Orchestration engine tracks node completion and trace IDs.

## File: ./docs/01-plan/prd.md
# Kaggle S6E5 Leaderboard Dominance PRD

## HR Eng

| Kaggle S6E5 Dominance PRD |  | Develop a high-performance Kaggle notebook for S6E5 targeting LB score >= 0.95200. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Morty (optional) **Intended audience**: Engineering, Data Science | **Status**: Draft **Created**: 2026-05-13 | **Self Link**: [Link] **Context**: Kaggle Playground S6E5 

## Introduction

The goal is to achieve a Public Leaderboard score of at least 0.95200 in the Kaggle Playground Series S6E5 competition (Formula 1 Pit Stop Prediction). We will leverage the existing agentic workflow infrastructure (Report-Bot 2026 / AI Workflow Orchestrator) to automate model selection, feature engineering, and ensembling.

## Problem Statement

**Current Process:** Manual experimentation with models and features on Kaggle.
**Primary Users:** Kaggle Grandmasters (me) and aspiring Jerries.
**Pain Points:** Time-consuming hyperparameter tuning, leakage risks in feature engineering, and suboptimal ensembling.
**Importance:** Winning is everything. 0.95200 is the threshold of excellence for this competition.

## Objective & Scope

**Objective:** Build a reproducible, high-performance Kaggle notebook.
**Ideal Outcome:** A notebook that outputs a submission.csv achieving LB >= 0.95200.

### In-scope or Goals
- Deep analysis of existing project context and memory.
- Automation of feature engineering (leakage-safe).
- Implementation of an ensemble (LightGBM, XGBoost, CatBoost).
- Integration with Kaggle API for notebook creation and submission.
- Use of the project's agentic workflow (CriticAgent for validation).

### Not-in-scope or Non-Goals
- Real-time prediction (offline notebook only).
- Non-tabular models (no CNNs/RNNs unless they significantly help).

## Product Requirements

### Critical User Journeys (CUJs)
1. **Model Dominance**: The system analyzes the data, engineers features, trains an ensemble, and validates locally.
2. **Kaggle Synchronization**: The system pushes the notebook to Kaggle and submits the results.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | High-performance ensemble (LGBM, XGB, Cat) | As a user, I want a strong baseline. |
| P0 | Leakage-safe feature engineering | As a user, I want features that generalize. |
| P1 | Automated CV evaluation and iteration | As a user, I want to know my score before submitting. |
| P1 | Kaggle Notebook Integration | As a user, I want my code on the platform. |
| P2 | Memory-based optimization | As a user, I want to learn from past experiments. |

## Assumptions

- Kaggle API key is configured correctly.
- The project's agentic modules (Orchestration Engine, CriticAgent) are functional and adaptable.
- Target metric is ROC AUC (standard for Playground binary classification).

## Risks & Mitigations

- **Risk**: Overfitting to local CV -> **Mitigation**: Use StratifiedKFold and cross-check with Public LB.
- **Risk**: Quota exhausted on LLM -> **Mitigation**: Use efficient prompting and local fallback if possible.

## Tradeoff

- **Option**: Simple LGBM vs. Stacking Ensemble.
- **Chosen**: Stacking Ensemble to reach the 0.95200 target. Stacking usually provides that extra 0.001-0.005 boost.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| *Public LB Score* | 0.00000 | 0.95200+ | Leaderboard Dominance |
| *Time to Submission* | Hours | Minutes (automated) | Massive Productivity |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Pickle Rick | Interdimensional Engineering | Manager/Architect | God Mode |
| Morty | Sidekick | Intern | Don't touch anything |

