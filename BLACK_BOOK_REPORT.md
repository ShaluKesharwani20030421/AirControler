# Aether-Link Project Black Book Report

## 1. Project Title
**Aether-Link: Touchless Gesture Interface using Orbbec Gemini 335**

## 2. Executive Summary
Aether-Link is a real-time, touchless human-computer interaction system that enables users to control desktop functions through hand gestures in free space. The project combines RGB/depth sensing from the Orbbec Gemini 335 camera, MediaPipe hand landmark estimation, gesture interpretation logic, a PyQt6 HUD, and system action modules (mouse, keyboard, media control).

The system was developed to provide a more natural and hygienic interaction model where users can navigate menus, click, type, and issue media commands without physically touching input devices.

## 3. Problem Statement
Traditional interaction (mouse/keyboard/touch) is not ideal in all scenarios, especially where:
- touchless control is preferred,
- accessibility support is needed,
- users require natural gesture-based interaction,
- system operation should remain possible from a short stand-off distance.

The main engineering challenge was achieving **stable and usable gesture control** under practical hand movements, including edge-of-screen navigation and reliable selection actions.

## 4. Project Objectives
- Build a robust gesture-controlled desktop interaction system.
- Integrate depth-aware hand tracking for better interaction confidence.
- Provide multi-mode control: Home, Media, Mouse, Keyboard.
- Deliver real-time visual feedback through an on-screen HUD.
- Minimize false triggers and improve user experience for repeated interactions.

## 5. Scope and Deliverables
### In Scope
- Camera stream acquisition and processing (Orbbec SDK).
- Hand landmark detection and depth mapping.
- Gesture detection (air-push, swipe up/down, open palm).
- State machine-driven application flow.
- Interactive HUD and menu rendering.
- Configuration-driven thresholds and behavior tuning.

### Out of Scope
- Multi-user simultaneous interaction.
- Cloud connectivity and remote inference.
- Full gesture personalization pipeline (future enhancement).

## 6. Technology Stack
- **Language**: Python 3.12
- **Camera SDK**: `pyorbbecsdk2`
- **Computer Vision**: OpenCV
- **Hand Tracking ML**: MediaPipe Hands
- **Math/Data**: NumPy
- **HUD/UI**: PyQt6
- **Desktop Automation**: PyAutoGUI

## 7. Hardware Platform
- **Primary Sensor**: Orbbec Gemini 335
- **Stream setup used**:
  - Depth: `640x480 @ 30 FPS` (`Y16`)
  - Color (preferred tracking source): `640x480 @ 30 FPS`
- **Depth-Color Alignment**: Hardware D2C alignment enabled where available.

## 8. System Architecture Overview
Aether-Link follows a modular architecture:

1. **Acquisition Layer**
   - Camera pipeline initialization and frame sync
   - Depth + color/IR frame retrieval

2. **Perception Layer**
   - Hand landmark extraction (MediaPipe)
   - Landmark-to-depth mapping (Depth-Lock)
   - Smoothed 3D landmark state estimation

3. **Interpretation Layer**
   - Gesture detection and temporal filtering
   - Cooldowns and trigger validation

4. **Control Layer**
   - State machine: Home / Media / Mouse / Keyboard
   - Mode-specific action execution

5. **Presentation Layer**
   - Transparent HUD overlay
   - Cursor, buttons, hover, depth/status feedback

## 9. Core Functional Modules
### 9.1 `main.py`
- Application entry point
- Camera setup and stream selection
- Frame processing loop
- Gesture handling and mode routing
- HUD updates and debug views

### 9.2 `core/depth_lock.py`
- Maps hand landmarks to depth map values
- Uses smoothing and robust depth lookup
- Produces stabilized 3D hand points

### 9.3 `core/gesture_detector.py`
- Air-push click detection using depth delta over time
- Swipe up/down and open palm recognition
- Cooldown controls to reduce repeated accidental triggers

### 9.4 `core/state_machine.py`
- Centralized app state transitions
- Predictable mode behavior and navigation

