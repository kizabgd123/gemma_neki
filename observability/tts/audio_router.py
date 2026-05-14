"""
AudioRouter — centralni router za audio notifikacije.

Filtrira kategorije, podržava mute/unmute i fallback.
"""

import logging
from typing import Optional, Set
from tts_piper_engine import PiperTTSEngine, PiperConfig

logger = logging.getLogger(__name__)


class AudioRouter:
    """
    Centralni router za sve audio notifikacije u AI Workflow Orchestratoru.

    Kategorije:
        'workflow'  → koraci workflow-a (started/completed/failed)
        'debate'    → debate eventi (argument/conflict/decision)
        'agent'     → izlaz specijalizovanih agenata
        'decision'  → finalne odluke (uvek prioritet)
        'error'     → sistemske greške
        'system'    → opšte sistemske poruke
    """

    DEFAULT_ENABLED: Set[str] = {"decision", "workflow", "error", "system"}

    def __init__(
        self,
        engine: Optional[PiperTTSEngine] = None,
        enabled_categories: Optional[Set[str]] = None,
        fallback_to_print: bool = True,
    ):
        self.engine = engine
        self.enabled_categories: Set[str] = (
            enabled_categories or set(self.DEFAULT_ENABLED)
        )
        self.fallback_to_print = fallback_to_print
        self._muted = False

    @classmethod
    def from_config(cls, config: PiperConfig, **kwargs) -> "AudioRouter":
        """Napravi AudioRouter sa novim PiperTTSEngine."""
        return cls(engine=PiperTTSEngine(config), **kwargs)

    # ── Glavna metoda ─────────────────────────────────────────────────────────

    def route(self, category: str, text: str, **kwargs) -> None:
        """
        Prosledi audio poruku odgovarajućem engine-u.

        Args:
            category: Tip poruke ('workflow', 'debate', 'agent', 'decision', 'error', 'system').
            text: Tekst za izgovaranje.
            **kwargs: Prosleđuje se PiperTTSEngine.speak() (npr. priority=True).
        """
        if self._muted:
            return
        if category not in self.enabled_categories:
            logger.debug(f"[AudioRouter] Kategorija '{category}' nije aktivna.")
            return

        if self.engine and self.engine._ready:
            self.engine.speak(text, **kwargs)
        elif self.fallback_to_print:
            tag = category.upper()
            print(f"\033[36m[AUDIO/{tag}]\033[0m {text}")
        else:
            logger.warning(f"[AudioRouter] TTS nedostupan, poruka izgubljena: {text[:80]}")

    # ── Convenience metode ────────────────────────────────────────────────────

    def workflow_step(self, step_name: str, status: str) -> None:
        """Izgovori status workflow koraka."""
        if self.engine and self.engine._ready:
            self.engine.speak_workflow_status(step_name, status)
        else:
            self.route("workflow", f"Workflow {step_name}: {status}")

    def debate_event(self, event_type: str, agent: str, message: str) -> None:
        """Izgovori debate event."""
        if self.engine and self.engine._ready:
            self.engine.speak_debate_event(event_type, agent, message)
        else:
            self.route("debate", f"[{event_type.upper()}] {agent}: {message}")

    def agent_output(self, agent_name: str, output: str, truncate: int = 150) -> None:
        """Izgovori skraćeni output agenta."""
        if self.engine and self.engine._ready:
            self.engine.speak_agent_output(agent_name, output, truncate)
        else:
            short = output[:truncate] + "..." if len(output) > truncate else output
            self.route("agent", f"{agent_name}: {short}")

    def final_decision(self, decision_text: str) -> None:
        """Izgovori finalnu odluku — uvek visoki prioritet."""
        self.route("decision", f"Finalna odluka: {decision_text}", priority=True)

    def system_alert(self, message: str) -> None:
        """Sistemska poruka — visoki prioritet."""
        self.route("system", message, priority=True)

    def error(self, message: str) -> None:
        """Izgovori grešku."""
        self.route("error", f"Greška: {message}", priority=True)

    # ── Kontrola ──────────────────────────────────────────────────────────────

    def mute(self) -> None:
        self._muted = True
        logger.info("[AudioRouter] 🔇 Audio utišan.")

    def unmute(self) -> None:
        self._muted = False
        logger.info("[AudioRouter] 🔊 Audio uključen.")

    def enable_category(self, category: str) -> None:
        self.enabled_categories.add(category)
        logger.debug(f"[AudioRouter] Kategorija '{category}' omogućena.")

    def disable_category(self, category: str) -> None:
        self.enabled_categories.discard(category)
        logger.debug(f"[AudioRouter] Kategorija '{category}' onemogućena.")

    def stop(self) -> None:
        if self.engine:
            self.engine.stop()

    def get_status(self) -> dict:
        return {
            "muted": self._muted,
            "enabled_categories": sorted(self.enabled_categories),
            "engine": self.engine.get_status() if self.engine else None,
        }

    def __repr__(self) -> str:
        state = "🔇 MUTED" if self._muted else "🔊 ACTIVE"
        cats = ", ".join(sorted(self.enabled_categories))
        return f"<AudioRouter [{state}] categories=[{cats}]>"
