# Aether-Link Quick Reference

## 🚀 Quick Start Commands

```bash
# Setup (first time only)
setup_env.bat

# Run application
run.bat

# Or manually
venv\Scripts\activate
python main.py
```

## 🎮 Gesture Controls

### Universal Gestures
| Gesture | Action | Description |
|---------|--------|-------------|
| **Move Hand** | Navigate | Move hand in air (30-60cm from camera) |
| **Air-Push** | Click/Select | Push index finger forward quickly |
| **Top-Left Corner + Air-Push** | Back to Menu | Navigate to top-left and push |

### Home Menu
| Button | Action |
|--------|--------|
| Media Control | Enter media mode |
| Air Mouse | Enter mouse mode |
| Virtual Keyboard | Enter keyboard mode |
| Exit | Close application |

### Media Mode
| Gesture | Action |
|---------|--------|
| Swipe Up | Volume Up (+2) |
| Swipe Down | Volume Down (-2) |
| Open Palm | Play/Pause |

### Mouse Mode
| Gesture | Action |
|---------|--------|
| Move Hand | Move Cursor |
| Air-Push | Left Click |

### Keyboard Mode
| Gesture | Action |
|---------|--------|
| Move Hand | Hover over keys |
| Air-Push | Type selected key |

## ⚙️ Configuration Quick Edit

**File**: `utils/config.py`

```python
# Distance range (mm)
INTERACTION_BOX_MIN = 300  # Closer = smaller number
INTERACTION_BOX_MAX = 600  # Farther = larger number

# Click sensitivity
AIR_CLICK_THRESHOLD = 50   # Lower = more sensitive
AIR_CLICK_TIME_WINDOW = 0.2  # Shorter = faster required

# Screen resolution
SCREEN_WIDTH = 1920   # Your screen width
SCREEN_HEIGHT = 1080  # Your screen height

# Smoothing (0.0 = no smoothing, 1.0 = max smoothing)
SMOOTHING_FACTOR = 0.7  # Higher = smoother but slower
```

## 🐛 Troubleshooting Quick Fixes

### Camera Not Working
```bash
# Check if camera is detected
python -c "from pyorbbecsdk import Pipeline; p = Pipeline(); print('OK')"

# Try different USB port (use USB 3.0)
# Restart computer
```

### Hand Not Detected
- Check lighting (not too dark, not too bright)
- Keep hand 30-60cm from camera
- Face palm toward camera
- Spread fingers slightly

### Laggy Performance
```python
# In utils/config.py, reduce resolution:
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Or increase smoothing:
SMOOTHING_FACTOR = 0.8
```

### HUD Not Visible
- Run as administrator
- Close fullscreen applications
- Check if PyQt6 installed: `pip show PyQt6`

## 📊 Performance Metrics

| Metric | Target | Acceptable |
|--------|--------|------------|
| FPS | 30 | 20-30 |
| Latency | <50ms | <100ms |
| CPU Usage | <30% | <50% |
| RAM Usage | ~50MB | <100MB |

## 🔧 Common Modifications

### Change Click Cooldown
**File**: `core/gesture_detector.py`
```python
self.click_cooldown = 0.3  # Seconds between clicks
```

### Change Volume Step
**File**: `utils/config.py`
```python
VOLUME_STEP = 2  # Number of volume increments
```

### Change Button Size
**File**: `utils/config.py`
```python
HUD_BUTTON_SIZE = 150  # Pixels
HUD_BUTTON_SPACING = 50  # Pixels between buttons
```

### Change Back Zone Size
**File**: `utils/config.py`
```python
BACK_BUTTON_ZONE_SIZE = 100  # Pixels (corner area)
```

## 📝 File Locations

| What | Where |
|------|-------|
| Main app | `main.py` |
| Config | `utils/config.py` |
| Gestures | `core/gesture_detector.py` |
| UI overlay | `ui/hud_overlay.py` |
| Media controls | `modes/media_mode.py` |
| Mouse controls | `modes/mouse_mode.py` |
| Keyboard | `modes/keyboard_mode.py` |

## 🎯 Gesture Detection Thresholds

```python
# Air-Push
DEPTH_CHANGE: 50mm forward in 0.2s

# Swipe Up/Down
Y_MOVEMENT: 30 pixels vertical

# Open Palm
EXTENDED_FINGERS: ≥3 fingers

# Back Zone
POSITION: Top-left 100×100 pixels
```

## 🔑 Keyboard Shortcuts

