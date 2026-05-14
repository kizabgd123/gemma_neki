"""
PiperTTSEngine — core engine za lokalni TTS koristeći Piper TTS.

Piper radi potpuno offline, bez API ključeva.
Koristi ONNX modele za brzu, prirodnu sintezu govora.

Instalacija (pokrenuti jednom ručno u terminalu):
    sudo apt install python3-pipx espeak-ng-data alsa-utils
    pipx install piper-tts

Preuzimanje modela:
    mkdir -p ~/.local/share/piper-voices
    cd ~/.local/share/piper-voices
    # Srpski glas:
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/sr/rs/serbski_institut/medium/sr_RS-serbski_institut-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/sr/rs/serbski_institut/medium/sr_RS-serbski_institut-medium.onnx.json
    # Engleski glas (backup):
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

Test:
    echo "Sistem je spreman" | ~/.local/bin/piper --model ~/.local/share/piper-voices/en_US-lessac-medium.onnx --output_raw | aplay -r 22050 -f S16_LE -t raw -
"""

import subprocess
import shutil
import logging
import os
import threading
import queue
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PiperConfig:
    """Konfiguracija za Piper TTS engine."""
    model_path: str = ""
    voices_dir: str = "~/.local/share/piper-voices"
    sample_rate: int = 22050
    audio_format: str = "S16_LE"
    speaker_id: Optional[int] = None
    length_scale: float = 1.0         # <1.0 brže, >1.0 sporije
    noise_scale: float = 0.667
    noise_w: float = 0.8
    player_cmd: str = "aplay"
    max_queue_size: int = 50
    async_mode: bool = True


