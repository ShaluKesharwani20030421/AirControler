import time
import numpy as np
from utils.config import Config


class GestureDetector:
    """
    Milestone B — Air-Push Trigger:
    Detects a rapid forward push (Z decreases >= 5 cm in <= 0.2 s) as a click.
    Uses raw_z (unsmoothed) from hand_data for accurate velocity measurement.
    """

    def __init__(self):
        self.depth_history = []
        self.last_click_time = 0
        self.click_cooldown = 0.5     # seconds between recognised clicks

        self.last_swipe_time = 0
        self.swipe_cooldown = 0.8     # seconds between swipes (prevents accidental triggers)

        self.last_palm_time = 0
        self.palm_cooldown = 1.5      # seconds — raised from 1.2 to reduce false triggers

        # Pinch gesture (thumb + index close together)
        self.last_pinch_time = 0
        self.pinch_cooldown = 1.0     # seconds between pinch triggers
        self._was_pinching = False    # edge detection state

        # Peace sign gesture (index + middle extended)
        self.last_peace_time = 0
        self.peace_cooldown = 2.0     # screenshot shouldn't fire often

    # ------------------------------------------------------------------
    # Max plausible human hand push: ~1.5 m/s × 0.35 s = 525 mm → cap at 600 mm.
    # Any ΔZ above this is stereo noise (depth dropped to 0 at FOV edge).
    MAX_VALID_DELTA_Z = 600.0
    MIN_VALID_DEPTH   = 80.0    # mm — below this = stereo blind / no-return pixel

    def detect_air_push(self, hand_data):
        """
        Milestone B — Air-Push:
        Detects ΔZ >= AIR_CLICK_THRESHOLD mm in <= AIR_CLICK_TIME_WINDOW s.

        Gemini 335 stereo physics fixes:
          • raw_z = 0 near FOV edges (blind spot) → SKIP, don't add to history.
          • ΔZ > 600 mm is physically impossible → REJECT, not a real push.
          • Require ≥ 3 valid samples so a single-frame glitch can't trigger.
        """
        if hand_data is None:
            self.depth_history.clear()
            return False

        raw_z = hand_data['index_tip'].get('raw_z', 0.0)
        now   = time.time()

        # ── Only append VALID depth readings ─────────────────────────
        if raw_z >= self.MIN_VALID_DEPTH:
            self.depth_history.append({'z': raw_z, 'time': now})

        # Keep only entries within the time window
        self.depth_history = [
            e for e in self.depth_history
            if now - e['time'] <= Config.AIR_CLICK_TIME_WINDOW
        ]

        # Need at least 3 valid readings to trigger (noise protection)
        if len(self.depth_history) < 3:
            return False

        if now - self.last_click_time < self.click_cooldown:
            return False

        oldest = self.depth_history[0]
        newest = self.depth_history[-1]
        depth_change = oldest['z'] - newest['z']   # positive = finger moved closer
        time_diff    = newest['time'] - oldest['time']

        # ── Hard physics cap — reject stereo noise spikes ────────────
        if depth_change > self.MAX_VALID_DELTA_Z:
            # This is a 0-depth false reading, not a real push — clear and ignore
            self.depth_history.clear()
            return False

        if depth_change >= Config.AIR_CLICK_THRESHOLD and time_diff <= Config.AIR_CLICK_TIME_WINDOW:
            print(f"[Gesture] Air-Push! ΔZ={depth_change:.1f} mm in {time_diff*1000:.0f} ms")
            self.last_click_time = now
            self.depth_history.clear()
            return True

        return False

    # ------------------------------------------------------------------
    # Swipe thresholds: higher = harder to trigger (less false positives)
    SWIPE_Y_THRESHOLD = 50   # pixels for up/down swipe
    SWIPE_X_THRESHOLD = 60   # pixels for left/right swipe

    def detect_swipe_up(self, hand_data, prev_hand_data):
        """Detect upward swipe with cooldown to prevent per-frame firing."""
        if hand_data is None or prev_hand_data is None:
            return False
        now = time.time()
        if now - self.last_swipe_time < self.swipe_cooldown:
            return False
        y_diff = prev_hand_data['index_tip']['y'] - hand_data['index_tip']['y']
        if y_diff > self.SWIPE_Y_THRESHOLD:
            self.last_swipe_time = now
            print(f"[Gesture] Swipe Up (Δy={y_diff}px)")
            return True
        return False

    # ------------------------------------------------------------------
    def detect_swipe_down(self, hand_data, prev_hand_data):
        """Detect downward swipe with cooldown."""
        if hand_data is None or prev_hand_data is None:
            return False
        now = time.time()
        if now - self.last_swipe_time < self.swipe_cooldown:
            return False
        y_diff = hand_data['index_tip']['y'] - prev_hand_data['index_tip']['y']
        if y_diff > self.SWIPE_Y_THRESHOLD:
            self.last_swipe_time = now
            print(f"[Gesture] Swipe Down (Δy={y_diff}px)")
            return True
        return False

    # ------------------------------------------------------------------
    def detect_swipe_left(self, hand_data, prev_hand_data):
        """Detect leftward swipe (for tab switching)."""
        if hand_data is None or prev_hand_data is None:
            return False
        now = time.time()
        if now - self.last_swipe_time < self.swipe_cooldown:
            return False
        x_diff = prev_hand_data['index_tip']['x'] - hand_data['index_tip']['x']
        if x_diff > self.SWIPE_X_THRESHOLD:
            self.last_swipe_time = now
            print(f"[Gesture] Swipe Left (Δx={x_diff}px)")
            return True
        return False

    # ------------------------------------------------------------------
    def detect_swipe_right(self, hand_data, prev_hand_data):
        """Detect rightward swipe (for tab switching)."""
        if hand_data is None or prev_hand_data is None:
            return False
        now = time.time()
        if now - self.last_swipe_time < self.swipe_cooldown:
            return False
        x_diff = hand_data['index_tip']['x'] - prev_hand_data['index_tip']['x']
        if x_diff > self.SWIPE_X_THRESHOLD:
            self.last_swipe_time = now
            print(f"[Gesture] Swipe Right (Δx={x_diff}px)")
            return True
        return False

    # ------------------------------------------------------------------
    def detect_open_palm(self, hand_data):
        """
        Detect open palm — ALL 4 fingers must be extended (was 3, too sensitive).
        Used for mode-specific actions: Play/Pause, New Tab, Maximize.
        NOT used for keyboard (use Pinch instead).
        """
        if hand_data is None:
            return False
        now = time.time()
        if now - self.last_palm_time < self.palm_cooldown:
            return False

        if 'landmarks_list' in hand_data:
            landmarks = hand_data['landmarks_list']
        elif 'landmarks' in hand_data:
            landmarks = hand_data['landmarks'].landmark
        else:
            return False

        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        extended = sum(
            1 for tip, pip in zip(finger_tips, finger_pips)
            if landmarks[tip].y < landmarks[pip].y
        )
        if extended >= 4:   # ALL 4 fingers must be clearly extended
            self.last_palm_time = now
            print("[Gesture] Open Palm \U0001f590")
            return True
        return False

    # ------------------------------------------------------------------
    # Pinch: thumb tip + index tip close together
    PINCH_THRESHOLD = 0.06   # normalised distance (~3 cm at 50 cm range)

    def detect_pinch(self, hand_data):
        """
        Detect pinch (thumb tip + index finger tip close together).
        Edge-triggered: fires ONCE when fingers come together.
        Used globally for toggling the keyboard overlay.
        """
        if hand_data is None:
            self._was_pinching = False
            return False
        now = time.time()
        if now - self.last_pinch_time < self.pinch_cooldown:
            return False

        if 'landmarks_list' not in hand_data:
            return False

        landmarks = hand_data['landmarks_list']
        thumb = landmarks[4]   # THUMB_TIP
        index = landmarks[8]   # INDEX_FINGER_TIP

        dx = thumb.x - index.x
        dy = thumb.y - index.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        is_pinching = dist < self.PINCH_THRESHOLD

        # Edge detection — only fire on NOT-pinching → pinching transition
        if is_pinching and not self._was_pinching:
            self._was_pinching = True
            self.last_pinch_time = now
            print(f"[Gesture] Pinch! (d={dist:.3f})")
            return True

        if not is_pinching:
            self._was_pinching = False

        return False

    # ------------------------------------------------------------------
    def detect_peace_sign(self, hand_data):
        """
        Detect peace / victory sign: index + middle extended, ring + pinky closed.
        Used for taking a screenshot.
        """
        if hand_data is None:
            return False
        now = time.time()
        if now - self.last_peace_time < self.peace_cooldown:
            return False

        if 'landmarks_list' not in hand_data:
            return False

        landmarks = hand_data['landmarks_list']

        index_ext  = landmarks[8].y  < landmarks[6].y   # tip above PIP
        middle_ext = landmarks[12].y < landmarks[10].y
        ring_closed  = landmarks[16].y >= landmarks[14].y
        pinky_closed = landmarks[20].y >= landmarks[18].y

        if index_ext and middle_ext and ring_closed and pinky_closed:
            self.last_peace_time = now
            print("[Gesture] Peace Sign \u270c\ufe0f — Screenshot!")
            return True
        return False

    # ------------------------------------------------------------------
    def is_in_back_zone(self, hand_data, screen_width, screen_height):
        """Return True if cursor is in the top-left back corner."""
        if hand_data is None:
            return False
        nx = hand_data['index_tip']['normalized_x']
        ny = hand_data['index_tip']['normalized_y']
        sx = nx * screen_width
        sy = ny * screen_height
        return sx < Config.BACK_BUTTON_ZONE_SIZE and sy < Config.BACK_BUTTON_ZONE_SIZE

    # ------------------------------------------------------------------
    def reset(self):
        self.depth_history.clear()
        self.last_click_time = 0
        self.last_swipe_time = 0
        self.last_palm_time = 0
        self.last_pinch_time = 0
        self.last_peace_time = 0
        self._was_pinching = False