### 9.5 UI Modules (`ui/hud_overlay.py`, `ui/menu_renderer.py`)
- Real-time visual interaction layer
- Menu layout, hover states, click feedback
- Back navigation affordance and status indicators

### 9.6 Mode Modules (`modes/*.py`)
- `mouse_mode.py`: cursor and click operations
- `keyboard_mode.py`: virtual key selection and typing
- `media_mode.py`: media control actions

### 9.7 Utilities (`utils/*.py`)
- `camera_utils.py`: frame format conversion, depth processing
- `config.py`: centralized constants and thresholds

## 10. Key Algorithms and Interaction Logic
### 10.1 Depth-Lock Mapping
- Converts normalized landmark coordinates to depth-space coordinates.
- Uses local/robust depth sampling to avoid single-pixel dropout issues.
- Applies smoothing to stabilize jitter.

### 10.2 Air-Push Gesture
- Tracks depth variation of index fingertip over a short time window.
- Positive forward movement above threshold is interpreted as click/select.
- Uses cooldown and validation rules to avoid repeated false clicks.

### 10.3 Cursor Mapping
- Hand coordinates are transformed into screen coordinates.
- Mapping strategy is tuned to maximize usable interaction area while preserving stability.

## 11. UX Challenges and Engineering Improvements
Major user-experience issues identified during validation:
- pointer movement felt unstable at times,
- some controls appeared hard to reach consistently,
- back/cancel interactions were less reliable in edge zones,
- occasional false or missed clicks.

Improvements implemented in iterations:
- better stream profile selection and camera initialization,
- stronger depth robustness and invalid-depth filtering,
- gesture cooldown tuning,
- richer HUD feedback for hand status/depth/click state,
- improved screen mapping and safer interaction zones,
- support for dwell-based selection in addition to air-push.

## 12. Performance Characteristics
- Real-time loop target: ~30 FPS (hardware dependent)
- Stable single-hand tracking workflow
- Responsive gesture-to-action latency suitable for interactive use
- Accuracy dependent on lighting, camera angle, distance, and hand presentation

## 13. Testing and Validation Approach
Testing was performed across:
- camera startup and stream stability,
- hand detection continuity,
- gesture trigger consistency,
- state transitions among all modes,
- keyboard/mouse/media action correctness,
- HUD feedback readability and responsiveness.

Reference test procedures and checklists are maintained in `TESTING_GUIDE.md`.

## 14. Project Structure Snapshot
Top-level structure (simplified):
- `main.py`
- `core/` (depth lock, gestures, state machine)
- `ui/` (HUD, menu rendering)
- `modes/` (mouse, keyboard, media)
- `utils/` (camera helpers, config)
- Documentation files (`README.md`, `INDEX.md`, `TECHNICAL_DOCUMENTATION.md`, etc.)

## 15. Risks and Limitations
- Interaction quality can degrade with poor lighting or occlusion.
- Very fast hand motions can reduce tracking confidence.
- Single-camera geometry constraints may affect extreme edge behavior.
- Gesture thresholds may require environment-specific tuning.

## 16. Future Enhancements
- Adaptive, user-specific calibration profile.
- Multi-gesture confidence fusion.
- Dynamic threshold auto-tuning based on runtime confidence.
- Optional lightweight model fallback paths for low-resource systems.
- Expanded accessibility presets and onboarding flow.

## 17. Conclusion
Aether-Link demonstrates a practical, modular, and extensible touchless interaction system. Through iterative refinement of camera handling, depth mapping, gesture logic, and HUD feedback, the project achieves usable real-time gesture control for desktop tasks.

The architecture is maintainable and ready for further extension in accessibility, gesture personalization, and advanced interaction reliability.

## 18. References
- Orbbec Gemini 335 product and documentation resources
- MediaPipe Hands documentation
- OpenCV documentation
- Project internal documents:
  - `README.md`
  - `PROJECT_SUMMARY.md`
  - `TECHNICAL_DOCUMENTATION.md`
  - `TESTING_GUIDE.md`
  - `INDEX.md`

---
**Document**: Black Book Report  
**Project**: Aether-Link  
**Format**: Markdown (`.md`)  
**Version**: 1.0
