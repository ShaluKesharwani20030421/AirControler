import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import RunningMode
from utils.camera_utils import get_depth_at_point
from utils.config import Config


# Landmark indices (same as old mp.solutions.hands.HandLandmark)
_INDEX_FINGER_TIP = 8
_THUMB_TIP        = 4
_WRIST            = 0

# Hand connection pairs for drawing skeleton
_HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),       # thumb
    (0,5),(5,6),(6,7),(7,8),       # index
    (0,9),(9,10),(10,11),(11,12),  # middle
    (0,13),(13,14),(14,15),(15,16),# ring
    (0,17),(17,18),(18,19),(19,20),# pinky
    (5,9),(9,13),(13,17),          # palm
]


class DepthLock:
    """
    Depth-Lock Logic (MediaPipe Tasks API — v0.10.21+, Python 3.13+):
    Maps MediaPipe hand landmarks onto the Orbbec Depth Map and returns
    the exact Z distance in millimetres.

    Key fix: depth lookup uses normalized coords mapped to depth_data's
    own resolution, so IR/depth resolution mismatches are handled correctly.
    """

    def __init__(self):
        # --- Locate model file -----------------------------------------
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'models', 'hand_landmarker.task'
        )
        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"MediaPipe model not found at {model_path}\n"
                "Download it:\n"
                "  Invoke-WebRequest -Uri "
                "\"https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/"
                "hand_landmarker.task\" "
                "-OutFile \"models\\hand_landmarker.task\""
            )

        # --- Create HandLandmarker (VIDEO mode for frame-by-frame) -----
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.3,
            running_mode=RunningMode.VIDEO,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self._frame_ts = 0  # monotonic timestamp for VIDEO mode

        # --- EMA smoothing state ----------------------------------------
        self.prev_x = 0
        self.prev_y = 0
        self.prev_z = 450.0   # init to 45 cm midpoint

        # --- Extra cursor smoothing for mouse control -------------------
        self.prev_norm_x = 0.5
        self.prev_norm_y = 0.5
        self.CURSOR_SMOOTH = 0.25  # higher = smoother, lower = faster. 0.25 = 1.5x faster

    # ------------------------------------------------------------------
    _PATCH = 7   # 15×15 neighbourhood for depth median

    def _lookup_depth(self, depth_data, norm_x, norm_y):
        """
        Depth-Lock core — Gemini 335 stereo-aware:
        Sample a 15×15 neighbourhood and take the MEDIAN of valid (>50 mm) pixels.
        """
        if depth_data is None:
            return 0.0
        dh, dw = depth_data.shape
        cx = int(norm_x * dw)
        cy = int(norm_y * dh)
        p  = self._PATCH
        x0 = max(0, cx - p);  x1 = min(dw, cx + p + 1)
        y0 = max(0, cy - p);  y1 = min(dh, cy + p + 1)
        patch = depth_data[y0:y1, x0:x1]
        valid = patch[patch > 50.0]
        if valid.size == 0:
            return 0.0
        return float(np.median(valid))

    # ------------------------------------------------------------------
    def process_frame(self, ir_frame, depth_data):
        """
        Process one pair of (colour/IR image, depth array) and return
        hand_data dict with 3-D position for each tracked landmark.
        """
        if ir_frame is None or depth_data is None:
            return None

        ir_h, ir_w = ir_frame.shape[:2]
        rgb_frame = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2RGB)

        # Convert to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect — VIDEO mode needs monotonic timestamp
        self._frame_ts += 33  # ~30 FPS
        result = self.landmarker.detect_for_video(mp_image, self._frame_ts)

        if not result.hand_landmarks:
            return None

        # Pick first (closest) hand
        landmarks = result.hand_landmarks[0]

        idx_lm = landmarks[_INDEX_FINGER_TIP]
        thm_lm = landmarks[_THUMB_TIP]
        wst_lm = landmarks[_WRIST]

        # --- Depth-Lock: normalised → depth-map pixel → mm --------
        raw_z = self._lookup_depth(depth_data, idx_lm.x, idx_lm.y)

        # --- EMA smoothing (position + depth) ----------------------
        raw_x = idx_lm.x * ir_w
        raw_y = idx_lm.y * ir_h
        a = Config.SMOOTHING_FACTOR
        sx = int(a * self.prev_x + (1 - a) * raw_x)
        sy = int(a * self.prev_y + (1 - a) * raw_y)

        if raw_z > 50:
            sz = a * self.prev_z + (1 - a) * raw_z
            self.prev_z = max(sz, 50.0)
        else:
            sz = self.prev_z

        sx_clamped = max(0, min(sx, ir_w - 1))
        sy_clamped = max(0, min(sy, ir_h - 1))
        self.prev_x, self.prev_y = sx_clamped, sy_clamped
        sx, sy = sx_clamped, sy_clamped

        # --- Extra cursor smoothing for normalized coords -----------
        cs = self.CURSOR_SMOOTH
        # Flip X-axis: hand right → cursor right (mirror effect)
        flipped_x = 1.0 - idx_lm.x
        smooth_nx = cs * self.prev_norm_x + (1 - cs) * flipped_x
        smooth_ny = cs * self.prev_norm_y + (1 - cs) * idx_lm.y
        self.prev_norm_x = smooth_nx
        self.prev_norm_y = smooth_ny

        hand_data = {
            'index_tip': {
                'x': sx,
                'y': sy,
                'z': sz,
                'raw_z': raw_z,
                'normalized_x': smooth_nx,
                'normalized_y': smooth_ny,
            },
            'thumb_tip': {
                'x': int(thm_lm.x * ir_w),
                'y': int(thm_lm.y * ir_h),
                'z': self._lookup_depth(depth_data, thm_lm.x, thm_lm.y),
            },
            'wrist': {
                'x': int(wst_lm.x * ir_w),
                'y': int(wst_lm.y * ir_h),
                'z': self._lookup_depth(depth_data, wst_lm.x, wst_lm.y),
            },
            'landmarks_list': landmarks,   # list of NormalizedLandmark
            'frame_width': ir_w,
            'frame_height': ir_h,
        }
        return hand_data

    # ------------------------------------------------------------------
    def is_in_interaction_box(self, hand_data):
        """Return True if the index finger is within the 30-60 cm zone."""
        if hand_data is None:
            return False
        z = hand_data['index_tip']['z']
        return Config.INTERACTION_BOX_MIN <= z <= Config.INTERACTION_BOX_MAX

    # ------------------------------------------------------------------
    def draw_hand_landmarks(self, frame, hand_data):
        """Draw skeleton + depth annotation on the debug frame."""
        if hand_data is None or 'landmarks_list' not in hand_data:
            return frame

        lms = hand_data['landmarks_list']
        h, w = frame.shape[:2]

        # Draw connections
        for (s, e) in _HAND_CONNECTIONS:
            x1, y1 = int(lms[s].x * w), int(lms[s].y * h)
            x2, y2 = int(lms[e].x * w), int(lms[e].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw landmark dots
        for lm in lms:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

        # Draw index tip with depth
        ix = hand_data['index_tip']['x']
        iy = hand_data['index_tip']['y']
        z_mm = hand_data['index_tip']['z']
        z_cm = z_mm / 10.0

        in_box = self.is_in_interaction_box(hand_data)
        dot_color = (0, 255, 0) if in_box else (0, 100, 255)

        cv2.circle(frame, (ix, iy), 10, dot_color, -1)

        label = f"{z_cm:.1f} cm  ({'IN' if in_box else 'OUT'})"
        cv2.putText(frame, label, (ix + 12, iy - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, dot_color, 2)

        return frame

    # ------------------------------------------------------------------
    def cleanup(self):
        self.landmarker.close()
