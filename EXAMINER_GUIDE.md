# Aether-Link: Complete Examiner-Ready Documentation

> **Project:** Aether-Link — Touchless Gesture + Voice Computer Interface
> **Hardware:** Orbbec Gemini 335 3D Depth Camera + PC Microphone
> **Purpose:** Control a computer entirely without touching a mouse or keyboard.

---

# TABLE OF CONTENTS
1. [How to Start the Project](#1-how-to-start-the-project)
2. [How to Reset & Record a New Signature](#2-how-to-reset--record-a-new-signature)
3. [All Voice Commands](#3-all-voice-commands---complete-list)
4. [All Camera Gestures](#4-all-camera-gestures---complete-list)
5. [All Adjustable Thresholds & Settings](#5-all-adjustable-thresholds--settings)
6. [All Files & What They Do](#6-all-files--what-they-do)
7. [All Libraries & SDKs Used](#7-all-libraries--sdks-used)
8. [Why We Chose Each Technology](#8-why-we-chose-each-technology)
9. [Examiner Q&A — Possible Questions & Answers](#9-examiner-qa--possible-questions--answers)

---

# 1. How to Start the Project

### Step 1: Install Dependencies
```powershell
cd c:\Users\HP\Documents\Project\Aether-Link
pip install -r requirements.txt
```

### Step 2: Download the Voice Model (First Time Only)
```powershell
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "models\vosk-model.zip"
Expand-Archive -Path "models\vosk-model.zip" -DestinationPath "models\"
Remove-Item "models\vosk-model.zip"
```

### Step 3: Run the Application
```powershell
python main.py
```

### What Happens on Start:
1. Camera starts (Gemini 335 Color + Depth streams at 640x480 @ 30fps).
2. Vosk voice model loads from `models/vosk-model-small-en-us-0.15/`.
3. If `signatures/my_signature.json` exists, the system starts **LOCKED**.
4. If no signature exists, the system starts **UNLOCKED** (goes straight to HOME).

---

# 2. How to Reset & Record a New Signature

### Delete Old Signature:
1. Close the running Aether-Link app (press Q or Ctrl+C).
2. Run this command:
```powershell
del signatures\my_signature.json
```

### Record a New Signature:
1. Run the recording tool:
```powershell
python record_signature.py
```
2. Wait for the camera window. You should see **"Hand detected"**.
3. Press **SPACEBAR** to start recording.
4. For 3 seconds, draw a unique pattern in the air. **IMPORTANT: Move your hand forward and backward (toward/away from camera), not just left and right.** The system checks for 3D movement.
5. When the bar reaches 100%, the signature auto-saves to `signatures/my_signature.json`.
6. Press **Q** to close the recorder.
7. Now run `python main.py` — the system will start LOCKED with your new signature.

### Important Tip for Signature:
- Keep the pattern **simple** (like a wave or a circle with depth).
- Practice the **same motion** 2-3 times before recording.
- Move smoothly, not jerky.

---

# 3. All Voice Commands — Complete List

**File:** `voice/voice_engine.py` — Lines 31-82 (the `COMMANDS` dictionary)

**Rule:** Voice uses **EXACT MATCH ONLY**. If you say something slightly different, it is ignored. No fuzzy matching.

**How to ADD a new command:** Open `voice/voice_engine.py`, add a new line inside the `COMMANDS = {` dictionary. Example:
```python
"open browser":     {"type": "action", "action": "open_browser"},
```
Then add the handler in `main.py` inside `handle_voice_command()` (around line 766).

**How to DELETE a command:** Simply delete or comment out the line from the `COMMANDS` dictionary.

### Navigation Commands (11 commands)
| Say This Exactly | What Happens |
|------------------|--------------|
| `"go home"` | Switch to HOME menu |
| `"go to home"` | Switch to HOME menu |
| `"go to media"` | Switch to MEDIA mode |
| `"media mode"` | Switch to MEDIA mode |
| `"go to mouse"` | Switch to MOUSE mode |
| `"mouse mode"` | Switch to MOUSE mode |
| `"go to tab"` | Switch to TAB mode |
| `"tab mode"` | Switch to TAB mode |
| `"go to window"` | Switch to WINDOW mode |
| `"window mode"` | Switch to WINDOW mode |
| `"go back"` | Return to HOME from any mode |

### Click Commands (4 commands)
| Say This Exactly | What Happens |
|------------------|--------------|
| `"click"` | Left-click at current cursor position |
| `"select"` | Left-click at current cursor position |
| `"double click"` | Double-click at current cursor position |
| `"right click"` | Right-click at current cursor position |

### Text Input (1 prefix command)
| Say This Exactly | What Happens |
|------------------|--------------|
| `"type [anything]"` | Types all words after "type". Example: `"type hello world"` types `hello world` |

### Media Commands (9 commands)
| Say This Exactly | What Happens |
|------------------|--------------|
| `"play music"` | Toggle play/pause |
| `"pause music"` | Toggle play/pause |
| `"play pause"` | Toggle play/pause |
| `"volume up"` | Increase volume by 2 steps |
| `"volume down"` | Decrease volume by 2 steps |
| `"next track"` | Skip to next track |
| `"next song"` | Skip to next track |
| `"previous track"` | Go to previous track |
| `"mute audio"` | Toggle mute on/off |

### Tab Commands (4 commands)
| Say This Exactly | What Happens | Windows Hotkey |
|------------------|--------------|----------------|
| `"next tab"` | Next browser tab | Ctrl+Tab |
| `"previous tab"` | Previous browser tab | Ctrl+Shift+Tab |
| `"close tab"` | Close current tab | Ctrl+W |
| `"new tab"` | Open new tab | Ctrl+T |

### Window Commands (5 commands)
| Say This Exactly | What Happens | Windows Hotkey |
|------------------|--------------|----------------|
| `"next window"` | Switch to next app | Alt+Tab |
| `"previous window"` | Switch to previous app | Alt+Shift+Tab |
| `"minimize window"` | Minimize current window | Win+Down |
| `"maximize window"` | Maximize current window | Win+Up |
| `"task view"` | Open Windows Task View | Win+Tab |

### Utility Commands (4 commands)
| Say This Exactly | What Happens |
|------------------|--------------|
| `"take screenshot"` | Saves screenshot (Win+PrintScreen) |
| `"show keyboard"` | Show/hide the air-keyboard overlay |
| `"lock system"` | Lock system, require signature to re-enter |
| `"exit app"` | Shut down Aether-Link completely |

**Total: 37 voice commands + 1 "type ..." prefix = 38 possible voice actions.**

---

# 4. All Camera Gestures — Complete List

**File:** `core/gesture_detector.py` — Contains all gesture detection logic.

### Universal Gestures (Work in ALL Modes)
| Gesture | How to Perform | What It Does | Cooldown |
|---------|----------------|-------------|----------|
| **Air-Push** | Push index finger forward 5cm quickly | Click / Select current button | 0.4s |
| **Dwell-Click** | Hold cursor still on a button for 1.5s | Auto-click that button | — |
| **Pinch** | Touch thumb tip to index fingertip | Toggle keyboard overlay | 0.5s |
| **Peace Sign** | Extend index + middle fingers, curl ring + pinky | Take screenshot (Win+PrintScreen) | 2.0s |

### Media Mode Gestures
| Gesture | What It Does |
|---------|-------------|
| **Open Palm** (all 5 fingers out) | Play/Pause |
| **Swipe Up** | Volume Up (x2 steps) |
| **Swipe Down** | Volume Down (x2 steps) |
| **Swipe Right** | Next Track |
| **Swipe Left** | Previous Track |

### Tab Mode Gestures
| Gesture | What It Does |
|---------|-------------|
| **Swipe Right** | Next Tab (Ctrl+Tab) |
| **Swipe Left** | Previous Tab (Ctrl+Shift+Tab) |

### Window Mode Gestures
| Gesture | What It Does |
|---------|-------------|
| **Swipe Right** | Next Window (Alt+Tab) |
| **Swipe Left** | Previous Window (Alt+Shift+Tab) |
| **Swipe Up** | Task View (Win+Tab) |
| **Swipe Down** | Minimize (Win+Down) |

### Mouse Mode Gestures
| Gesture | What It Does |
|---------|-------------|
| **Move hand** | Cursor follows hand position (with Z-gain scaling) |
| **Air-Push** | Left-click at cursor |

### Locked Mode
| Gesture | What It Does |
|---------|-------------|
| **Air-Push** | Start 3-second signature recording |
| **Draw in air** | Record 3D trajectory for DTW matching |

---

# 5. All Adjustable Thresholds & Settings

## A. Signature Forgiveness (How Easy/Hard to Unlock)

| Setting | Current Value | File | Line | How to Change |
|---------|--------------|------|------|---------------|
| **DTW Threshold** | `350.0` | `main.py` | Line 66 | Increase = easier to unlock. Decrease = stricter. Change: `threshold=350.0` to `threshold=450.0` |
| **Min Z-Variance** | `100.0` | `main.py` | Line 75 | Minimum 3D movement needed in signature. Lower = allows flatter signatures. |
| **Recording Duration** | `3.0` seconds | `main.py` | Line 75 | How long you draw. Change: `duration=3.0` to `duration=4.0` |

**Example: To make unlocking easier, change line 66 of `main.py`:**
```python
# Before (strict):
threshold=350.0,
# After (forgiving):
threshold=500.0,
```

## B. Air-Push Sensitivity (How Easy/Hard to Click)

| Setting | Current Value | File | Line | Effect |
|---------|--------------|------|------|--------|
| **AIR_CLICK_THRESHOLD** | `50` mm | `utils/config.py` | Line 8 | Lower = easier to trigger a click. Higher = harder. |
| **AIR_CLICK_TIME_WINDOW** | `0.35` seconds | `utils/config.py` | Line 9 | Wider window = easier. Narrower = stricter. |
| **MAX_VALID_DELTA_Z** | `600` mm | `core/gesture_detector.py` | Line 37 | Any push bigger than this is rejected as noise. |
| **MIN_VALID_DEPTH** | `80` mm | `core/gesture_detector.py` | Line 38 | Depth values below this are ignored (stereo blind spot). |
| **click_cooldown** | `0.4` seconds | `core/gesture_detector.py` | Line 17 | Time between two consecutive clicks. |

## C. Swipe Sensitivity

| Setting | Current Value | File | Line | Effect |
|---------|--------------|------|------|--------|
| **SWIPE_Y_THRESHOLD** | `80` pixels | `core/gesture_detector.py` | Line 98 | Lower = easier to swipe up/down. |
| **SWIPE_X_THRESHOLD** | `90` pixels | `core/gesture_detector.py` | Line 99 | Lower = easier to swipe left/right. |
| **swipe_cooldown** | `0.4` seconds | `core/gesture_detector.py` | Line 20 | Time between two consecutive swipes. |

## D. Cursor Speed (Z-Gain Scaling)

| Setting | Current Value | File | Line | Effect |
|---------|--------------|------|------|--------|
| **Z_GAIN_REF_DISTANCE** | `500.0` mm | `utils/config.py` | Line 33 | The "ideal" distance. Cursor has gain=1.0 at this distance. |
| **Z_GAIN_POWER** | `0.6` | `utils/config.py` | Line 34 | How aggressively speed scales. Higher = more difference between close/far. |
| **Z_GAIN_MIN** | `0.7` | `utils/config.py` | Line 35 | Minimum speed (when very close). |
| **Z_GAIN_MAX** | `2.5` | `utils/config.py` | Line 36 | Maximum speed (when very far). |

**Example: To make the cursor faster overall:**
```python
# In utils/config.py:
Z_GAIN_MIN = 1.0    # was 0.7 — cursor never goes below normal speed
Z_GAIN_MAX = 3.0    # was 2.5 — cursor goes even faster when far
```

## E. Cursor Smoothing (1 Euro Filter)

| Setting | Current Value | File | Line | Effect |
|---------|--------------|------|------|--------|
| **mincutoff (X, Y)** | `0.1` | `core/depth_lock.py` | Lines 69-70 | Lower = smoother (more lag). Higher = responsive (more jitter). |
| **beta (X, Y)** | `0.7` | `core/depth_lock.py` | Lines 69-70 | Higher = more speed-adaptive (reacts faster to quick moves). |
| **mincutoff (Z)** | `1.0` | `core/depth_lock.py` | Line 71 | Higher than X/Y because depth is noisier. |
| **beta (Z)** | `0.1` | `core/depth_lock.py` | Line 71 | Low because sudden Z-changes are usually noise, not real movement. |

## F. Other Settings

| Setting | Current Value | File | Line | Effect |
|---------|--------------|------|------|--------|
| **DWELL_TIME** | `1.5` seconds | `main.py` | Line 48 | How long to hold cursor on a button to auto-click. |
| **HAND_JUMP_THRESHOLD** | `200` pixels | `utils/config.py` | Line 40 | Max wrist jump between frames. Larger jump = rejected as different hand. |
| **VOLUME_STEP** | `2` | `utils/config.py` | Line 25 | How many volume increments per swipe/command. |
| **HUD_BUTTON_SIZE** | `180` pixels | `utils/config.py` | Line 15 | Size of on-screen buttons. |
| **PINCH_THRESHOLD** | `0.06` normalised | `core/gesture_detector.py` | Line 210 | How close thumb+index must be. Lower = need to touch more precisely. |
| **palm_cooldown** | `1.0` seconds | `core/gesture_detector.py` | Line 23 | Time between play/pause triggers. |
| **peace_cooldown** | `2.0` seconds | `core/gesture_detector.py` | Line 32 | Time between screenshot triggers. |
| **Voice CMD_COOLDOWN** | `0.5` seconds | `voice/voice_engine.py` | Line 102 | Minimum gap between two voice commands. |

---

# 6. All Files & What They Do

| File | Purpose | Key Responsibility |
|------|---------|-------------------|
| `main.py` | **Main application** | Starts everything. Camera init, UI timer, gesture routing, voice routing, Z-gain calculation. |
| `core/depth_lock.py` | **Hand tracking engine** | Runs MediaPipe on each frame, fuses hand landmarks with depth map, applies 1 Euro Filter, rejects hand teleports. |
| `core/gesture_detector.py` | **Gesture recognition** | Detects air-push, swipe (4 directions), pinch, open palm, peace sign. Contains all gesture thresholds. |
| `core/state_machine.py` | **Mode manager** | Manages transitions: LOCKED, HOME, MEDIA, MOUSE, TAB, WINDOW. Handles keyboard overlay state. |
| `voice/voice_engine.py` | **Voice engine** | Runs Vosk offline STT in background thread. Parses speech into commands. Contains the COMMANDS dictionary. |
| `voice/__init__.py` | Package marker | Makes `voice/` a Python package (empty file). |
| `modes/mouse_mode.py` | **Mouse control** | Moves cursor with `pyautogui.moveTo()`, handles click, right-click, double-click, scroll. |
| `modes/media_mode.py` | **Media control** | Sends media key presses: play/pause, volume up/down, next/previous track, mute. |
| `modes/keyboard_mode.py` | **Air keyboard** | Renders QWERTY keyboard overlay. Handles key selection via hover + air-push/dwell. |
| `modes/tab_mode.py` | **Tab control** | Sends hotkeys: Ctrl+Tab, Ctrl+Shift+Tab, Ctrl+W, Ctrl+T for browser tab management. |
| `modes/window_mode.py` | **Window control** | Sends hotkeys: Alt+Tab, Win+Down/Up/Tab for window management. |
| `security/signature_recorder.py` | **Signature capture** | Records 3D hand trajectory for 3 seconds. Validates Z-variance. Saves to JSON file. |
| `security/signature_verifier.py` | **Signature matching** | Uses DTW (Dynamic Time Warping) to compare live signature against stored reference. Returns verified/rejected. |
| `utils/config.py` | **All constants** | Every tunable number in one place: thresholds, screen size, Z-gain, button sizes, etc. |
| `utils/one_euro_filter.py` | **Cursor smoothing** | Speed-adaptive low-pass filter. Smooth when still, responsive when moving fast. |
| `utils/camera_utils.py` | **Frame converters** | Converts raw Orbbec frames (depth, IR, color) to numpy/OpenCV format. |
| `ui/hud_overlay_premium.py` | **HUD display** | Transparent PyQt6 overlay window. Draws cursor dot, dwell arc, state text, button highlights. |
| `ui/menu_renderer.py` | **Button layout** | Calculates button positions for HOME, MEDIA, TAB, WINDOW menus. Checks hover detection. |
| `record_signature.py` | **Standalone recorder** | Separate tool to record a new 3D signature. Press SPACE to start, draws for 3 seconds. |

---

# 7. All Libraries & SDKs Used

| Library | Version | Purpose | Why We Chose It |
|---------|---------|---------|-----------------|
| **pyorbbecsdk2** | >=2.0.18 | Orbbec Gemini 335 camera SDK | Only official SDK for this 3D depth camera. Provides color + depth streams + D2C alignment. |
| **opencv-python** | >=4.8.0 | Image processing & display | Industry standard for real-time computer vision. Used for frame display and color conversion. |
| **numpy** | >=1.24.0 | Numerical computation | Required for depth data arrays, median filtering, and coordinate math. |
| **mediapipe** | >=0.10.0 | Hand landmark detection | Google's ML framework. Detects 21 hand landmarks in real-time. The backbone of all gesture recognition. |
| **PyQt6** | >=6.5.0 | Transparent HUD overlay | Only Qt6 supports truly transparent, click-through windows on Windows 10/11. Used for the cursor and button overlay. |
| **pyautogui** | >=0.9.54 | Mouse/keyboard simulation | Moves the actual cursor, sends clicks, types text, sends hotkeys. The bridge between our gestures and the OS. |
| **fastdtw** | >=0.3.4 | Dynamic Time Warping | Compares 3D signatures with time-warping tolerance. Used for biometric verification. |
| **scipy** | >=1.11.0 | Euclidean distance | Provides the `euclidean()` function used by fastdtw for 3D point distance calculation. |
| **vosk** | >=0.3.45 | Offline speech recognition | Runs completely offline (no internet). Privacy-safe. Low latency (~200ms). |
| **pyaudio** | >=0.2.13 | Microphone stream | Captures raw audio from the PC microphone and feeds it to Vosk in 4096-byte chunks. |
| **pygetwindow** | >=0.0.9 | Active window detection | Optional. Detects which app is in focus (for context-aware keyboard triggering). |

---

# 8. Why We Chose Each Technology

### Why Orbbec Gemini 335 (Not a Webcam)?
A regular webcam gives only 2D (X, Y). The Gemini 335 gives **3D depth** (X, Y, Z). This enables:
- Z-axis cursor gain (speed scales with distance)
- Air-push detection (measures forward movement in millimeters)
- 3D biometric signatures (cannot be spoofed with a flat photo)

### Why MediaPipe (Not OpenPose or YOLO)?
- Runs on **CPU** (no GPU required, works on any laptop)
- Detects **21 hand landmarks** in real-time at 30fps
- Officially maintained by Google
- Tiny model size (~7.8 MB)

### Why Vosk (Not Google Speech API or Whisper)?
- **100% Offline** — no internet required, no privacy concerns
- Low latency (~200ms per recognition)
- Small model size (~50 MB)
- Free and open source

### Why PyQt6 (Not Tkinter or Pygame)?
- Supports **transparent, click-through** overlay windows
- The cursor and buttons overlay on top of ALL other applications
- Hardware-accelerated rendering
- Native Windows DPI awareness

### Why DTW for Signatures (Not Neural Network)?
- Works with **single reference** (no need for 100+ training samples)
- Handles timing differences naturally (user draws faster/slower)
- Computationally cheap (runs in <10ms)
- Easy to tune threshold

### Why Camera for Pointing but Voice for Clicking?
- **Camera** excels at continuous spatial tracking (pointing, scrolling, drawing)
- **Voice** excels at discrete named actions (click, type, switch mode)
- Air-push causes cursor jitter at the moment of click — voice keeps cursor perfectly still

---

# 9. Examiner Q&A — Possible Questions & Answers

### Q1: "What is the core technology behind this project?"
**A:** We use an Orbbec Gemini 335 **3D depth camera** combined with Google's **MediaPipe** hand landmark detection. The camera provides both a color stream (for hand detection) and a depth stream (for measuring distance in millimeters). We fuse these two streams using Hardware D2C (Depth-to-Color) alignment to get precise 3D hand coordinates.

### Q2: "How does the air-push click work?"
**A:** We track the Z-coordinate (depth) of the index fingertip over time. If the fingertip moves **50mm or more toward the camera within 350 milliseconds**, we detect it as a click. We also have three noise protection layers: (1) ignore invalid depth readings of 0, (2) reject jumps larger than 600mm as impossible, (3) require at least 3 valid samples before triggering. The code is in `core/gesture_detector.py`, the `detect_air_push()` method.

### Q3: "What is the 1 Euro Filter and why do you use it?"
**A:** The 1 Euro Filter is a **speed-adaptive low-pass filter**. When the hand is still, it applies heavy smoothing to remove jitter. When the hand moves fast, it reduces smoothing to avoid lag. This gives us the best of both worlds — stable cursor when hovering and instant response when moving. The formula uses two parameters: `mincutoff` (base smoothing) and `beta` (speed reactivity). Code is in `utils/one_euro_filter.py`.

### Q4: "How does the signature security work?"
**A:** We record the user's hand trajectory in 3D space (X, Y, Z) over 3 seconds. This creates a unique "3D signature." To verify, we use **Dynamic Time Warping (DTW)** from the `fastdtw` library. DTW can compare two sequences even if they have different speeds — the user might draw faster or slower each time. We also enforce a minimum Z-variance of 100mm² to prevent spoofing with a flat 2D gesture. The threshold is set at 350 (normalized DTW distance). Code is in `security/signature_verifier.py`.

### Q5: "Why does the cursor move faster when I lean back?"
**A:** This is the **Z-Gain Dynamic Cursor Scaling** feature. The formula is `gain = (distance / 500mm) ^ 0.6`, clamped between 0.7 and 2.5. At 50cm (desk distance), the gain is 1.0 (normal). At 1.5m, the gain is about 2.0, meaning small wrist movements cover large screen areas. This eliminates "Gorilla Arm" fatigue — users don't need to make big arm movements from far away. Code is in `main.py`, the `_compute_gain()` method.

### Q6: "Why is voice used only for certain actions?"
**A:** We follow the **Golden Rule**: Camera handles **continuous spatial actions** (pointing, scrolling, drawing), and voice handles **discrete named actions** (click, type, switch mode). Voice cannot express continuous positions ("move cursor to pixel 847, 392" is impossible), and camera cannot efficiently type text (air-keyboard takes 30-60x longer than speech).

### Q7: "How do you prevent false voice triggers?"
**A:** Three safety measures: (1) **Exact match only** — no fuzzy/partial matching (we removed this after "it" accidentally triggered "exit"). (2) **Multi-word commands** — dangerous single-word commands like "exit" were replaced with "exit app". (3) **0.5-second cooldown** between commands to prevent rapid-fire triggers.

### Q8: "What happens if someone walks behind the user?"
**A:** We have **Hand Identity Tracking**. We measure the distance between the wrist position in consecutive frames. If the wrist "jumps" more than 200 pixels in one frame (33ms), it's physically impossible for the same hand — so we reject it as a different person's hand and keep using the last known good position. Code is in `core/depth_lock.py`.

### Q9: "Can this work without the voice engine?"
**A:** Yes. If Vosk or PyAudio is not installed, or if the model is missing, the system silently falls back to **gesture-only mode**. All camera-based features work perfectly. Voice is designed as a "surgical patch" — it only fills the gaps where gestures are weak.

### Q10: "How would you add a new gesture?"
**A:** (1) Add a new detection method in `core/gesture_detector.py` (e.g., `detect_thumbs_up()`). (2) Add a cooldown variable in `__init__`. (3) Call the method inside `handle_gestures()` in `main.py` under the appropriate mode section.

### Q11: "What is the Dwell-Click and why is it useful?"
**A:** Dwell-Click means holding the cursor still on a button for **1.5 seconds** to auto-click. This is useful because air-push can be difficult for some users — it requires a quick forward push. Dwell is zero-effort: just point and wait. We also have a 0.3-second "jitter forgiveness" window so small hand tremors don't reset the timer. Code is in `main.py`, the `_check_dwell()` method.

### Q12: "What threading model does the application use?"
**A:** Three threads: (1) **Camera thread** (background) — captures frames and runs MediaPipe. (2) **Voice thread** (background) — listens to microphone and runs Vosk. (3) **Main UI thread** — runs PyQt6 event loop, processes gestures, updates HUD. All communication uses thread-safe mechanisms: `threading.Lock` for frame data, `queue.Queue` for voice commands.

### Q13: "How do you change the signature threshold?"
**A:** Open `main.py`, go to line 66, change `threshold=350.0` to a higher number (e.g., `threshold=500.0`) for easier matching, or lower (e.g., `threshold=200.0`) for stricter security. Then restart the app.

### Q14: "What is the screen margin and why?"
**A:** We use a 4% margin (`margin=0.04`) in the `_map_to_screen()` function. The Gemini 335's stereo depth becomes unreliable at the edges of the camera frame (the left and right cameras can't see the same area at the extreme edges). By ignoring the outer 4% of the frame, we keep the cursor in the reliable depth zone. Code is in `main.py`, `_map_to_screen()` method.

### Q15: "What are the system requirements?"
**A:** Windows 10/11, Python 3.10+, Orbbec Gemini 335 camera (USB 3.0), any microphone. No GPU required — everything runs on CPU using MediaPipe's TensorFlow Lite.

### Q16: "Where exactly does the `type [text]` voice command write the text? Does it need a special box?"
**A:** No special text box or specific location in our app is needed. The `type` command uses the `pyautogui` library to simulate physical keyboard presses at the OS level. This means it will type the text **wherever your computer's cursor is currently focused**. 
* If you click on a Google Chrome search bar and say "type weather today", it will type it in the browser. 
* If you have MS Word or Notepad open and active, it types in that document. 
* It works exactly as if a ghost were typing on your physical keyboard. The relevant code is in `main.py`, under `handle_voice_command()`: `pyautogui.write(cmd['content'], interval=0.02)`.

### Q17: "Do voice commands work if my hand is NOT visible to the camera?"
**A:** **YES!** This is a critical and deliberate feature of the hybrid design. The voice engine runs in a completely separate background thread and operates independently of the camera's hand detection. As long as the system is **UNLOCKED**, you can put your hands down, rest your arms, drink water, or even walk across the room, and voice commands like "play music", "go to tab", or "type hello" will still work perfectly. The main loop in `update_ui()` processes voice commands every frame even if `hand_data` is `None`.

### Q18: "What happens if there's loud background noise or people talking nearby?"
**A:** The system is protected by our **"Surgical Voice" philosophy**. We intentionally removed single-word commands (like "play", "mute", "exit") because they frequently occur in normal conversation or background noise, leading to accidental triggers. We strictly enforce **multi-word exact-match phrases** (like "play music", "exit app"). If someone nearby says "Can you lock the door?", the system ignores it because the exact required phrase is "lock system". Additionally, the Vosk offline STT engine is highly resilient to background noise compared to cloud-based APIs.

### Q19: "How does the D2C (Depth-to-Color) alignment work and why is it needed?"
**A:** The Orbbec Gemini 335 camera has two separate sensors (an RGB Color sensor and an IR Depth sensor) which sit physically apart from each other. This physical offset means they have slightly different fields of view (FOV). D2C (Hardware Align Mode) uses the camera's internal processing chip to mathematically warp and reproject the depth map so it perfectly overlays the color image. Without D2C, the (X, Y) pixel of your fingertip detected in the color image would point to the wrong spatial location in the depth map, causing the cursor depth to be inaccurate or the air-push to fail. Code is in `main.py`: `config.set_align_mode(OBAlignMode.HW_MODE)`.

### Q20: "If the user is far away, the hand appears smaller in pixels. How does MediaPipe handle this?"
**A:** MediaPipe uses an intelligent two-stage machine learning pipeline. First, a lightweight **Palm Detector** runs on the full image to find a bounding box around the hand. It is trained on a massive dataset to detect hands at various scales and distances. Once the bounding box is found, the **Hand Landmark model** crops that specific region, scales it to a fixed uniform size (e.g., 224x224 pixels), and then detects the 21 joints. Because it crops and normalizes the scale first, it works reliably whether the hand is 30cm away (taking up the whole screen) or 2 meters away (very small).

### Q21: "Can I use both hands at the same time?"
**A:** The system is currently designed to track **one primary hand** to prevent confusing the OS cursor. MediaPipe is configured to track `max_num_hands=1`. If two hands are visible in the frame, it picks the one with the highest confidence score. However, our custom **Hand Identity Tracking** ensures stability: if your primary hand is moving, and someone else waves a hand behind you, the cursor won't suddenly teleport to their hand. We calculate the distance the wrist moved; if it jumps more than 200 pixels in 33 milliseconds, we reject it as a different person's hand.

### Q22: "How does the system handle rapid back-to-back voice commands?"
**A:** To prevent the system from queuing up dozens of commands if you speak rapidly (or if a TV/podcast is playing in the background), we implemented a **Command Cooldown** in `voice_engine.py` (`self.cooldown = 0.5` seconds). After a command is successfully recognized and executed, the voice engine actively ignores further speech input for half a second. This acts as a rate-limiter, ensuring stable, predictable, and controlled performance.

### Q23: "Why did you build this system? What is the real-world application?"
**A:** This system is built for environments where touching a physical mouse or keyboard is impossible, dangerous, or highly unhygienic. Real-world applications include:
1. **Medical / Surgery:** Surgeons in operating rooms can navigate medical scans, MRIs, and patient records without breaking sterility (they don't have to touch a dirty mouse or take off gloves).
2. **Industrial & Manufacturing:** Factory workers with greasy, dirty, or heavy protective gloves can interact with machinery control panels.
3. **Accessibility:** Users with limited mobility (who can point and speak but lack the fine motor skills to easily grip a physical mouse or type on a keyboard) can regain full control of their PC.

### Q24: "How does the system differentiate between a deliberate click (Air-Push) and normal hand movement?"
**A:** Normal hand movement is generally side-to-side (X/Y axis) or slow forward movement. A deliberate click requires a rapid motion specifically on the Z-axis (depth). Our `detect_air_push()` algorithm specifically checks if the Z-value of the index finger decreases by **50mm or more** within a tight time window of **350 milliseconds**. If you move your hand forward slowly over 1 second, it will not trigger. It requires a distinct, quick "stab" motion.

### Q25: "Is my voice data sent to the cloud or Google for processing?"
**A:** **No, absolutely not.** The system uses the **Vosk** speech recognition engine, which runs 100% locally and offline on your CPU. The voice model is downloaded once and stored in the `models/` folder. No audio data ever leaves your computer, making this system entirely private and secure, which is essential for medical or enterprise environments.
