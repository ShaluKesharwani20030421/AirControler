# Aether-Link Setup Guide

## Prerequisites

1. **Hardware**:
   - Orbbec Gemini 335 depth camera
   - Windows PC with USB 3.0 port
   - Minimum 8GB RAM recommended

2. **Software**:
   - Python 3.10 or higher
   - Windows 10/11

## Installation Steps

### 1. Install Orbbec SDK

The Orbbec SDK should already be installed on your system. If not:
- Download from: https://github.com/orbbec/pyorbbecsdk
- Follow the installation instructions for Windows

### 2. Setup Python Environment

Run the setup script:
```bash
setup_env.bat
```

This will:
- Create a virtual environment
- Install all required dependencies
- Configure the project

### 3. Connect the Camera

1. Connect your Orbbec Gemini 335 to a USB 3.0 port
2. Wait for Windows to recognize the device
3. Verify the camera is detected by running:
   ```bash
   venv\Scripts\activate
   python -c "from pyorbbecsdk import Pipeline; p = Pipeline(); print('Camera detected!')"
   ```

## Running Aether-Link

### Quick Start

Simply double-click `run.bat` or run:
```bash
run.bat
```

### Manual Start

1. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Usage Instructions

### Interaction Zone

Position your hand **30-60cm** from the camera for optimal tracking.

### Gestures

1. **Navigation**: Move your hand in the air
2. **Select/Click**: Push your index finger forward (air-push)
3. **Back to Menu**: Air-push in the top-left corner of the screen

### Modes

#### Home Menu
- Select from 4 options: Media Control, Air Mouse, Virtual Keyboard, Exit

#### Media Control Mode
- **Swipe Up**: Increase volume
- **Swipe Down**: Decrease volume
- **Open Palm**: Play/Pause

#### Air Mouse Mode
- **Move Hand**: Control cursor position
- **Air-Push**: Left click

#### Virtual Keyboard Mode
- **Move Hand**: Hover over keys
- **Air-Push**: Type the selected key

## Troubleshooting

### Camera Not Detected
- Ensure the camera is connected to a USB 3.0 port
- Check Device Manager for Orbbec devices
- Try a different USB port
- Restart the computer

### Hand Tracking Issues
- Ensure adequate lighting
- Keep hand within 30-60cm range
- Face your palm toward the camera
- Avoid rapid movements initially

### Performance Issues
- Close other applications using the camera
- Reduce screen resolution in config.py
- Check CPU usage

### HUD Not Visible
- Ensure PyQt6 is installed correctly
- Check if other applications are in fullscreen mode
- Try running as administrator

## Configuration

Edit `utils/config.py` to customize:

```python
INTERACTION_BOX_MIN = 300  # Minimum distance (mm)
INTERACTION_BOX_MAX = 600  # Maximum distance (mm)
AIR_CLICK_THRESHOLD = 50   # Depth change for click (mm)
SCREEN_WIDTH = 1920        # Your screen width
SCREEN_HEIGHT = 1080       # Your screen height
```

## Keyboard Shortcuts

- **Q**: Quit application (in OpenCV window)
- **ESC**: Emergency exit

## Tips for Best Experience

1. **Lighting**: Use consistent, moderate lighting
2. **Background**: Plain backgrounds work best
3. **Hand Position**: Keep fingers spread for better tracking
4. **Calibration**: Practice the air-push gesture a few times
5. **Smoothness**: Make deliberate, smooth movements

## Advanced Configuration

### Adjusting Sensitivity

In `core/gesture_detector.py`:
- Modify `click_cooldown` for click frequency
- Adjust swipe thresholds for gesture sensitivity

### Customizing UI

In `ui/hud_overlay.py`:
- Change colors, opacity, and button sizes
- Modify overlay positions

### Adding Custom Gestures

1. Add detection logic in `core/gesture_detector.py`
2. Handle the gesture in `main.py`
3. Update the UI in `ui/menu_renderer.py`

## Support

For issues or questions:
1. Check the console output for error messages
2. Review the troubleshooting section
3. Ensure all dependencies are installed correctly

## Performance Optimization

- Run in Release mode (not Debug)
- Close unnecessary background applications
- Ensure good USB 3.0 connection
- Update graphics drivers

## System Requirements

**Minimum**:
- CPU: Intel i5 or equivalent
- RAM: 8GB
- USB: 3.0 port
- OS: Windows 10

**Recommended**:
- CPU: Intel i7 or equivalent
- RAM: 16GB
- USB: 3.1/3.2 port
- OS: Windows 11
