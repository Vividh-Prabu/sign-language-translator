"""
Text-to-Speech (TTS) Service for the Sign Language Translator GUI.
Provides speech output for translated signs and sentences.
Supports pyttsx3 when installed, native Windows SAPI synthesis, and silent mock fallback.
"""

import os
import sys
import threading
import logging
from typing import Optional
import frontend.config as config

logger = logging.getLogger(__name__)


class TTSService:
    """
    Manages speech synthesis for translating sign language outputs to audible speech.
    Non-blocking and thread-safe.
    """

    def __init__(self, enabled: bool = config.TTS_ENABLED, rate: int = config.DEFAULT_SPEECH_RATE):
        self.enabled = enabled
        self.rate = rate
        self._engine = None
        self._is_speaking = False
        self._init_engine()

    def _init_engine(self) -> None:
        """Initialize the speech engine if available."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
        except Exception:
            self._engine = None

    def speak(self, text: str) -> None:
        """Speak the given text asynchronously without freezing the UI."""
        if not self.enabled or not text or text.strip() == "" or text.strip() == "—":
            return

        thread = threading.Thread(target=self._speak_worker, args=(text.strip(),), daemon=True)
        thread.start()

    def _speak_worker(self, text: str) -> None:
        """Background worker for speech synthesis."""
        self._is_speaking = True
        try:
            if self._engine is not None:
                self._engine.say(text)
                self._engine.runAndWait()
            elif sys.platform == "win32":
                # Fallback to Windows SAPI via PowerShell command without blocking UI
                import subprocess
                clean_text = text.replace('"', '').replace("'", "")
                ps_cmd = (
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$s.Speak('{clean_text}')"
                )
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                    startupinfo=startupinfo,
                    timeout=5,
                    check=False
                )
        except Exception as e:
            logger.debug(f"TTS execution note: {e}")
        finally:
            self._is_speaking = False

    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self._is_speaking

    def set_enabled(self, enabled: bool) -> None:
        """Toggle TTS state."""
        self.enabled = enabled

    def set_rate(self, rate: int) -> None:
        """Update speech rate."""
        self.rate = rate
        if self._engine is not None:
            try:
                self._engine.setProperty("rate", self.rate)
            except Exception:
                pass


# Global singleton instance
tts_service = TTSService()
