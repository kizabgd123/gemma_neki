"""
TTSMiddleware — middleware za automatski TTS output iz Orchestratora i DebateEngine-a.

Koristi se kao mixin ili wrapper oko postojećih klasa.
"""

import functools
import logging
from typing import Callable, Optional
from tts_audio_router import AudioRouter

logger = logging.getLogger(__name__)


class TTSMiddleware:
    """
    Middleware koji dodaje TTS notifikacije na svaki ključni korak sistema.

    Primer integracije u Orchestrator:
        class MyOrchestrator:
            def __init__(self, ...):
                self.tts = TTSMiddleware(router=AudioRouter.from_config(config))

            def execute_workflow(self, workflow):
                self.tts.on_workflow_start(workflow.name)
                # ... logika ...
                self.tts.on_workflow_complete(workflow.name, result)

    Ili kao dekorator:
        @TTSMiddleware.tts_step("load_memory_context")
        def load_memory_context(self):
            ...
    """

    def __init__(self, router: Optional[AudioRouter] = None):
        self.router = router or AudioRouter(fallback_to_print=True)

    # ── Workflow eventi ───────────────────────────────────────────────────────

    def on_workflow_start(self, workflow_name: str) -> None:
        self.router.workflow_step(workflow_name, "started")

    def on_workflow_complete(self, workflow_name: str, result: str = "") -> None:
        self.router.workflow_step(workflow_name, "completed")
        if result:
            self.router.route("workflow", f"Rezultat: {result[:120]}")

    def on_workflow_failed(self, workflow_name: str, error: str = "") -> None:
        self.router.workflow_step(workflow_name, "failed")
        if error:
            self.router.error(f"Detalji greške u '{workflow_name}': {error[:100]}")

    def on_step_start(self, step_name: str) -> None:
        self.router.workflow_step(step_name, "started")

    def on_step_complete(self, step_name: str) -> None:
        self.router.workflow_step(step_name, "completed")

    # ── Debate eventi ─────────────────────────────────────────────────────────

    def on_debate_started(self, topic: str) -> None:
        self.router.route("debate", f"Debate pokrenuta za temu: {topic[:100]}")

    def on_argument(self, agent: str, argument: str) -> None:
        self.router.debate_event("argument", agent, argument[:120])

    def on_critique(self, agent: str, critique: str) -> None:
        self.router.debate_event("critique", agent, critique[:120])

    def on_conflict_detected(self, agent_a: str, agent_b: str, topic: str) -> None:
        self.router.debate_event(
            "conflict", agent_a, f"u sukobu sa {agent_b} oko: {topic[:80]}"
        )

    def on_consensus_reached(self, decision: str, confidence: float) -> None:
        pct = int(confidence * 100)
        self.router.debate_event(
            "consensus", "Orchestrator",
            f"{decision[:100]} — pouzdanost {pct} posto"
        )

    def on_final_decision(self, decision: str) -> None:
        self.router.final_decision(decision[:150])

    # ── Agent eventi ──────────────────────────────────────────────────────────

    def on_agent_output(self, agent_name: str, output: str) -> None:
        self.router.agent_output(agent_name, output)

    def on_agent_error(self, agent_name: str, error: str) -> None:
        self.router.error(f"Agent '{agent_name}' prijavio grešku: {error[:100]}")

    # ── Memory eventi ─────────────────────────────────────────────────────────

    def on_memory_loaded(self, num_items: int) -> None:
        self.router.route("system", f"Memorija učitana: {num_items} stavki.")

    def on_memory_stored(self, artifact_type: str) -> None:
        self.router.route("system", f"Sačuvano u memoriji: {artifact_type}.")

    # ── Sistemski eventi ──────────────────────────────────────────────────────

    def on_system_ready(self) -> None:
        self.router.system_alert("AI Workflow Orchestrator spreman.")

    def on_shutdown(self) -> None:
        self.router.system_alert("Sistem se gasi. Čuvam stanje.")
        self.router.stop()

    # ── Dekorator ─────────────────────────────────────────────────────────────

    @staticmethod
    def tts_step(step_name: str, router_attr: str = "tts"):
        """
        Dekorator koji automatski izgovara početak i kraj metode.

        Primer:
            class Orchestrator:
                tts = TTSMiddleware()

                @TTSMiddleware.tts_step("load_memory_context")
                def load_memory_context(self):
                    ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self_obj, *args, **kwargs):
                mw: TTSMiddleware = getattr(self_obj, router_attr, None)
                if mw:
                    mw.on_step_start(step_name)
                try:
                    result = func(self_obj, *args, **kwargs)
                    if mw:
                        mw.on_step_complete(step_name)
                    return result
                except Exception as exc:
                    if mw:
                        mw.on_workflow_failed(step_name, str(exc))
                    raise
            return wrapper
        return decorator

    def get_status(self) -> dict:
        return {
            "router": self.router.get_status(),
        }
