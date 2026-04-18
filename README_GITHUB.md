# 🌟 Aether-Link: Touchless Gesture Interface

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.33-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

**Control your computer with magical hand gestures in 3D space**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

**Aether-Link** is a revolutionary touchless interface that transforms hand gestures into computer commands using depth-aware 3D tracking. No mouse, no keyboard, no touch—just your hands in the air.

### ✨ What Makes It Special

- **🔒 Biometric Security**: 3D air-signature authentication with anti-spoofing
- **🎨 Premium UI**: Glassmorphic HUD with energy orb cursor and ripple effects
- **🎯 Precise Control**: Triple-layer EMA smoothing for comfortable cursor movement
- **⌨️ Universal Keyboard**: Access virtual keyboard from anywhere with Open Palm gesture
- **🖱️ Smart Mouse**: Auto-detects text fields and shows keyboard automatically
- **🎵 Media Control**: Swipe gestures for volume, play/pause
- **🪟 Window Management**: Task View, minimize, switch windows with gestures

---

## 🚀 Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **3D Hand Tracking** | MediaPipe Tasks API with Orbbec Gemini 335 depth camera |
| **Air-Push Click** | Natural "push forward" gesture for clicking (30mm depth change) |
| **Mirror-Mode Cursor** | Hand right = cursor right (intuitive control) |
| **Dwell-to-Click** | Hover 1.5s on buttons as alternative to air-push |
| **Signature Lock** | Draw 3D pattern in air to unlock system |

### 5 Modes + Keyboard Overlay

#### 🏠 HOME Mode
- 2×3 grid menu (Media, Mouse, Tab, Window, Keyboard, Exit)
- Air-push or dwell to select

#### 🎵 MEDIA Mode
- **Swipe Up**: Volume Up
- **Swipe Down**: Volume Down
- **Open Palm**: Show Keyboard

#### 🖱️ MOUSE Mode
- Move hand to control cursor (1.5x speed)
- Air-push to click
- Auto-keyboard on text field click
- **Open Palm**: Show Keyboard

#### 🔄 TAB Mode
- **Swipe Right**: Next Tab
- **Swipe Left**: Previous Tab
- **Air-Push**: Close Tab
- **Open Palm**: Show Keyboard

#### 🪟 WINDOW Mode
- **Swipe Right**: Next Window
- **Swipe Left**: Previous Window
- **Swipe Up**: Task View
- **Swipe Down**: Minimize
- **Open Palm**: Show Keyboard

#### ⌨️ KEYBOARD Overlay
- Full QWERTY layout
- Accessible from **ANY mode** via Open Palm
- Auto-appears in Mouse mode on text field click
- BACK button to dismiss

---

## 🎬 Demo

### Gesture Recognition
```
Air-Push:    👋 → 👊 (push forward 30mm)
Swipe Right: 👋 → 👉 (60px horizontal)
Swipe Up:    👋 → ☝️ (50px vertical)
Open Palm:   🖐️ (3+ fingers extended)
```

### Signature Lock
```
1. Air-push to start recording
2. Draw pattern in 3D space (3 seconds)
3. Move forward/backward (depth required)
4. System verifies using DTW algorithm
5. Unlocks if pattern matches (threshold: 350)
```

---

## 📦 Installation

### Prerequisites

- **Hardware**: Orbbec Gemini 335 depth camera
- **OS**: Windows 10/11
- **Python**: 3.12 or 3.13

### Quick Setup

```powershell
# 1. Clone repository
git clone https://github.com/ShaluKesharwani20030421/AirControler.git
cd AirControler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download MediaPipe model (if not included)
# The hand_landmarker.task model should be in models/ folder

# 4. Connect Orbbec camera

# 5. Run!
python main.py
```

### Manual Installation

```powershell
pip install mediapipe==0.10.33
pip install opencv-python==4.10.0.84
pip install numpy==2.0.2
pip install PyQt6==6.8.0
pip install pyautogui==0.9.54
pip install pyorbbecsdk2==2.1.11
pip install pygetwindow==0.0.9
pip install fastdtw==0.3.4
pip install scipy==1.14.1
```

---

## 🎮 Usage

### First Time Setup

#### 1. Record Your Signature (Optional)
```powershell
python record_signature.py
```
- Press **SPACE** to start
- Draw a 3D pattern for 3 seconds
- Move hand forward/backward (depth required)
- Pattern saved to `signatures/my_signature.json`

#### 2. Run Main App
```powershell
python main.py
```

### Controls

| Action | Gesture |
|--------|---------|
| **Click/Select** | Air-push (push forward 30mm) |
| **Alternative Click** | Dwell 1.5s on button |
| **Show Keyboard** | Open Palm (any mode) |
| **Go Back** | BACK button (top center) |
| **Quit** | Press Q in OpenCV window |

### Keyboard Access

**3 Ways to Access**:
1. HOME menu → Click "Keyboard" button
2. **Any mode** → Open Palm gesture
3. Mouse mode → Click text field (auto)

**To Dismiss**:
- Press BACK button (top center)
- Or Open Palm again (toggle)

---

## 🔧 Configuration

### Cursor Speed
Edit `modes/mouse_mode.py` line 23:
```python
self.MOUSE_SMOOTH = 0.3  # Lower = faster (0.1-0.9)
```

Edit `core/depth_lock.py` line 75:
```python
self.CURSOR_SMOOTH = 0.25  # Lower = faster (0.1-0.9)
```

