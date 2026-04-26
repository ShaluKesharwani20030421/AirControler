"""
Aether-Link Voice Engine
Offline speech recognition using Vosk for surgical voice commands.
Voice fills ONLY the gaps where the 3D depth camera cannot deliver:
  - Text input (replaces painfully slow air-keyboard)
  - Click confirmation (replaces unreliable air-push)
  - App/mode switching by name (replaces tedious sequential swiping)
"""

import threading
import queue
import json
import os
import time


class VoiceEngine:
    """
    Offline voice command engine using Vosk.
    Runs in a dedicated background thread.
    Commands are pushed to a thread-safe queue for the main loop to consume.
    """

    # ── Recognised command phrases ────────────────────────────────────
    # ONLY these phrases are accepted. Everything else is silently ignored.
    # This eliminates false triggers from background noise / TV / music.
    # ── Safety rule: ALL commands are MULTI-WORD (≥2 words) except a few ──
    # Single-word commands are REMOVED because short words appear in normal
    # speech ('it' ⊂ 'exit', 'lay' ⊂ 'play', etc.) causing false triggers.
    # Only truly unambiguous short words kept: 'click', 'select', 'screenshot'
    COMMANDS = {
        # Navigation — all multi-word, very safe
        "go home":          {"type": "nav", "target": "home"},
        "go to home":       {"type": "nav", "target": "home"},
        "go to media":      {"type": "nav", "target": "media"},
        "media mode":       {"type": "nav", "target": "media"},
        "go to mouse":      {"type": "nav", "target": "mouse"},
        "mouse mode":       {"type": "nav", "target": "mouse"},
        "go to tab":        {"type": "nav", "target": "tab"},
        "tab mode":         {"type": "nav", "target": "tab"},
        "go to window":     {"type": "nav", "target": "window"},
        "window mode":      {"type": "nav", "target": "window"},
        "go back":          {"type": "nav", "target": "back"},

        # Click confirmation — kept: distinctive enough
        "click":            {"type": "click", "button": "left"},
        "select":           {"type": "click", "button": "left"},
        "double click":     {"type": "click", "button": "double"},
        "right click":      {"type": "click", "button": "right"},

        # Media — REMOVED single-word 'play', 'pause', 'mute' (too risky)
        # Using multi-word variants only
        "play music":       {"type": "media", "action": "play_pause"},
        "pause music":      {"type": "media", "action": "play_pause"},
        "play pause":       {"type": "media", "action": "play_pause"},
        "volume up":        {"type": "media", "action": "volume_up"},
        "volume down":      {"type": "media", "action": "volume_down"},
        "next track":       {"type": "media", "action": "next_track"},
        "next song":        {"type": "media", "action": "next_track"},
        "previous track":   {"type": "media", "action": "previous_track"},
        "mute audio":       {"type": "media", "action": "mute"},

        # Tab actions — all multi-word, safe
        "next tab":         {"type": "tab", "action": "next_tab"},
        "previous tab":     {"type": "tab", "action": "previous_tab"},
        "close tab":        {"type": "tab", "action": "close_tab"},
        "new tab":          {"type": "tab", "action": "new_tab"},

        # Window actions
        "next window":      {"type": "window", "action": "next_window"},
        "previous window":  {"type": "window", "action": "previous_window"},
        "minimize window":  {"type": "window", "action": "minimize"},
        "maximize window":  {"type": "window", "action": "maximize"},
        "task view":        {"type": "window", "action": "task_view"},

        # Utility — REMOVED single-word 'exit', 'lock', 'keyboard' (too dangerous)
        # Using multi-word variants only
        "take screenshot":  {"type": "action", "action": "screenshot"},
        "show keyboard":    {"type": "action", "action": "toggle_keyboard"},
        "lock system":      {"type": "action", "action": "lock"},
        "exit app":         {"type": "action", "action": "exit"},
    }

    def __init__(self, model_path=None):
        """
        Args:
            model_path: Path to Vosk model directory.
                        Default: models/vosk-model-small-en-us-0.15
        """
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'models', 'vosk-model-small-en-us-0.15'
            )

        self.model_path = model_path
        self.command_queue = queue.Queue(maxsize=10)
        self.listening = False
        self.available = False
        self._thread = None
        self._last_cmd_time = 0
        self.CMD_COOLDOWN = 0.5  # seconds between voice commands

        self._init_engine()

    def _init_engine(self):
        """Initialize Vosk model and recognizer."""
        try:
            from vosk import Model, KaldiRecognizer, SetLogLevel
            SetLogLevel(-1)  # suppress Vosk debug output

            if not os.path.isdir(self.model_path):
                print(f"[Voice] Model not found at: {self.model_path}")
                print(f"[Voice] Download it:")
                print(f"  pip install vosk")
                print(f"  Download from: https://alphacephei.com/vosk/models")
                print(f"  Extract to: models/vosk-model-small-en-us-0.15/")
                print(f"[Voice] Voice commands DISABLED — gesture-only mode")
                return

            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.available = True
            print(f"[Voice] Vosk model loaded from: {self.model_path}")
            print(f"[Voice] {len(self.COMMANDS)} voice commands available")

        except ImportError:
            print("[Voice] 'vosk' not installed — voice commands DISABLED")
            print("[Voice] Install with: pip install vosk pyaudio")
            print("[Voice] Gesture-only mode active")
        except Exception as e:
            print(f"[Voice] Init error: {e}")
            print("[Voice] Voice commands DISABLED — gesture-only mode")

    def start(self):
        """Start the voice listening thread."""
        if not self.available:
            return False

        try:
            import pyaudio
            self._pyaudio = pyaudio
        except ImportError:
            print("[Voice] 'pyaudio' not installed — voice DISABLED")
            print("[Voice] Install with: pip install pyaudio")
            self.available = False
            return False

        self.listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[Voice] Listening started (background thread)")
        return True

    def stop(self):
        """Stop the voice listening thread."""
        self.listening = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        print("[Voice] Listening stopped")

    def _listen_loop(self):
        """Main voice listening loop — runs in background thread."""
        try:
            audio = self._pyaudio.PyAudio()
            stream = audio.open(
                rate=16000,
                channels=1,
                format=self._pyaudio.paInt16,
                input=True,
                frames_per_buffer=4096,
            )
            stream.start_stream()
            print("[Voice] Microphone stream opened")

            while self.listening:
                try:
                    data = stream.read(4096, exception_on_overflow=False)
                except OSError:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip().lower()
                    if text:
                        self._process_text(text)

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except Exception as e:
            print(f"[Voice] Listen loop error: {e}")
            self.listening = False

    def _process_text(self, text):
        """Parse recognized text into a command and push to queue.

        STRICT matching only — NO fuzzy/partial matching.
        Fuzzy matching caused 'it' → 'exit' crash (substring of 'exit').
        Only EXACT phrase match or 'type ...' prefix is accepted.
        """
        now = time.time()
        if now - self._last_cmd_time < self.CMD_COOLDOWN:
            return

        # Guard: ignore very short noise (1-2 chars, e.g. 'it', 'a', 'the')
        if len(text) < 3:
            return

        # Check for "type ..." prefix (free-form text input)
        if text.startswith("type "):
            content = text[5:].strip()
            if content and len(content) >= 2:  # at least 2 chars to type
                cmd = {"type": "text", "content": content}
                self._push_command(cmd, text)
                return

        # EXACT match only — no fuzzy, no partial, no substring
        cmd = self.COMMANDS.get(text)
        if cmd:
            self._push_command(cmd, text)
            return

        # ⚠️ NO FUZZY MATCHING — intentionally removed.
        # Fuzzy matching caused false triggers (e.g. 'it' matched 'exit').
        # If a command is misheard, the user simply says it again.

    def _push_command(self, cmd, raw_text):
        """Push a parsed command to the queue."""
        self._last_cmd_time = time.time()
        try:
            self.command_queue.put_nowait(cmd)
            print(f"[Voice] Recognized: '{raw_text}' → {cmd}")
        except queue.Full:
            pass  # drop command if queue is full

    def get_command(self):
        """Non-blocking: get next command from queue, or None."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def is_available(self):
        """Check if voice engine is available and running."""
        return self.available and self.listening
