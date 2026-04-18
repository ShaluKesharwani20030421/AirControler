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
from utils.camera_utils import process_depth_frame, process_ir_frame, process_color_frame
import os
import time
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

        self.current_hand_data = None
        self.prev_hand_data    = None
        self.running = False

        self.init_camera()

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(33)   # ~30 FPS

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
    def process_frame(self):
        if not self.running or self.pipeline is None:
            return
        try:
            frames = self.pipeline.wait_for_frames(100)
            if frames is None:
                return

            depth_frame = frames.get_depth_frame()
            # ── Get tracking frame (color preferred, IR fallback) ─────
            track_frame = None
            if self.use_color_cam:
                color_raw = frames.get_frame(OBFrameType.COLOR_FRAME)
                track_frame = process_color_frame(color_raw)
            if track_frame is None:
                ir_raw = frames.get_frame(self.ir_ftype)
                track_frame = process_ir_frame(ir_raw)

            if depth_frame is None or track_frame is None:
                return

            depth_colormap, depth_data = process_depth_frame(
                depth_frame, AppConfig.DEPTH_MIN, AppConfig.DEPTH_MAX
            )
            if depth_data is None:
                return

            self.prev_hand_data    = self.current_hand_data
            self.current_hand_data = self.depth_lock.process_frame(track_frame, depth_data)

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

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cleanup()

        except Exception as e:
            print(f"[WARN ] Frame error: {e}")
    
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
    
    def _screen_pos(self):
        """Return already-mapped (screen_x, screen_y) for current hand.
        4% margin keeps hand in reliable stereo zone while maximising range.
        """
        nx = self.current_hand_data['index_tip']['normalized_x']
        ny = self.current_hand_data['index_tip']['normalized_y']
        return (self._map_to_screen(nx, 0.04, AppConfig.SCREEN_WIDTH),
                self._map_to_screen(ny, 0.04, AppConfig.SCREEN_HEIGHT))

    def _check_dwell(self, hovered_idx, air_push):
        """Returns True when a click should fire (air-push OR dwell 1.5 s).
        Also returns dwell_progress [0..1] for the HUD arc indicator.
        """
        now = time.time()
        if air_push:
            self._dwell_btn   = None
            self._dwell_start = 0.0
            return True, 0.0

        if hovered_idx is None:
            self._dwell_btn   = None
            self._dwell_start = 0.0
            return False, 0.0

        if self._dwell_btn != hovered_idx:
            self._dwell_btn   = hovered_idx
            self._dwell_start = now

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
        buttons  = self.menu_renderer.get_home_menu_buttons()
        sx, sy   = self._screen_pos()
        hovered  = self.menu_renderer.check_button_hover(buttons, sx, sy)
        clicked, dwell_p = self._check_dwell(hovered, air_push)
        self.hud.set_dwell_progress(dwell_p)

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
        
        # Check if keyboard overlay is active
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Open Palm toggles keyboard (global shortcut)
        if self.gesture_detector.detect_open_palm(self.current_hand_data):
            self.state_machine.show_keyboard_overlay('manual')
            return
        
        if self.gesture_detector.detect_swipe_up(self.current_hand_data, self.prev_hand_data):
            self.media_mode.volume_up()
            return
        
        if self.gesture_detector.detect_swipe_down(self.current_hand_data, self.prev_hand_data):
            self.media_mode.volume_down()
            return
    
    def handle_mouse_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        # Check if keyboard overlay is active
        if self.state_machine.has_keyboard_overlay():
            # Keyboard overlay takes priority - handle keyboard input
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        # Normal mouse mode
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        self.mouse_mode.move_cursor_screen(sx, sy)
        
        if air_push:
            self.mouse_mode.click()
            # Context-aware keyboard: check if click was in text input
            if self.mouse_mode.is_text_input_likely():
                self.state_machine.show_keyboard_overlay('text_input_click')
    
    def handle_keyboard_overlay(self, air_push, sx, sy):
        """
        Handle keyboard overlay input (appears over any primary mode).
        User can type or dismiss the keyboard.
        """
        # Check for dismiss gesture (swipe down or click outside keyboard area)
        if self.gesture_detector.detect_swipe_down(self.current_hand_data, self.prev_hand_data):
            self.state_machine.dismiss_keyboard_overlay()
            return
        
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
        
        # Check if keyboard overlay is active
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Open Palm toggles keyboard (global shortcut)
        if self.gesture_detector.detect_open_palm(self.current_hand_data):
            self.state_machine.show_keyboard_overlay('manual')
            return
        
        if self.gesture_detector.detect_swipe_right(self.current_hand_data, self.prev_hand_data):
            self.tab_mode.next_tab()
            return
        
        if self.gesture_detector.detect_swipe_left(self.current_hand_data, self.prev_hand_data):
            self.tab_mode.previous_tab()
            return
        
        if air_push:
            self.tab_mode.close_tab()

    def handle_window_mode(self, air_push):
        sx, sy = self._screen_pos()
        
        # Check if keyboard overlay is active
        if self.state_machine.has_keyboard_overlay():
            self.handle_keyboard_overlay(air_push, sx, sy)
            return
        
        if self._check_back(sx, sy, air_push, None):
            self.state_machine.go_to_home()
            return
        
        # Open Palm toggles keyboard (global shortcut)
        if self.gesture_detector.detect_open_palm(self.current_hand_data):
            self.state_machine.show_keyboard_overlay('manual')
            return
        
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

        if self.state_machine.is_home():
            # Check if keyboard overlay is active
            if self.state_machine.has_keyboard_overlay():
                buttons = self.keyboard_mode.get_keyboard_buttons(
                    AppConfig.SCREEN_WIDTH, 
                    AppConfig.SCREEN_HEIGHT
                )
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("HOME + KEYBOARD")
                self.hud.set_info_text("Type with keyboard | BACK button to dismiss")
            else:
                buttons = self.menu_renderer.get_home_menu_buttons()
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("HOME MENU")
                self.hud.set_info_text("Select a mode with air-push gesture")
            
        elif self.state_machine.is_media():
            # Check if keyboard overlay is active
            if self.state_machine.has_keyboard_overlay():
                buttons = self.keyboard_mode.get_keyboard_buttons(
                    AppConfig.SCREEN_WIDTH, 
                    AppConfig.SCREEN_HEIGHT
                )
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("MEDIA + KEYBOARD")
                self.hud.set_info_text("Type with keyboard | BACK button to dismiss")
            else:
                buttons = self.menu_renderer.get_media_menu_buttons()
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(None)
                self.hud.set_state_text("MEDIA CONTROL")
                self.hud.set_info_text("Swipe Up/Down for volume | Open Palm for keyboard")
            
        elif self.state_machine.is_mouse():
            # Check if keyboard overlay is active
            if self.state_machine.has_keyboard_overlay():
                buttons = self.keyboard_mode.get_keyboard_buttons(
                    AppConfig.SCREEN_WIDTH, 
                    AppConfig.SCREEN_HEIGHT
                )
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("MOUSE + KEYBOARD")
                self.hud.set_info_text("Type with keyboard | BACK button to dismiss")
            else:
                self.hud.set_buttons([])
                self.hud.set_state_text("AIR MOUSE")
                self.hud.set_info_text("Move hand to control cursor | Open Palm for keyboard")
            
        elif self.state_machine.is_tab():
            # Check if keyboard overlay is active
            if self.state_machine.has_keyboard_overlay():
                buttons = self.keyboard_mode.get_keyboard_buttons(
                    AppConfig.SCREEN_WIDTH, 
                    AppConfig.SCREEN_HEIGHT
                )
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("TAB + KEYBOARD")
                self.hud.set_info_text("Type with keyboard | BACK button to dismiss")
            else:
                buttons = self.menu_renderer.get_tab_menu_buttons()
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(None)
                self.hud.set_state_text("TAB SWITCHER")
                self.hud.set_info_text("Swipe Left/Right to switch tabs | Open Palm for keyboard")
            
        elif self.state_machine.is_window():
            # Check if keyboard overlay is active
            if self.state_machine.has_keyboard_overlay():
                buttons = self.keyboard_mode.get_keyboard_buttons(
                    AppConfig.SCREEN_WIDTH, 
                    AppConfig.SCREEN_HEIGHT
                )
                hovered = self.menu_renderer.check_button_hover(buttons, screen_x, screen_y)
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(hovered)
                self.hud.set_state_text("WINDOW + KEYBOARD")
                self.hud.set_info_text("Type with keyboard | BACK button to dismiss")
            else:
                buttons = self.menu_renderer.get_window_menu_buttons()
                self.hud.set_buttons(buttons)
                self.hud.set_hovered_button(None)
                self.hud.set_state_text("WINDOW SWITCHER")
                self.hud.set_info_text("Swipe to switch windows | Open Palm for keyboard")
    
    def cleanup(self):
        print("\nShutting down Aether-Link...")
        self.running = False
        
        if self.pipeline:
            self.pipeline.stop()
        
        self.depth_lock.cleanup()
        
        cv2.destroyAllWindows()
        
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        print("\n" + "="*60)
        print("  AETHER-LINK: Touchless Gesture Interface")
        print("="*60)
        print("  Controls:")
        print("    - Move hand in air (30-60cm from camera)")
        print("    - Air-push (push forward) to click/select")
        print("    - Top-left corner to go back to menu")
        print("    - Press 'Q' in OpenCV window to quit")
        print("="*60 + "\n")
        
        sys.exit(self.app.exec())

if __name__ == "__main__":
    aether = AetherLink()
    aether.run()
