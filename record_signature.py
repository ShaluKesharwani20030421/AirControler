"""
3D Biometric Signature Recording Utility
Standalone script to record your unique 3D hand signature.
"""

import sys
import cv2
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pyorbbecsdk import (
    Pipeline, Config as OBConfig,
    OBSensorType, OBFormat, OBFrameType, OBAlignMode
)

from core.depth_lock import DepthLock
from security.signature_recorder import SignatureRecorder
from utils.camera_utils import process_depth_frame, process_color_frame


class SignatureRecordingApp:
    """
    Simple app to record 3D biometric signatures.
    
    Usage:
    1. Run this script
    2. Press SPACE to start recording
    3. Draw your signature in 3D space for 3 seconds
    4. Signature auto-saves when complete
    """
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Initialize camera
        self.pipeline = Pipeline()
        self.init_camera()
        
        # Initialize components
        self.depth_lock = DepthLock()
        self.recorder = SignatureRecorder(
            duration=3.0,           # 3 seconds
            min_z_variance=100.0    # Minimum depth variation to prevent spoofing
        )
        
        # Timer for frame processing
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(33)  # ~30 FPS
        
        self.print_instructions()
    
    def init_camera(self):
        """Initialize Orbbec Gemini 335 camera."""
        config = OBConfig()
        
        # Depth stream
        d_profiles = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        d_profile = d_profiles.get_video_stream_profile(640, 0, OBFormat.Y16, 30)
        config.enable_stream(d_profile)
        
        # Color stream
        c_profiles = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        c_profile = c_profiles.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
        config.enable_stream(c_profile)
        
        # Enable D2C alignment
        try:
            config.set_align_mode(OBAlignMode.HW_MODE)
        except:
            pass
        
        self.pipeline.start(config)
        print("[Camera] Orbbec Gemini 335 initialized")
    
    def print_instructions(self):
        """Print usage instructions."""
        print("\n" + "="*70)
        print("  3D BIOMETRIC SIGNATURE RECORDING")
        print("="*70)
        print("\n📝 Instructions:")
        print("  1. Position your hand in front of the camera (30-60 cm)")
        print("  2. Press SPACE to start recording")
        print("  3. Draw your signature in 3D space for 3 seconds")
        print("  4. Move your finger in ALL 3 dimensions (X, Y, Z)")
        print("  5. The signature will auto-save when complete")
        print("\n⚠️  Important:")
        print("  - Move your hand FORWARD and BACKWARD (Z-axis) during signature")
        print("  - Flat 2D signatures will be rejected (anti-spoofing)")
        print("  - You need at least 100 mm² Z-variance")
        print("\n🎮 Controls:")
        print("  SPACE = Start recording")
        print("  Q     = Quit")
        print("\n" + "="*70 + "\n")
    
    def process_frame(self):
        """Process each camera frame."""
        try:
            frames = self.pipeline.wait_for_frames(100)
            if frames is None:
                return
            
            # Get frames
            depth_frame = frames.get_frame(OBFrameType.DEPTH_FRAME)
            color_frame = frames.get_frame(OBFrameType.COLOR_FRAME)
            
            if depth_frame is None or color_frame is None:
                return
            
            # Process frames
            _, depth_data = process_depth_frame(depth_frame, 150, 1200)
            color_image = process_color_frame(color_frame)
            
            if color_image is None or depth_data is None:
                return
            
            # Detect hand
            hand_data = self.depth_lock.process_frame(color_image, depth_data)
            
            # Record signature points
            if hand_data and self.recorder.recording:
                complete = self.recorder.add_point(hand_data)
                if complete:
                    # Save signature
                    self.recorder.save_signature('signatures/my_signature.json')
                    print("\n✅ Signature saved successfully!")
                    print("   File: signatures/my_signature.json")
                    print("\n   You can now:")
                    print("   1. Close this window (press Q)")
                    print("   2. Enable security in main.py")
                    print("   3. Run Aether-Link with biometric authentication\n")
            
            # Visualize
            self.display_frame(color_image, hand_data)
            
        except Exception as e:
            print(f"[Error] {e}")
    
    def display_frame(self, color_image, hand_data):
        """Display camera feed with recording status."""
        display = color_image.copy()
        
        # Draw hand landmarks
        if hand_data:
            display = self.depth_lock.draw_hand_landmarks(display, hand_data)
        
        # Recording status
        if self.recorder.recording:
            progress = self.recorder.get_progress()
            # Red recording indicator
            cv2.putText(display, f"● RECORDING: {progress*100:.0f}%", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            
            # Progress bar
            bar_width = int(600 * progress)
            cv2.rectangle(display, (10, 60), (610, 90), (100, 100, 100), 2)
            cv2.rectangle(display, (10, 60), (10 + bar_width, 90), (0, 0, 255), -1)
            
            # Point count
            cv2.putText(display, f"Points: {len(self.recorder.signature_path)}", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            # Waiting for user
            cv2.putText(display, "Press SPACE to start recording", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if hand_data:
                cv2.putText(display, "Hand detected ✓", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(display, "No hand detected", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow("3D Signature Recording", display)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and not self.recorder.recording:
            self.recorder.start_recording()
        elif key == ord('q'):
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown."""
        print("\n[Shutdown] Closing camera...")
        self.pipeline.stop()
        cv2.destroyAllWindows()
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        """Run the application."""
        return self.app.exec()


if __name__ == '__main__':
    app = SignatureRecordingApp()
    sys.exit(app.run())
