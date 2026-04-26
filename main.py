import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pyorbbecsdk import (
    Pipeline, Config as OBConfig,
    OBSensorType, OBFormat, OBFrameType, OBAlignMode,
)

from core.depth_lock import DepthLock
from core.gesture_detector import GestureDetector
from core.state_machine import StateMachine, AppState
from ui.hud_overlay_premium import HUDOverlay  # Premium magical UI
from ui.menu_renderer import MenuRenderer
from modes.media_mode import MediaMode
from modes.mouse_mode import MouseMode
from modes.keyboard_mode import KeyboardMode
from modes.tab_mode import TabMode
from modes.window_mode import WindowMode
from voice.voice_engine import VoiceEngine
from utils.camera_utils import process_depth_frame, process_ir_frame, process_color_frame
import os
import time
import threading
import pyautogui
from utils.config import Config as AppConfig
from security.signature_recorder import SignatureRecorder
from security.signature_verifier import SignatureVerifier


class AetherLink:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # ── Dynamic screen resolution (must happen before MenuRenderer) ──
        screen = self.app.primaryScreen().geometry()
        AppConfig.SCREEN_WIDTH  = screen.width()
        AppConfig.SCREEN_HEIGHT = screen.height()
        print(f"Screen: {AppConfig.SCREEN_WIDTH}x{AppConfig.SCREEN_HEIGHT}")

        self.pipeline      = None
        self.device        = None
        self.ir_ftype      = OBFrameType.LEFT_IR_FRAME
        self.use_color_cam = False   # set True when color stream starts

        # Dwell-click: hover a button for DWELL_TIME seconds = auto-click
        self.DWELL_TIME     = 1.5
        self._dwell_btn     = None   # currently hovered button index
        self._dwell_start   = 0.0

        self.depth_lock       = DepthLock()
        self.gesture_detector = GestureDetector()

        # --- Security: Signature-based lock ---
        self.SIGNATURE_FILE = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'signatures', 'my_signature.json'
        )
        sig_exists = os.path.isfile(self.SIGNATURE_FILE)
        self.state_machine = StateMachine(require_auth=sig_exists)

        if sig_exists:
            self.signature_verifier = SignatureVerifier(
                reference_path=self.SIGNATURE_FILE,
                threshold=350.0,  # More forgiving threshold (was 200)
            )
            print(f"[Security] Signature loaded — system starts LOCKED")
            print("           Forgot signature? Delete: signatures\\my_signature.json")
        else:
            self.signature_verifier = None
            print("[Security] No signature found — system UNLOCKED")
            print("           Record one:  python record_signature.py")

        self.sig_recorder = SignatureRecorder(duration=3.0, min_z_variance=100.0)
        self._lock_msg_shown = False
        self._failed_attempts = 0
        self._bypass_available = False

        self.hud          = HUDOverlay()
        self.menu_renderer = MenuRenderer(AppConfig.SCREEN_WIDTH, AppConfig.SCREEN_HEIGHT)

        self.media_mode    = MediaMode()
        self.mouse_mode    = MouseMode()
        self.keyboard_mode = KeyboardMode()
        self.tab_mode      = TabMode()
        self.window_mode   = WindowMode()

        # ── Voice Engine (surgical voice commands) ─────────────────
        self.voice_engine = VoiceEngine()
        if self.voice_engine.available:
            self.voice_engine.start()
            print("[Voice] Voice engine active — say 'click', 'type ...', 'go home', etc.")
        else:
            print("[Voice] Voice unavailable — gesture-only mode (all features still work)")

        self.current_hand_data = None
        self.prev_hand_data    = None
        self.running = False
        
        self.latest_frame_data = None
        self.frame_lock = threading.Lock()

        self.init_camera()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(33)   # ~30 FPS strictly for UI
        
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        if self.running:
            self.capture_thread.start()

    # ------------------------------------------------------------------
    def init_camera(self):
        try:
            self.pipeline = Pipeline()
            self.device   = self.pipeline.get_device()
            info = self.device.get_device_info()
            print(f"Camera : {info.get_name()}  FW: {info.get_firmware_version()}")

            sensor_list = self.device.get_sensor_list()
            has_left_ir = has_ir = False
            for i in range(sensor_list.get_count()):
                st = sensor_list.get_sensor_by_index(i).get_type()
                if st == OBSensorType.LEFT_IR_SENSOR:
                    has_left_ir = True
                elif st == OBSensorType.IR_SENSOR:
                    has_ir = True

            config = OBConfig()

            # ── Depth stream (prefer 30 fps, fallback to default) ─────
            try:
                d_profiles = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
                d_profile = None
                for w, fps in [(640, 30), (848, 30), (0, 30)]:
                    try:
                        d_profile = d_profiles.get_video_stream_profile(w, 0, OBFormat.Y16, fps)
                        break
                    except Exception:
                        continue
                if d_profile is None:
                    d_profile = d_profiles.get_default_video_stream_profile()
                config.enable_stream(d_profile)
                print(f"Depth  : {d_profile.get_width()}x{d_profile.get_height()} @ {d_profile.get_fps()}fps  fmt={d_profile.get_format()}")
            except Exception as e:
                print(f"[ERROR] Depth stream failed: {e}")
                return False

            # ── COLOR stream (primary tracking camera) ────────────────
            # MediaPipe was trained on RGB — color gives far better detection
            # than grayscale IR, especially near the edges of the FOV.
            color_ok = False
            try:
                c_profiles = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
                c_profile = None
                for w, fmt, fps in [
                    (640, OBFormat.RGB,  30), (640, OBFormat.MJPG, 30),
                    (0,   OBFormat.RGB,  30), (0,   OBFormat.MJPG, 30),
                ]:
                    try:
                        c_profile = c_profiles.get_video_stream_profile(w, 0, fmt, fps)
                        break
                    except Exception:
                        continue
                if c_profile is None:
                    c_profile = c_profiles.get_default_video_stream_profile()
                config.enable_stream(c_profile)
                print(f"Color  : {c_profile.get_width()}x{c_profile.get_height()} @ {c_profile.get_fps()}fps  fmt={c_profile.get_format()}")
                color_ok = True
                self.use_color_cam = True
            except Exception as e:
                print(f"[WARN ] Color stream unavailable ({e}), falling back to IR")

            # ── IR fallback (used only if color unavailable) ──────────
            if not color_ok:
                ir_sensor = OBSensorType.LEFT_IR_SENSOR if has_left_ir else OBSensorType.IR_SENSOR
                self.ir_ftype = OBFrameType.LEFT_IR_FRAME if has_left_ir else OBFrameType.IR_FRAME
                try:
                    ir_profiles = self.pipeline.get_stream_profile_list(ir_sensor)
                    ir_profile = None
                    for fmt, w, fps in [
                        (OBFormat.Y8, 640, 30), (OBFormat.Y8, 848, 30),
                        (OBFormat.Y16, 640, 30), (OBFormat.Y8, 0, 30),
                    ]:
                        try:
                            ir_profile = ir_profiles.get_video_stream_profile(w, 0, fmt, fps)
                            break
                        except Exception:
                            continue
                    if ir_profile is None:
                        ir_profile = ir_profiles.get_default_video_stream_profile()
                    config.enable_stream(ir_profile)
                    lbl = "IR Left" if has_left_ir else "IR"
                    print(f"{lbl:6s} : {ir_profile.get_width()}x{ir_profile.get_height()} @ {ir_profile.get_fps()}fps  fmt={ir_profile.get_format()}")
                except Exception as e:
                    print(f"[ERROR] IR stream also failed: {e}")
                    return False

            # ── D2C hardware alignment (depth reprojected to color FOV) ─
            try:
                config.set_align_mode(OBAlignMode.HW_MODE)
                print("D2C    : HW alignment enabled")
            except Exception as e:
                print(f"[WARN ] D2C alignment: {e}")

            # ── Frame sync ────────────────────────────────────────────
            try:
                self.pipeline.enable_frame_sync()
            except Exception as e:
                print(f"[WARN ] Frame sync: {e}")

            self.pipeline.start(config)
            print("Camera ready — streaming started.\n")
            self.running = True
            return True

        except Exception as e:
            print(f"[ERROR] Camera init failed: {e}")
            return False

    # ------------------------------------------------------------------
    def capture_loop(self):
        """Runs in background thread to unblock main UI thread."""
        while self.running:
            if self.pipeline is None:
                time.sleep(0.1)
                continue
            try:
                frames = self.pipeline.wait_for_frames(100)
                if frames is None:
                    continue

                depth_frame = frames.get_depth_frame()
                track_frame = None
                if self.use_color_cam:
                    color_raw = frames.get_frame(OBFrameType.COLOR_FRAME)
                    track_frame = process_color_frame(color_raw)
                if track_frame is None:
                    ir_raw = frames.get_frame(self.ir_ftype)
                    track_frame = process_ir_frame(ir_raw)

                if depth_frame is None or track_frame is None:
                    continue

                depth_colormap, depth_data = process_depth_frame(
                    depth_frame, AppConfig.DEPTH_MIN, AppConfig.DEPTH_MAX
                )
                if depth_data is None:
                    continue

                hand_data = self.depth_lock.process_frame(track_frame, depth_data)
                
                with self.frame_lock:
                    self.latest_frame_data = (track_frame, depth_colormap, hand_data)

            except Exception as e:
                import traceback
                print(f"[WARN ] Capture error: {e}")
                traceback.print_exc()

    def update_ui(self):
        """Runs in main UI thread."""
        if not self.running:
            return
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cleanup()
            return
            
        with self.frame_lock:
            if not self.latest_frame_data:
                return
            track_frame, depth_colormap, hand_data = self.latest_frame_data
            self.latest_frame_data = None  # consume it

        self.prev_hand_data    = self.current_hand_data
        self.current_hand_data = hand_data

        # ── Check voice commands (non-blocking) ──────────────────
        # IMPORTANT: Voice is BLOCKED when LOCKED.
        # Only the 3D air-signature can unlock the system — voice cannot bypass it.
        if not self.state_machine.is_locked():
            voice_cmd = self.voice_engine.get_command()
            if voice_cmd:
                self.handle_voice_command(voice_cmd)
        else:
            # Drain the queue silently so commands don't queue up during lock
            self.voice_engine.get_command()

        self.handle_gestures()
        self.update_hud()

        debug_frame = track_frame.copy()
        if self.current_hand_data:
            debug_frame = self.depth_lock.draw_hand_landmarks(debug_frame, self.current_hand_data)
        src = "Color" if self.use_color_cam else "IR"
        cv2.putText(debug_frame,
                    f"[{src}] {self.state_machine.get_state_name()}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Aether-Link  [Hand Tracking]", debug_frame)
        if depth_colormap is not None:
            cv2.imshow("Aether-Link  [Depth Map]", depth_colormap)
    
    def handle_gestures(self):
        if self.current_hand_data is None:
            return

        # Interaction box is now ADVISORY only — gestures always work.
        # The air-push detector self-gates via depth history velocity.
        air_push = self.gesture_detector.detect_air_push(self.current_hand_data)

        if air_push:
            self.hud.flash_click()   # visual "CLICK!" banner for 250 ms

        if self.state_machine.is_locked():
            self.handle_locked_mode(air_push)
            return

        if self.state_machine.is_home():
            self.handle_home_mode(air_push)
        elif self.state_machine.is_media():
            self.handle_media_mode(air_push)
        elif self.state_machine.is_mouse():
            self.handle_mouse_mode(air_push)
        elif self.state_machine.is_tab():
            self.handle_tab_mode(air_push)
        elif self.state_machine.is_window():
            self.handle_window_mode(air_push)
    
    def _compute_gain(self, z_mm):
        """Dynamic cursor gain based on hand distance from camera.
        Close (30cm) → precise, slow cursor for small targets.
        Far  (1.5m)  → fast cursor, small wrist flick = full screen.
        """
        if z_mm < 100:  # invalid or too close
            return 1.0
        raw = (z_mm / AppConfig.Z_GAIN_REF_DISTANCE) ** AppConfig.Z_GAIN_POWER
        return max(AppConfig.Z_GAIN_MIN, min(AppConfig.Z_GAIN_MAX, raw))

    def _screen_pos(self):
        """Return (screen_x, screen_y) with Z-adaptive cursor gain.
        4% margin keeps hand in reliable stereo zone.
        Gain scales cursor speed based on distance from camera.
        """
        nx = self.current_hand_data['index_tip']['normalized_x']
        ny = self.current_hand_data['index_tip']['normalized_y']
        z_mm = self.current_hand_data['index_tip']['z']

        gain = self._compute_gain(z_mm)

        # Apply gain around the center of normalised space (0.5, 0.5)
        cx, cy = 0.5, 0.5
        nx_scaled = cx + (nx - cx) * gain
        ny_scaled = cy + (ny - cy) * gain

        return (self._map_to_screen(nx_scaled, 0.04, AppConfig.SCREEN_WIDTH),
                self._map_to_screen(ny_scaled, 0.04, AppConfig.SCREEN_HEIGHT))

    def _check_dwell(self, hovered_idx, air_push):
        """Returns True when a click should fire (air-push OR dwell 1.5 s).
        Also returns dwell_progress [0..1] for the HUD arc indicator.
        """
        now = time.time()
        if not hasattr(self, '_dwell_last_seen'):
            self._dwell_last_seen = now

        if air_push:
            self._dwell_btn   = None
            self._dwell_start = 0.0
            return True, 0.0

        # Forgiveness / Leaky Bucket for hand jitter
        if hovered_idx is None and self._dwell_btn is not None:
            if (now - self._dwell_last_seen) < 0.3:
                # Pretend we are still hovering it
                hovered_idx = self._dwell_btn
            else:
                self._dwell_btn   = None
                self._dwell_start = 0.0
                return False, 0.0
        elif hovered_idx is None:
            self._dwell_btn   = None
            self._dwell_start = 0.0
            return False, 0.0

        if self._dwell_btn != hovered_idx:
            self._dwell_btn   = hovered_idx
            self._dwell_start = now

        self._dwell_last_seen = now
        elapsed  = now - self._dwell_start
        progress = min(1.0, elapsed / self.DWELL_TIME)
        
        if elapsed >= self.DWELL_TIME:
            self._dwell_btn   = None
            self._dwell_start = 0.0
            self.hud.flash_click()
            return True, 1.0
        return False, progress

    def _check_back(self, sx, sy, air_push, hovered_idx):
        """Returns True when the persistent BACK button is activated."""
        back_rect = self.menu_renderer.get_back_button_rect()
        bx, by, bw, bh = back_rect
        on_back = (bx <= sx <= bx + bw) and (by <= sy <= by + bh)
        if on_back:
            clicked, _ = self._check_dwell(-1, air_push)  # -1 = back button
            return clicked
        return False

    def handle_home_mode(self, air_push):
        # Check keyboard overlay first
        if self.state_machine.has_keyboard_overlay():
            sx, sy = self._screen_pos()
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        buttons  = self.menu_renderer.get_home_menu_buttons()
        sx, sy   = self._screen_pos()
        hovered  = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)

        # Pinch → toggle keyboard
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.toggle_keyboard_overlay()
            return
        
        # Peace sign → screenshot
        if self.gesture_detector.detect_peace_sign(self.current_hand_data):
            self._take_screenshot()
            return

        if clicked and hovered is not None:
            bid = buttons[hovered]['id']
            if bid == 'media':      self.state_machine.go_to_media()
            elif bid == 'mouse':    self.state_machine.go_to_mouse()
            elif bid == 'tab':      self.state_machine.go_to_tab()
            elif bid == 'window':   self.state_machine.go_to_window()
            elif bid == 'keyboard': self.state_machine.show_keyboard_overlay('manual')
            elif bid == 'exit':     self.cleanup()
    
    def handle_media_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Pinch → toggle keyboard (deliberate gesture)
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.toggle_keyboard_overlay()
            return
        
        # Peace sign → screenshot
        if self.gesture_detector.detect_peace_sign(self.current_hand_data):
            self._take_screenshot()
            return
        
        # Open Palm → Play/Pause (its ORIGINAL purpose, not keyboard!)
        if self.gesture_detector.detect_open_palm(self.current_hand_data):
            self.media_mode.play_pause()
            return
        
        # Swipe gestures
        if self.gesture_detector.detect_swipe_up(self.current_hand_data, self.prev_hand_data):
            self.media_mode.volume_up()
            return
        if self.gesture_detector.detect_swipe_down(self.current_hand_data, self.prev_hand_data):
            self.media_mode.volume_down()
            return
        if self.gesture_detector.detect_swipe_right(self.current_hand_data, self.prev_hand_data):
            self.media_mode.next_track()
            return
        if self.gesture_detector.detect_swipe_left(self.current_hand_data, self.prev_hand_data):
            self.media_mode.previous_track()
            return
        
        # Clickable buttons (air-push/dwell on specific buttons)
        buttons = self.menu_renderer.get_media_menu_buttons()
        hovered = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)
        
        if clicked and hovered is not None:
            bid = buttons[hovered]['id']
            if bid == 'play_pause':    self.media_mode.play_pause()
            elif bid == 'next_track':  self.media_mode.next_track()
            elif bid == 'volume_up':   self.media_mode.volume_up()
            elif bid == 'volume_down': self.media_mode.volume_down()
    
    def handle_mouse_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Pinch → toggle keyboard (deliberate gesture)
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.toggle_keyboard_overlay()
            return
        
        # Peace sign → screenshot
        if self.gesture_detector.detect_peace_sign(self.current_hand_data):
            self._take_screenshot()
            return
        
        # Normal mouse control
        self.mouse_mode.move_cursor_screen(sx, sy)
        
        if air_push:
            self.mouse_mode.click()
    
    def handle_keyboard_overlay(self, air_push, sx, sy):
        """
        Keyboard overlay — type with air-push on keys.
        Dismiss: Pinch (toggle) or BACK button. NOT swipe (avoids conflicts).
        """
        # Pinch → dismiss keyboard (same gesture that opened it)
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.dismiss_keyboard_overlay()
            return
        
        # BACK button → dismiss keyboard
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.dismiss_keyboard_overlay()
            return
        
        # Type on keyboard buttons
        buttons = self.keyboard_mode.get_keyboard_buttons(
            AppConfig.SCREEN_WIDTH, AppConfig.SCREEN_HEIGHT
        )
        hovered  = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)
        
        if clicked and hovered is not None:
            button_id = buttons[hovered]['id']
            self.keyboard_mode.type_key(button_id)

    def handle_tab_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Pinch → toggle keyboard (deliberate gesture)
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.toggle_keyboard_overlay()
            return
        
        # Peace sign → screenshot
        if self.gesture_detector.detect_peace_sign(self.current_hand_data):
            self._take_screenshot()
            return
        
        # Swipe shortcuts (still work)
        if self.gesture_detector.detect_swipe_right(self.current_hand_data, self.prev_hand_data):
            self.tab_mode.next_tab()
            return
        if self.gesture_detector.detect_swipe_left(self.current_hand_data, self.prev_hand_data):
            self.tab_mode.previous_tab()
            return
        
        # Button-based actions — Close Tab ONLY fires on button hover!
        # No more accidental tab closing from random air-pushes.
        buttons = self.menu_renderer.get_tab_menu_buttons()
        hovered = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)
        
        if clicked and hovered is not None:
            bid = buttons[hovered]['id']
            if bid == 'next_tab':    self.tab_mode.next_tab()
            elif bid == 'prev_tab':  self.tab_mode.previous_tab()
            elif bid == 'close_tab': self.tab_mode.close_tab()
            elif bid == 'new_tab':   self.tab_mode.new_tab()

    def handle_window_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Pinch → toggle keyboard (deliberate gesture)
        if self.gesture_detector.detect_pinch(self.current_hand_data):
            self.state_machine.toggle_keyboard_overlay()
            return
        
        # Peace sign → screenshot
        if self.gesture_detector.detect_peace_sign(self.current_hand_data):
            self._take_screenshot()
            return
        
        # Swipe shortcuts (still work)
        if self.gesture_detector.detect_swipe_right(self.current_hand_data, self.prev_hand_data):
            self.window_mode.next_window()
            return
        if self.gesture_detector.detect_swipe_left(self.current_hand_data, self.prev_hand_data):
            self.window_mode.previous_window()
            return
        if self.gesture_detector.detect_swipe_up(self.current_hand_data, self.prev_hand_data):
            self.window_mode.show_task_view()
            return
        if self.gesture_detector.detect_swipe_down(self.current_hand_data, self.prev_hand_data):
            self.window_mode.minimize_window()
            return
        
        # Clickable buttons
        buttons = self.menu_renderer.get_window_menu_buttons()
        hovered = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)
        
        if clicked and hovered is not None:
            bid = buttons[hovered]['id']
            if bid == 'next_window':  self.window_mode.next_window()
            elif bid == 'prev_window': self.window_mode.previous_window()
            elif bid == 'task_view':  self.window_mode.show_task_view()
            elif bid == 'minimize':   self.window_mode.minimize_window()
            elif bid == 'maximize':   self.window_mode.maximize_window()

    # ------------------------------------------------------------------
    def handle_locked_mode(self, air_push):
        """LOCKED state — user must draw air-signature to unlock."""
        if not self._lock_msg_shown:
            print("\n" + "="*70)
            print("  🔒  SYSTEM LOCKED — Draw your air-signature to unlock")
            print("      Air-push to start recording (3 seconds)")
            print("\n  💡 TIPS:")
            print("      • Draw the SAME pattern you recorded")
            print("      • Move forward/backward (3D motion required)")
            print("      • Simple patterns work best (circle, figure-8)")
            print("\n  🆘 FORGOT SIGNATURE?")
            print("      Press Q in OpenCV window, then delete:")
            print("      signatures\\my_signature.json")
            print("="*70 + "\n")
            self._lock_msg_shown = True

        # If recorder is actively recording, feed it points
        if self.sig_recorder.recording:
            complete = self.sig_recorder.add_point(self.current_hand_data)
            progress = self.sig_recorder.get_progress()
            self.hud.set_dwell_progress(progress if progress >= 0 else 0)

            if complete:
                # Signature captured — verify it
                result = self.signature_verifier.verify(
                    self.sig_recorder.signature_path
                )
                if result['verified']:
                    print("\n✅ Signature VERIFIED — unlocking system!")
                    self.state_machine.unlock()
                    self._lock_msg_shown = False
                    self._failed_attempts = 0
                    self.hud.flash_click()
                else:
                    self._failed_attempts += 1
                    print(f"\n❌ Verification FAILED (Attempt {self._failed_attempts}): {result['reason']}")
                    print(f"   DTW Distance: {result['dtw_distance']:.1f} (threshold: 350)")
                    
                    if self._failed_attempts >= 3:
                        print("\n" + "="*70)
                        print("  🆘 EMERGENCY BYPASS AVAILABLE")
                        print("     Press Q in OpenCV window to exit, then:")
                        print("     del signatures\\my_signature.json")
                        print("     Then restart the app (it will start UNLOCKED)")
                        print("="*70 + "\n")
                        self._bypass_available = True
                    else:
                        print("   Try again — air-push to start\n")
                
                # Reset recorder for next attempt
                self.sig_recorder = SignatureRecorder(duration=3.0, min_z_variance=100.0)
            return

        # Not recording yet — air-push starts recording
        if air_push:
            self.sig_recorder.start_recording()
            self.hud.flash_click()
    
    # ------------------------------------------------------------------
    def handle_voice_command(self, cmd):
        """Route voice commands to the appropriate handler.
        Voice is a surgical patch — it only handles discrete/named actions
        that the camera cannot do well.
        """
        t = cmd['type']

        if t == 'nav':
            target = cmd['target']
            if target == 'home':    self.state_machine.go_to_home()
            elif target == 'media': self.state_machine.go_to_media()
            elif target == 'mouse': self.state_machine.go_to_mouse()
            elif target == 'tab':   self.state_machine.go_to_tab()
            elif target == 'window':self.state_machine.go_to_window()
            elif target == 'back':  self.state_machine.go_to_home()
            self.hud.flash_click()
            print(f"[Voice] Navigation → {target}")

        elif t == 'click':
            btn = cmd['button']
            if btn == 'left':      self.mouse_mode.click()
            elif btn == 'double':  self.mouse_mode.double_click()
            elif btn == 'right':   self.mouse_mode.right_click()
            self.hud.flash_click()
            print(f"[Voice] Click → {btn}")

        elif t == 'text':
            pyautogui.write(cmd['content'], interval=0.02)
            self.hud.flash_click()
            print(f"[Voice] Typed: '{cmd['content']}'")

        elif t == 'media':
            action = cmd['action']
            if action == 'play_pause':     self.media_mode.play_pause()
            elif action == 'volume_up':    self.media_mode.volume_up()
            elif action == 'volume_down':  self.media_mode.volume_down()
            elif action == 'next_track':   self.media_mode.next_track()
            elif action == 'previous_track': self.media_mode.previous_track()
            elif action == 'mute':         self.media_mode.mute()
            self.hud.flash_click()
            print(f"[Voice] Media → {action}")

        elif t == 'tab':
            action = cmd['action']
            if action == 'next_tab':     self.tab_mode.next_tab()
            elif action == 'previous_tab': self.tab_mode.previous_tab()
            elif action == 'close_tab':  self.tab_mode.close_tab()
            elif action == 'new_tab':    self.tab_mode.new_tab()
            self.hud.flash_click()
            print(f"[Voice] Tab → {action}")

        elif t == 'window':
            action = cmd['action']
            if action == 'next_window':     self.window_mode.next_window()
            elif action == 'previous_window': self.window_mode.previous_window()
            elif action == 'minimize':      self.window_mode.minimize_window()
            elif action == 'maximize':      self.window_mode.maximize_window()
            elif action == 'task_view':     self.window_mode.show_task_view()
            self.hud.flash_click()
            print(f"[Voice] Window → {action}")

        elif t == 'action':
            action = cmd['action']
            if action == 'screenshot':       self._take_screenshot()
            elif action == 'toggle_keyboard': self.state_machine.toggle_keyboard_overlay()
            elif action == 'lock':           self.state_machine.lock()
            elif action == 'exit':           self.cleanup()
            print(f"[Voice] Action → {action}")

    def _take_screenshot(self):
        """Take screenshot with Win+PrintScreen."""
        pyautogui.hotkey('win', 'printscreen')
        print("[Action] Screenshot taken! (Win+PrintScreen)")
        self.hud.flash_click()

    @staticmethod
    def _map_to_screen(norm, margin, screen_size):
        """
        Gemini 335 FOV fix: map normalised coord to screen using only the
        central (1 - 2*margin) of the frame.  This keeps the fingertip out
        of the stereo blind-spot zone at the edges so depth stays valid.
        margin = 0.075  →  use central 85% of frame width / height.
        """
        clamped = max(margin, min(1.0 - margin, norm))
        ratio   = (clamped - margin) / (1.0 - 2 * margin)
        return int(ratio * screen_size)

    def update_hud(self):
        if self.current_hand_data is None:
            self.hud.set_hand_status(False, 0.0)
            return

        z_mm = self.current_hand_data['index_tip']['z']
        screen_x, screen_y = self._screen_pos()

        self.hud.set_cursor_position(screen_x, screen_y)
        self.hud.set_hand_status(True, z_mm)

        if self.state_machine.is_locked():
            self.hud.set_buttons([])
            self.hud.set_hovered_button(None)
            if self.sig_recorder.recording:
                progress = self.sig_recorder.get_progress()
                self.hud.set_state_text("🔒  RECORDING SIGNATURE")
                self.hud.set_info_text(f"Drawing... {int(progress*100)}% — keep moving in 3D!")
                self.hud.set_dwell_progress(progress if progress >= 0 else 0)
            else:
                if self._failed_attempts > 0:
                    self.hud.set_state_text(f"🔒  LOCKED (Attempt {self._failed_attempts}/∞)")
                    if self._bypass_available:
                        self.hud.set_info_text("Forgot? Press Q, delete signatures\\my_signature.json, restart")
                    else:
                        self.hud.set_info_text("Try again | Air-push to record | Draw SAME pattern")
                else:
                    self.hud.set_state_text("🔒  LOCKED")
                    self.hud.set_info_text("Air-push to draw your signature | Forgot? Press Q for help")
                self.hud.set_dwell_progress(0)
            return

        # ── Keyboard overlay HUD (same for every mode) ──────────────────
        if self.state_machine.has_keyboard_overlay():
            mode_name = self.state_machine.current_state.name
            buttons = self.keyboard_mode.get_keyboard_buttons(
                AppConfig.SCREEN_WIDTH, AppConfig.SCREEN_HEIGHT
            )
            hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
            self.hud.set_buttons(buttons)
            self.hud.set_hovered_button(hovered)
            self.hud.set_state_text(f"{mode_name} + KEYBOARD")
            self.hud.set_info_text("Type with air-push | Pinch or BACK to dismiss")
            return

        # ── Normal mode HUD ──────────────────────────────────────────────
        if self.state_machine.is_home():
            buttons = self.menu_renderer.get_home_menu_buttons()
            hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
            self.hud.set_buttons(buttons)
            self.hud.set_hovered_button(hovered)
            self.hud.set_state_text("HOME MENU")
            self.hud.set_info_text("Air-push to select | Pinch for keyboard | Peace for screenshot")
            
        elif self.state_machine.is_media():
            buttons = self.menu_renderer.get_media_menu_buttons()
            hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
            self.hud.set_buttons(buttons)
            self.hud.set_hovered_button(hovered)
            self.hud.set_state_text("MEDIA CONTROL")
            self.hud.set_info_text("Swipe: Vol Up/Down, Track L/R | Palm: Play/Pause | Pinch: Keyboard")
            
        elif self.state_machine.is_mouse():
            self.hud.set_buttons([])
            self.hud.set_hovered_button(None)
            self.hud.set_state_text("AIR MOUSE")
            self.hud.set_info_text("Move hand to control cursor | Air-push to click | Pinch: Keyboard")
            
        elif self.state_machine.is_tab():
            buttons = self.menu_renderer.get_tab_menu_buttons()
            hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
            self.hud.set_buttons(buttons)
            self.hud.set_hovered_button(hovered)
            self.hud.set_state_text("TAB SWITCHER")
            self.hud.set_info_text("Swipe L/R to switch | Click buttons for actions | Pinch: Keyboard")
            
        elif self.state_machine.is_window():
            buttons = self.menu_renderer.get_window_menu_buttons()
            hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
            self.hud.set_buttons(buttons)
            self.hud.set_hovered_button(hovered)
            self.hud.set_state_text("WINDOW SWITCHER")
            self.hud.set_info_text("Swipe to switch/minimize/taskview | Click buttons | Pinch: Keyboard")
    
    def cleanup(self):
        print("\nShutting down Aether-Link...")
        self.running = False

        # Stop voice engine
        if self.voice_engine and self.voice_engine.is_available():
            self.voice_engine.stop()
        
        if self.pipeline:
            self.pipeline.stop()
        
        self.depth_lock.cleanup()
        
        cv2.destroyAllWindows()
        
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        # Force UTF-8 output so Unicode chars don't crash on Windows console
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

        print("\n" + "="*60)
        print("  AETHER-LINK: Touchless Gesture + Voice Interface")
        print("="*60)
        print("  Gestures (Camera):")
        print("    Air-Push   (push forward 5cm) => Click / Select")
        print("    Pinch      (thumb + index)    => Toggle Keyboard")
        print("    Peace Sign (index + middle)   => Screenshot")
        print("    Open Palm  (all fingers)      => Play/Pause")
        print("    Swipe      (move hand fast)   => Directional")
        if self.voice_engine.is_available():
            print("  Voice Commands (say clearly):")
            print("    'click'                       => Click at cursor")
            print("    'type hello world'            => Type text instantly")
            print("    'go home' / 'go to media'     => Navigate modes")
            print("    'play music' / 'volume up'    => Media control")
            print("    'next tab' / 'close tab'      => Tab control")
            print("    'minimize window' / 'task view' => Window control")
        print("  Navigation:")
        print("    BACK button (top-center)      => Go back")
        print("    Press 'Q' in OpenCV window    => Quit")
        print("="*60 + "\n")
        
        sys.exit(self.app.exec())

if __name__ == "__main__":
    aether = AetherLink()
    aether.run()
