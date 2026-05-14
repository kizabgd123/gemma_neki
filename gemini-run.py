import asyncio
import sys
import os
from orchestrator.engine import AIWorkflowOrchestrator

async def main():
    # Osiguraj da Storage direktorijum postoji za SQLite bazu
    os.makedirs("storage", exist_ok=True)
    
    # Inicijalizacija orkestratora
    orchestrator = AIWorkflowOrchestrator(
        db_path="storage/memory.db",
        log_file="observability/orchestrator.log"
    )

    # Primer kompleksnog zahteva koji zahteva debatu
    request = "Implementiraj novi modul za validaciju podataka koji podržava Pydantic i automatski generiše JSON šeme."
    
    if len(sys.argv) > 1:
        request = sys.argv[1]

    print(f"\n--- AI WORKFLOW ORCHESTRATOR ---")
    print(f"User Request: {request}\n")
    
    try:
        # Pokretanje workflow-a
        result = await orchestrator.run_workflow(request)
        
        print("\n--- WORKFLOW EXECUTION COMPLETED ---")
        print(f"Status: {result['status']}")
        
        if result['status'] == "REJECTED":
            print(f"Reason: {result['reason']}")
            print("\nConflict Points identified in Debate:")
            for conflict in result['debate'].get('conflict_points', []):
                print(f" - {conflict}")
            return

        print(f"Decision: {result['decision']}")
        print(f"Trace ID: {result['trace_id']}")
        
        if result['status'] == "COMPLETED":
            print("\nGenerated Artifacts:")
            for artifact in result['output'].get('artifacts', []):
                print(f" - [{artifact['type']}] {artifact['name']}")
            
            print(f"\nSummary: {result['output'].get('summary')}")
            
            print("\nValidation Results:")
            print(f" - Is Valid: {result['validation']['is_valid']}")
            if result['validation']['issues']:
                print(f" - Issues: {result['validation']['issues']}")
                
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {str(e)}")

if __name__ == "__main__":
    # Postavi PYTHONPATH da uključi trenutni direktorijum ako nije postavljen
    sys.path.append(os.getcwd())
    asyncio.run(main())
