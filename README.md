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