| Key | Action | Where |
|-----|--------|-------|
| Q | Quit | OpenCV window |
| ESC | Emergency exit | OpenCV window |

## 📦 Dependencies

```
pyorbbecsdk2>=2.0.18  # Camera SDK
opencv-python>=4.8.0  # Image processing
numpy>=1.24.0         # Math operations
mediapipe>=0.10.0     # Hand tracking
PyQt6>=6.5.0          # UI overlay
pyautogui>=0.9.54     # System control
```

## 🎨 UI Colors (RGB)

```python
# Ghost Cursor
GREEN = (0, 255, 0)

# Hovered Button
YELLOW = (255, 255, 0)

# Normal Button
BLUE = (100, 200, 255)

# Back Zone
RED = (255, 100, 100)

# Text
WHITE = (255, 255, 255)
```

## 📐 Coordinate Mapping

```python
# Hand to Screen
screen_x = hand_normalized_x × SCREEN_WIDTH
screen_y = hand_normalized_y × SCREEN_HEIGHT

# Camera to Hand
hand_x = landmark.x × frame_width
hand_y = landmark.y × frame_height
hand_z = depth_map[hand_y, hand_x]
```

## 🔄 State Transitions

```
HOME ──[select]──> MEDIA/MOUSE/KEYBOARD
ANY ───[back]────> HOME
```

## 💡 Tips & Tricks

1. **Better Tracking**: Keep hand flat, fingers spread
2. **Faster Clicks**: Reduce `AIR_CLICK_THRESHOLD` to 40
3. **Smoother Cursor**: Increase `SMOOTHING_FACTOR` to 0.8
4. **Larger Buttons**: Increase `HUD_BUTTON_SIZE` to 200
5. **Easier Back**: Increase `BACK_BUTTON_ZONE_SIZE` to 150

## 🆘 Emergency Commands

```bash
# Force quit (if frozen)
Ctrl + C  # In terminal

# Kill process (Windows)
taskkill /F /IM python.exe

# Restart camera
# Unplug and replug USB cable
```

## 📞 Debug Mode

Add to `main.py` for verbose output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎓 Learning Path

1. ✅ Run basic demo
2. ✅ Try all gestures
3. ✅ Adjust sensitivity
4. ✅ Customize UI
5. ✅ Add new gestures
6. ✅ Create custom modes

## 🔗 Useful Links

- MediaPipe Hands: https://google.github.io/mediapipe/solutions/hands
- Orbbec SDK: https://github.com/orbbec/pyorbbecsdk
- PyQt6 Docs: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- PyAutoGUI: https://pyautogui.readthedocs.io/

## 📊 System Requirements Check

```python
# Check Python version (need 3.10+)
python --version

# Check pip
pip --version

# Check camera
python -c "from pyorbbecsdk import Pipeline; print('Camera OK')"

# Check MediaPipe
python -c "import mediapipe; print('MediaPipe OK')"

# Check PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

## 🎯 Calibration Guide

1. **Distance**: Hold hand at comfortable distance, note depth value
2. **Sensitivity**: Adjust `AIR_CLICK_THRESHOLD` until comfortable
3. **Smoothing**: Adjust `SMOOTHING_FACTOR` for cursor stability
4. **Speed**: Practice air-push gesture at different speeds

## 🔐 Safety Features

- ✅ Click cooldown (prevents spam)
- ✅ Interaction box (only 30-60cm)
- ✅ Failsafe disabled (full screen access)
- ✅ Emergency exit (Q key)
- ✅ State validation (no invalid transitions)

## 📈 Performance Tuning

### For Speed
```python
SMOOTHING_FACTOR = 0.5  # Less smoothing
min_detection_confidence = 0.5  # Lower confidence
```

### For Accuracy
```python
SMOOTHING_FACTOR = 0.9  # More smoothing
min_detection_confidence = 0.8  # Higher confidence
```

### For Battery
```python
# Reduce FPS
self.timer.start(50)  # 20 FPS instead of 30
```

## 🎬 Demo Script

1. Start application
2. Show hand to camera (30-60cm)
3. Navigate to Media Control
4. Air-push to select
5. Swipe up for volume
6. Open palm to pause
7. Back to menu (top-left + push)
8. Try Air Mouse
9. Move cursor around
10. Air-push to click

---

**Last Updated**: April 16, 2026  
**Version**: 1.0.0  
**Quick Help**: Press Q to quit, top-left corner to go back