### Gesture Sensitivity
Edit `core/gesture_detector.py`:
```python
AIR_CLICK_THRESHOLD = 30      # mm (lower = more sensitive)
SWIPE_X_THRESHOLD = 60        # px (lower = easier swipes)
SWIPE_Y_THRESHOLD = 50        # px
swipe_cooldown = 0.8          # seconds between swipes
```

### Signature Security
Edit `main.py` line 63:
```python
threshold=350.0,  # DTW distance (lower = stricter)
```

**Recommended values**:
- **100-200**: Very strict (exact match)
- **250-350**: Balanced (similar pattern)
- **400-600**: Forgiving (rough similarity)

---

## 📁 Project Structure

```
Aether-Link/
├── main.py                    # Main application entry
├── record_signature.py        # Signature recording tool
├── requirements.txt           # Python dependencies
│
├── core/
│   ├── depth_lock.py         # MediaPipe + depth fusion
│   ├── gesture_detector.py   # Gesture recognition
│   └── state_machine.py      # App state management
│
├── modes/
│   ├── media_mode.py         # Media control
│   ├── mouse_mode.py         # Air mouse
│   ├── keyboard_mode.py      # Virtual keyboard
│   ├── tab_mode.py           # Tab switching
│   └── window_mode.py        # Window management
│
├── ui/
│   ├── hud_overlay.py        # Transparent HUD (PyQt6)
│   └── menu_renderer.py      # Button layouts
│
├── security/
│   ├── signature_recorder.py # 3D signature capture
│   └── signature_verifier.py # DTW verification
│
├── utils/
│   ├── camera_utils.py       # Orbbec frame processing
│   └── config.py             # Global configuration
│
└── models/
    └── hand_landmarker.task  # MediaPipe model
```

---

## 🛠️ Troubleshooting

### Camera Not Detected
```powershell
# Check camera connection
python -c "from pyorbbecsdk2 import Context; print(Context().query_devices())"
```

### Hand Not Tracking
- **Lighting**: Ensure bright, even lighting
- **Distance**: Keep hand 40-60cm from camera
- **Position**: Show palm facing camera
- **Background**: Avoid cluttered backgrounds

### Cursor Too Slow/Fast
```python
# Edit mouse_mode.py line 23
self.MOUSE_SMOOTH = 0.3  # Decrease for faster, increase for slower
```

### Signature Always Rejected
```powershell
# Delete and re-record
del signatures\my_signature.json
python record_signature.py

# Or increase threshold in main.py line 63
threshold=500.0,  # More forgiving
```

### Locked Out?
```powershell
# Emergency bypass
del signatures\my_signature.json
python main.py  # Will start unlocked
```

---

## 📚 Documentation

### Detailed Guides
- `COMPLETE_SETUP_GUIDE.md` - Step-by-step installation
- `COMPLETE_TESTING_GUIDE.md` - Testing procedures
- `SYSTEM_STATUS.md` - Current system status
- `UNLOCK_HELP.md` - Signature lock help
- `KEYBOARD_FIX.md` - Keyboard troubleshooting
- `FIXES_SUMMARY.md` - Recent fixes

### Quick References
- `INSTALL_COMMANDS.md` - Installation commands
- `RESET_SIGNATURE.bat` - Emergency unlock tool

---

## 🎨 Technical Highlights

### Depth-Lock Algorithm
- **Stereo depth fusion**: MediaPipe landmarks + Orbbec depth map
- **15×15 median filter**: Robust depth sampling
- **Triple EMA smoothing**: Depth (0.6) → Normalized (0.25) → Screen (0.3)
- **Mirror-mode X-axis**: Intuitive left/right control

### Gesture Recognition
- **Air-Push**: 30mm depth change in 350ms
- **Swipes**: 50-60px movement with 0.8s cooldown
- **Open Palm**: 3+ fingers extended, 1.2s cooldown
- **Dwell**: 1.5s hover with circular progress indicator

### Biometric Security
- **3D signature**: Index finger tip path (X, Y, Z)
- **DTW verification**: Dynamic Time Warping distance
- **Anti-spoofing**: Minimum Z-variance 100mm²
- **Threshold**: Normalized DTW distance < 350

### UI/UX
- **Glassmorphic design**: Semi-transparent blur effects
- **Energy orb cursor**: Pulsating glow with sparkles
- **Ripple animations**: Expanding circles on air-push
- **Dwell timer**: Circular arc with gradient fill
- **State-based HUD**: Context-aware button layouts

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Shalu Kesharwani**
- GitHub: [@ShaluKesharwani20030421](https://github.com/ShaluKesharwani20030421)

---

## 🙏 Acknowledgments

- **MediaPipe** - Hand landmark detection
- **Orbbec** - Depth camera SDK
- **PyQt6** - Transparent overlay UI
- **FastDTW** - Signature verification

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Intel i5 8th Gen | Intel i7 10th Gen+ |
| **RAM** | 8 GB | 16 GB |
| **GPU** | Integrated | Dedicated (optional) |
| **Camera** | Orbbec Gemini 335 | Orbbec Gemini 335 |
| **OS** | Windows 10 | Windows 11 |
| **Python** | 3.12 | 3.13 |

---

## 🔮 Future Enhancements

- [ ] Multi-hand gesture support
- [ ] Custom gesture recording
- [ ] Linux/macOS support
- [ ] Voice command integration
- [ ] Gesture macro system
- [ ] Cloud signature sync
- [ ] Mobile companion app

---

<div align="center">

**Made with ❤️ and ✨ magic**

⭐ Star this repo if you found it helpful!

</div>
