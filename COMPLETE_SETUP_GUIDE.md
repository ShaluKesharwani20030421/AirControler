# Aether-Link Complete Setup Guide
## Fresh Installation on New Machine/Laptop

**Version**: 2.0 (with 3D Biometric Security)  
**Last Updated**: April 18, 2026  
**Platform**: Windows 10/11

---

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Software Prerequisites](#software-prerequisites)
3. [Python Installation](#python-installation)
4. [Project Setup](#project-setup)
5. [Library Installation](#library-installation)
6. [Hardware Setup](#hardware-setup)
7. [First Run](#first-run)
8. [Biometric Signature Setup](#biometric-signature-setup)
9. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit) or Windows 11
- **RAM**: 8 GB
- **CPU**: Intel i5 (8th gen) or AMD Ryzen 5 or better
- **USB**: USB 3.0 port (for Orbbec camera)
- **Storage**: 2 GB free space

### Recommended Requirements
- **OS**: Windows 11
- **RAM**: 16 GB
- **CPU**: Intel i7 (10th gen) or AMD Ryzen 7
- **GPU**: Integrated graphics (for MediaPipe acceleration)
- **USB**: USB 3.1/3.2 port

---

## 📦 Software Prerequisites

### 1. Microsoft Visual C++ Redistributable
**Required for**: OpenCV, NumPy, SciPy

**Download**: https://aka.ms/vs/17/release/vc_redist.x64.exe

**Installation**:
```powershell
# Download and run the installer
# Accept license and install
```

### 2. Git (Optional, for cloning)
**Version**: 2.40.0 or later

**Download**: https://git-scm.com/download/win

---

## 🐍 Python Installation

### Step 1: Download Python
**Version Required**: **Python 3.12.x** (Tested with 3.12.0)

**Download Link**: https://www.python.org/downloads/release/python-3120/
- Select: "Windows installer (64-bit)"

### Step 2: Install Python
```
1. Run python-3.12.0-amd64.exe
2. ✅ CHECK "Add python.exe to PATH"
3. Click "Install Now"
4. Wait for installation
5. Click "Close"
```

### Step 3: Verify Installation
```powershell
python --version
# Expected output: Python 3.12.0

pip --version
# Expected output: pip 23.x.x from ...
```

---

## 📁 Project Setup

### Method 1: Download ZIP
```powershell
# 1. Download project ZIP
# 2. Extract to: C:\Users\YourName\Documents\Project\Aether-Link
# 3. Open PowerShell in that directory
cd C:\Users\YourName\Documents\Project\Aether-Link
```

### Method 2: Git Clone
```powershell
cd C:\Users\YourName\Documents\Project
git clone <repository-url> Aether-Link
cd Aether-Link
```

---

## 📚 Library Installation

### Step 1: Create Virtual Environment (Recommended)
```powershell
# Navigate to project directory
cd C:\Users\YourName\Documents\Project\Aether-Link

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 3: Install Core Dependencies
```powershell
# Install from requirements.txt
pip install -r requirements.txt
```

### Step 4: Install Security Dependencies (NEW)
```powershell
# For 3D Biometric Signature System
pip install fastdtw==0.3.4
pip install scipy==1.11.4
```

### Step 5: Install Optional Dependencies
```powershell
# For better text input detection in Mouse mode
pip install pygetwindow==0.0.9
```

---

## 📝 Complete Library Versions

### requirements.txt
```txt
# Core Dependencies
pyorbbecsdk2==2.0.18
opencv-python==4.8.1.78
numpy==1.26.2
mediapipe==0.10.14
PyQt6==6.6.1
pyautogui==0.9.54

# Security (NEW)
fastdtw==0.3.4
scipy==1.11.4

# Optional
pygetwindow==0.0.9
```

### Detailed Version Table

| Library | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.12.0 | Runtime environment |
| **pyorbbecsdk2** | 2.0.18 | Orbbec Gemini 335 camera SDK |
| **opencv-python** | 4.8.1.78 | Image processing |
| **numpy** | 1.26.2 | Numerical operations |
| **mediapipe** | 0.10.14 | Hand tracking ML model |
| **PyQt6** | 6.6.1 | Transparent HUD overlay |
| **pyautogui** | 0.9.54 | System control automation |
| **fastdtw** | 0.3.4 | Dynamic Time Warping for signature verification |
| **scipy** | 1.11.4 | Scientific computing (DTW distance) |
| **pygetwindow** | 0.0.9 | Window detection (optional) |

---

## 🎥 Hardware Setup

### Orbbec Gemini 335 Camera

#### Step 1: Install Orbbec Driver
```powershell
# Download Orbbec Viewer from:
# https://www.orbbec.com/developers/orbbec-viewer/

# Install Orbbec Viewer (includes drivers)
# Run OrbbecViewer_vX.X.X_win_x64.exe
```

#### Step 2: Connect Camera
```
1. Connect Gemini 335 to USB 3.0 port (blue port)
2. Wait for Windows to recognize device
3. Open Orbbec Viewer to test camera
4. Verify depth and color streams work
```

#### Step 3: Camera Positioning
```
- Height: Eye level or slightly above
- Distance: 50-100 cm from user
- Angle: Pointing slightly downward (10-15°)
- Lighting: Avoid direct sunlight or bright backlighting
```

---

## 🚀 First Run

### Step 1: Verify Project Structure
```powershell
# Check if all directories exist
ls

# Expected output:
# core/
# modes/
# ui/
# utils/
# security/  ← NEW
# main.py
# requirements.txt
```

### Step 2: Test Camera Connection
```powershell
python -c "from pyorbbecsdk import Pipeline; print('Camera SDK OK')"
```

### Step 3: Run Application (Without Security)
```powershell
python main.py
```

**Expected Output**:
```
Screen: 1920x1080
Camera : Orbbec Gemini 335  FW: 1.4.60
Depth  : 640x480 @ 30fps  fmt=OBFormat.Y16
Color  : 640x480 @ 30fps  fmt=OBFormat.RGB
D2C    : HW alignment enabled
Camera ready — streaming started.

============================================================
  AETHER-LINK: Touchless Gesture Interface
============================================================
```

---

## 🔐 Biometric Signature Setup

### Step 1: Record Your Signature

Create a signature recording script:

**File**: `record_signature.py`
```python
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pyorbbecsdk import Pipeline, Config as OBConfig, OBSensorType, OBFormat
from core.depth_lock import DepthLock
from security.signature_recorder import SignatureRecorder
from utils.camera_utils import process_depth_frame, process_color_frame
import cv2

class SignatureRecordingApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.pipeline = Pipeline()
        self.depth_lock = DepthLock()
        self.recorder = SignatureRecorder(duration=3.0, min_z_variance=100.0)
        
        # Initialize camera
        config = OBConfig()
        d_profiles = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        d_profile = d_profiles.get_video_stream_profile(640, 0, OBFormat.Y16, 30)
        config.enable_stream(d_profile)
        
        c_profiles = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        c_profile = c_profiles.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
        config.enable_stream(c_profile)
        
        self.pipeline.start(config)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(33)
        
        print("\n" + "="*60)
        print("  3D BIOMETRIC SIGNATURE RECORDING")
        print("="*60)
        print("\nInstructions:")
        print("1. Press SPACE to start recording")
        print("2. Draw your signature in 3D space for 3 seconds")
        print("3. Move your finger in all 3 dimensions (X, Y, Z)")
        print("4. Press 'Q' to quit\n")
    
    def process_frame(self):
        frames = self.pipeline.wait_for_frames(100)
        if frames is None:
            return
        
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if depth_frame is None or color_frame is None:
            return
        
        _, depth_data = process_depth_frame(depth_frame, 150, 1200)
        color_image = process_color_frame(color_frame)
        
        if color_image is None or depth_data is None:
            return
        
        hand_data = self.depth_lock.process_frame(color_image, depth_data)
        
        if hand_data:
            if self.recorder.recording:
                complete = self.recorder.add_point(hand_data)
                if complete:
                    self.recorder.save_signature('signatures/my_signature.json')
                    print("\n✓ Signature saved! You can now close the window.")
        
        # Display
        display = color_image.copy()
        if hand_data:
            display = self.depth_lock.draw_hand_landmarks(display, hand_data)
        
        if self.recorder.recording:
            progress = self.recorder.get_progress()
            cv2.putText(display, f"RECORDING: {progress*100:.0f}%", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(display, "Press SPACE to record", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Signature Recording", display)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and not self.recorder.recording:
            self.recorder.start_recording()
        elif key == ord('q'):
            self.cleanup()
    
    def cleanup(self):
        self.pipeline.stop()
        cv2.destroyAllWindows()
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        return self.app.exec()

if __name__ == '__main__':
    app = SignatureRecordingApp()
    sys.exit(app.run())
```

**Run**:
```powershell
python record_signature.py
```

### Step 2: Enable Security in Main App

**Edit `main.py`**:
```python
# Line ~46: Change state machine initialization
self.state_machine = StateMachine(require_auth=True)  # Enable security

# Add signature verifier
from security import SignatureVerifier
self.signature_verifier = SignatureVerifier(
    reference_path='signatures/my_signature.json',
    threshold=50.0
)
```

### Step 3: Test Verification
```powershell
python main.py
# App will start in LOCKED state
# Draw your signature to unlock
```

---

## 🐛 Troubleshooting

### Issue 1: Camera Not Detected
```powershell
# Check USB connection
# Verify in Device Manager: "Orbbec Depth Sensor"
# Try different USB 3.0 port
# Reinstall Orbbec drivers
```

### Issue 2: MediaPipe Import Error
```powershell
# Reinstall mediapipe
pip uninstall mediapipe
pip install mediapipe==0.10.14
```

### Issue 3: PyQt6 DPI Warning
```
# This is a warning, not an error - app will still work
# To suppress: Add to main.py before QApplication:
import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
```

### Issue 4: fastdtw Installation Fails
```powershell
# Install Visual C++ Build Tools first
# Or use pre-built wheel:
pip install --only-binary :all: fastdtw
```

### Issue 5: Signature Always Rejected
```
# Check Z-variance in recording:
# - Move hand closer/farther during signature
# - Ensure 3D movement, not just 2D
# - Lower threshold if needed:
SignatureVerifier(threshold=100.0)  # More lenient
```

---

## 📊 Performance Optimization

### For Low-End Systems
```python
# In main.py, reduce frame rate:
self.timer.start(50)  # 20 FPS instead of 30

# In depth_lock.py, reduce tracking confidence:
min_tracking_confidence=0.2
```

### For High-End Systems
```python
# Enable GPU acceleration (if available):
# MediaPipe will auto-detect and use GPU
```

---

## 🔄 Updating the Project

### Update Python Libraries
```powershell
pip install --upgrade -r requirements.txt
```

### Update Orbbec SDK
```
1. Download latest Orbbec Viewer
2. Install (will update drivers)
3. Test camera in Orbbec Viewer
4. Restart Aether-Link
```

---

## 📞 Support & Resources

### Official Documentation
- Orbbec SDK: https://www.orbbec.com/developers/
- MediaPipe: https://google.github.io/mediapipe/
- PyQt6: https://www.riverbankcomputing.com/static/Docs/PyQt6/

### Common Commands
```powershell
# Check Python version
python --version

# List installed packages
pip list

# Check package version
pip show mediapipe

# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

---

## ✅ Setup Checklist

- [ ] Python 3.12.0 installed
- [ ] Visual C++ Redistributable installed
- [ ] Virtual environment created and activated
- [ ] All libraries installed from requirements.txt
- [ ] Security libraries installed (fastdtw, scipy)
- [ ] Orbbec drivers installed
- [ ] Camera connected and tested in Orbbec Viewer
- [ ] Project runs without errors
- [ ] Biometric signature recorded
- [ ] Signature verification tested

---

**Setup Complete!** 🎉

You're now ready to use Aether-Link with 3D Biometric Security.
