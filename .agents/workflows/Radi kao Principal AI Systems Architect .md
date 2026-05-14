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