class PiperTTSEngine:
    """
    Piper TTS Engine — lokalni, offline, neuronski TTS.

    Unix filozofija: text | piper --output_raw | aplay -r 22050 -f S16_LE -t raw -
    Nema međufajlova. Nema cloud-a. Nema API ključeva.

    Primer:
        engine = PiperTTSEngine(PiperConfig(
            model_path="~/.local/share/piper-voices/en_US-lessac-medium.onnx"
        ))
        engine.speak("Sistem je spreman.")
        engine.speak_agent_output("AnalysisAgent", "Identifikavano je 3 rešenja.")
        engine.speak_debate_event("decision", "Orchestrator", "Odabrana opcija B.")
    """

    def __init__(self, config: Optional[PiperConfig] = None):
        self.config = config or PiperConfig()
        self._queue: queue.Queue = queue.Queue(maxsize=self.config.max_queue_size)
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._piper_bin: Optional[str] = None
        self._aplay_bin: Optional[str] = None
        self._ready = False
        self._stats = {
            "total_spoken": 0,
            "total_errors": 0,
            "session_start": datetime.utcnow().isoformat(),
        }
        self._resolve_binaries()
        self._resolve_model()
        if self.config.async_mode:
            self._start_worker()

    # ── Inicijalizacija ───────────────────────────────────────────────────────

    def _resolve_binaries(self) -> None:
        """Pronađi piper i aplay u sistemu."""
        search_dirs = [
            os.path.expanduser("~/.local/bin"),
            "/usr/local/bin",
            "/usr/bin",
        ]
        for d in search_dirs:
            candidate = os.path.join(d, "piper")
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                self._piper_bin = candidate
                logger.info(f"[TTS] piper pronađen: {self._piper_bin}")
                break

        if not self._piper_bin:
            self._piper_bin = shutil.which("piper")

        if not self._piper_bin:
            logger.warning(
                "[TTS] ⚠️  piper NIJE PRONAĐEN!\n"
                "     Pokrenite: pipx install piper-tts\n"
                "     Zatim proverite: ~/.local/bin/piper --version"
            )

        self._aplay_bin = shutil.which(self.config.player_cmd)
        if not self._aplay_bin:
            logger.warning(
                f"[TTS] ⚠️  '{self.config.player_cmd}' nije pronađen!\n"
                "     Pokrenite: sudo apt install alsa-utils"
            )

    def _resolve_model(self) -> None:
        """Razreši putanju do ONNX modela, ili auto-detektuj."""
        if not self.config.model_path:
            voices_dir = Path(self.config.voices_dir).expanduser()
            if voices_dir.exists():
                models = sorted(voices_dir.glob("**/*.onnx"))
                if models:
                    self.config.model_path = str(models[0])
                    logger.info(f"[TTS] Auto-detektovan model: {self.config.model_path}")

        if self.config.model_path:
            p = Path(self.config.model_path).expanduser()
            if p.exists():
                self._ready = bool(self._piper_bin and self._aplay_bin)
                if self._ready:
                    logger.info(f"[TTS] ✅ Engine spreman. Model: {p.name}")
            else:
                logger.warning(f"[TTS] Model nije pronađen na putanji: {p}")
        else:
            logger.warning(
                "[TTS] ⚠️  Nema modela.\n"
                "     Preuzmite sa: https://huggingface.co/rhasspy/piper-voices\n"
                "     Stavite u: ~/.local/share/piper-voices/"
            )

    # ── Async worker ──────────────────────────────────────────────────────────

    def _start_worker(self) -> None:
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._audio_worker,
            name="piper-tts-worker",
            daemon=True,
        )
        self._worker_thread.start()
        logger.debug("[TTS] Async worker pokrenut.")

    def _audio_worker(self) -> None:
        while self._running:
            try:
                item = self._queue.get(timeout=1.0)
                if item is None:
                    break
                self._synthesize_and_play(item)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as exc:
                logger.error(f"[TTS Worker] Greška: {exc}")

    # ── Jezgro pipeline-a ─────────────────────────────────────────────────────

    def _synthesize_and_play(self, text: str) -> bool:
        """
        Sintetizuj i reprodukuj tekst:
            echo TEXT | piper --model X.onnx --output_raw | aplay -r 22050 -f S16_LE -t raw -

        Returns:
            True ako je uspešno, False ako je greška.
        """
        if not self._ready:
            logger.warning(f"[TTS] Engine nije spreman. Tekst izgubljen: '{text[:50]}'")
            return False

        if not text or not text.strip():
            return True

        try:
            model_path = str(Path(self.config.model_path).expanduser())

            piper_cmd = [self._piper_bin, "--model", model_path, "--output_raw"]
            if self.config.speaker_id is not None:
                piper_cmd += ["--speaker", str(self.config.speaker_id)]
            if self.config.length_scale != 1.0:
                piper_cmd += ["--length_scale", str(self.config.length_scale)]
            if self.config.noise_scale != 0.667:
                piper_cmd += ["--noise_scale", str(self.config.noise_scale)]

            aplay_cmd = [
                self._aplay_bin,
                "-r", str(self.config.sample_rate),
                "-f", self.config.audio_format,
                "-t", "raw",
                "-",
            ]

            # Pokreni oba procesa
            piper_proc = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            aplay_proc = subprocess.Popen(
                aplay_cmd,
                stdin=piper_proc.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )

            # Pošalji tekst piper-u i zatvori stdin
            piper_proc.stdin.write(text.encode("utf-8"))
            piper_proc.stdin.close()

            piper_proc.wait()
            aplay_proc.wait()

            if piper_proc.returncode != 0:
                err = piper_proc.stderr.read().decode("utf-8", errors="replace")
                logger.error(f"[TTS] piper greška (exit {piper_proc.returncode}): {err}")
                self._stats["total_errors"] += 1
                return False

            self._stats["total_spoken"] += 1
            logger.debug(f"[TTS] ✅ Izgovoreno ({len(text)} ch): '{text[:60]}...'")
            return True

        except FileNotFoundError as exc:
            logger.error(f"[TTS] Binarni fajl nije pronađen: {exc}")
            self._stats["total_errors"] += 1
            return False
        except Exception as exc:
            logger.error(f"[TTS] Neočekivana greška: {exc}", exc_info=True)
            self._stats["total_errors"] += 1
            return False

    # ── Javni API ─────────────────────────────────────────────────────────────

    def speak(self, text: str, priority: bool = False) -> None:
        """
        Izgovori tekst.

        Args:
            text: Tekst koji treba izgovoriti.
            priority: Ako True, preskoči red i izgovori odmah (sync).
        """
        if not text or not text.strip():
            return
        if not self.config.async_mode or priority:
            self._synthesize_and_play(text)
        else:
            try:
                self._queue.put_nowait(text)
            except queue.Full:
                logger.warning("[TTS] Red pun, poruka odbijena.")

    def speak_agent_output(
        self, agent_name: str, output: str, truncate: int = 200
    ) -> None:
        """Izgovori output agenta sa prefiksom."""
        if len(output) > truncate:
            output = output[:truncate] + "... ostatak skraćen."
        self.speak(f"{agent_name} kaže: {output}")

    def speak_debate_event(
        self, event_type: str, agent: str, message: str
    ) -> None:
        """Izgovori debate event sa kontekstualnim prefiksom."""
        prefixes = {
            "argument":  f"{agent} argumentuje",
            "conflict":  f"Konflikt — {agent} protivreči",
            "decision":  "Finalna odluka sistema",
            "consensus": "Konsenzus postignut",
            "warning":   f"Upozorenje od {agent}",
            "critique":  f"{agent} kritikuje",
        }
        prefix = prefixes.get(event_type, agent)
        is_priority = event_type in ("decision", "consensus")
        self.speak(f"{prefix}: {message}", priority=is_priority)

    def speak_workflow_status(self, step: str, status: str) -> None:
        """Izgovori status workflow koraka."""
        labels = {
            "started":   f"Pokrenuto: {step}",
            "completed": f"Završeno: {step}",
            "failed":    f"GREŠKA u koraku: {step}. Proverite logove.",
            "skipped":   f"Preskočeno: {step}",
        }
        self.speak(labels.get(status, f"{step}: {status}"))

    def wait_until_done(self, timeout: float = 30.0) -> None:
        """Blokiraj dok se red ne isprazni."""
        self._queue.join()

    def stop(self) -> None:
        """Gašenje engine-a i worker threada."""
        self._running = False
        if self.config.async_mode:
            try:
                self._queue.put_nowait(None)
            except queue.Full:
                pass
            if self._worker_thread:
                self._worker_thread.join(timeout=5.0)
        logger.info(f"[TTS] Engine ugašen. Statistike: {self._stats}")

    def get_status(self) -> dict:
        """Vrati rečnik statusa engine-a."""
        return {
            "ready":      self._ready,
            "piper_bin":  self._piper_bin,
            "aplay_bin":  self._aplay_bin,
            "model_path": self.config.model_path,
            "queue_size": self._queue.qsize(),
            "async_mode": self.config.async_mode,
            "stats":      self._stats,
        }

    def __repr__(self) -> str:
        state = "SPREMAN ✅" if self._ready else "NIJE SPREMAN ⚠️"
        model = Path(self.config.model_path).name if self.config.model_path else "NEMA MODELA"
        return f"<PiperTTSEngine [{state}] model={model}>"
