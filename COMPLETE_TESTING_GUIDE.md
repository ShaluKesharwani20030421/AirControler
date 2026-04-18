# Complete Testing Guide - Step by Step

## 🎯 Table of Contents
1. [Initial Setup & Launch](#initial-setup--launch)
2. [Testing Premium UI Features](#testing-premium-ui-features)
3. [Testing All Modes](#testing-all-modes)
4. [2-Hand Scenario (Closest Hand)](#2-hand-scenario-closest-hand)
5. [3D Biometric Signature Recording](#3d-biometric-signature-recording)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Initial Setup & Launch

### Step 1: Verify Installation
```powershell
# Check Python version
python --version
# Expected: Python 3.12.0

# Verify all packages installed
pip list | Select-String -Pattern "pyorbbecsdk2|opencv-python|numpy|mediapipe|PyQt6|pyautogui|fastdtw|scipy"
```

### Step 2: Connect Camera
```
1. Plug Orbbec Gemini 335 into USB 3.0 port (blue port)
2. Wait for Windows to recognize device
3. Check Device Manager → "Orbbec Depth Sensor" should appear
```

### Step 3: Launch Application
```powershell
cd C:\Users\HP\Documents\Project\Aether-Link
python main.py
```

**Expected Console Output**:
```
load extensions from ...
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

**What You'll See**:
- ✅ **OpenCV Window**: Camera feed with hand tracking
- ✅ **Transparent HUD**: Overlay on your screen
- ✅ **Energy Orb Cursor**: Magical glowing cursor

---

## ✨ Testing Premium UI Features

### Test 1: Energy Orb Cursor

**Steps**:
1. Show your RIGHT hand to camera (30-60 cm away)
2. Observe the cursor

**Expected Behavior**:
- ✅ **Green glowing orb** appears
- ✅ **Pulsates smoothly** (breathing effect)
- ✅ **Follows your hand** precisely
- ✅ **Sparkle orbits** the core
- ✅ **Triple-layer glow** (halo effect)

**If No Hand Detected**:
- ❌ **Gray orb** (inactive state)
- ❌ Dimmer glow
- ❌ "Hand: NOT DETECTED" in status bar

---

### Test 2: Ripple Animation

**Steps**:
1. Position hand over any button
2. Perform **air-push** (push hand forward quickly)

**Expected Behavior**:
- ✅ **Ripple waves** expand from cursor
- ✅ **Dual rings** (outer + inner)
- ✅ **Smooth fade-out** over 1 second
- ✅ **Full-screen flash** (radial gradient)
- ✅ **"✓ CLICK!" text** appears

**Console Output**:
```
[Gesture] Air-Push! ΔZ=XXX.0 mm in XXX ms
```

---

### Test 3: Circular Dwell Timer

**Steps**:
1. Hover hand over any button
2. **Hold still** for 1.5 seconds
3. Watch the circular timer

**Expected Behavior**:
- ✅ **Circle outline** appears around button
- ✅ **Fills clockwise** from 12 o'clock
- ✅ **Color gradient**: Green → Yellow
- ✅ **Percentage text** shows below (0% → 100%)
- ✅ **Auto-clicks** when reaches 100%
- ✅ **White center dot** visible

---

### Test 4: Glassmorphic Buttons

**Steps**:
1. Move cursor over different buttons
2. Observe hover effects

**Expected Behavior**:
- ✅ **Default**: Semi-transparent blue
- ✅ **Hover**: Yellow glow + radial gradient
- ✅ **Border thickens** on hover (2px → 4px)
- ✅ **Background never blocks** content behind

---

## 🎮 Testing All Modes

### Mode 1: HOME MENU

**Layout**:
```
[🎵 Media Control]    [🖱️ Air Mouse]
[🔄 Tab Switcher]     [🪟 Window Switcher]
         [❌ Exit]
```

**Test Steps**:
1. Launch app → Should start at HOME
2. Move hand over each button
3. Observe dwell timer
4. Air-push or wait 1.5s to select

**Expected**:
- ✅ 5 buttons visible
- ✅ Keyboard button NOT present (removed in v2.0)
- ✅ Hover effects work
- ✅ Dwell timer fills
- ✅ Ripple on click

---

### Mode 2: MEDIA CONTROL

**Gestures**:
| Gesture | Action | How To |
|---------|--------|--------|
| Open Palm | Play/Pause | Spread all 5 fingers |
| Swipe Up | Volume Up | Move hand upward quickly |
| Swipe Down | Volume Down | Move hand downward quickly |

**Test Steps**:
1. Select "Media Control" from HOME
2. Play a video/music (YouTube, Spotify, etc.)
3. **Open Palm**: Spread all fingers wide
4. **Swipe Up**: Quick upward hand motion
5. **Swipe Down**: Quick downward hand motion

**Expected Console Output**:
```
[Gesture] Open Palm — Play/Pause
Media: Play/Pause
Media: Volume Up
Media: Volume Down
```

**Expected Behavior**:
- ✅ Media pauses/plays on open palm
- ✅ Volume increases on swipe up
- ✅ Volume decreases on swipe down
- ✅ BACK button visible at top-center

---

### Mode 3: AIR MOUSE (with Context-Aware Keyboard!)

**Gestures**:
| Action | How To |
|--------|--------|
| Move Cursor | Move hand in air |
| Left Click | Air-push |
| Auto Keyboard | Click text field |
| Dismiss Keyboard | Swipe down |

**Test Steps**:

#### A. Basic Mouse Control
1. Select "Air Mouse" from HOME
2. Move hand → Cursor follows
3. Air-push → Left click

**Expected**:
- ✅ Cursor moves smoothly
- ✅ Click works on desktop icons
- ✅ Ripple animation on click

#### B. Context-Aware Keyboard (NEW!)
1. Open Chrome browser
2. Navigate to Google.com
3. Move cursor to search bar
4. **Air-push** to click search bar
5. **Keyboard overlay appears automatically!**
6. Use air-push to type keys
7. **Swipe down** to dismiss keyboard

**Expected**:
- ✅ Keyboard appears when clicking text fields
- ✅ Works in Chrome, Edge, Notepad, VS Code
- ✅ State shows "MOUSE + KEYBOARD"
- ✅ Swipe down dismisses keyboard
- ✅ Returns to normal mouse mode

**Console Output**:
```
Mouse: Click
[Overlay] Keyboard activated (text_input_click) over MOUSE
[Overlay] Keyboard dismissed, returning to MOUSE
```

---

### Mode 4: TAB SWITCHER

**Gestures**:
| Gesture | Action | Shortcut |
|---------|--------|----------|
| Swipe Right | Next Tab | Ctrl+Tab |
| Swipe Left | Previous Tab | Ctrl+Shift+Tab |
| Air-Push | Close Tab | Ctrl+W |

**Test Steps**:
1. Open Chrome with 3+ tabs
2. Select "Tab Switcher"
3. **Swipe Right**: Quick right hand motion
4. **Swipe Left**: Quick left hand motion
5. **Air-Push**: Close current tab

**Expected Console Output**:
```
Tab: Next Tab (Ctrl+Tab)
Tab: Previous Tab (Ctrl+Shift+Tab)
Tab: Close Tab (Ctrl+W)
```

**Expected Behavior**:
- ✅ Tabs switch on swipe
- ✅ Tab closes on air-push
- ✅ Works in Chrome, Edge, Firefox

---

### Mode 5: WINDOW SWITCHER

**Gestures**:
| Gesture | Action | Shortcut |
|---------|--------|----------|
| Swipe Right | Next Window | Alt+Tab |
| Swipe Left | Previous Window | Alt+Shift+Tab |
| Swipe Up | Task View | Win+Tab |
| Swipe Down | Minimize | Win+Down |

**Test Steps**:
1. Open multiple windows (Chrome, Notepad, File Explorer)
2. Select "Window Switcher"
3. **Swipe Right**: Cycles to next window
4. **Swipe Left**: Cycles to previous window
5. **Swipe Up**: Opens Task View
6. **Swipe Down**: Minimizes current window

**Expected Console Output**:
```
Window: Next Window (Alt+Tab)
Window: Previous Window (Alt+Shift+Tab)
Window: Task View (Win+Tab)
Window: Minimize (Win+Down)
```

---

## 👥 2-Hand Scenario (Closest Hand Detection)

### How It Works

The system is configured to track **only 1 hand** and automatically selects the **closest hand** to the camera.

**Configuration** (in `core/depth_lock.py`):
```python
max_num_hands=1  # Only track 1 hand
```

### Testing 2-Hand Scenario

**Test Steps**:
1. Launch application
2. Show **both hands** to camera
3. Observe which hand is tracked

**Expected Behavior**:
- ✅ **Closest hand** is tracked (lower Z value)
- ✅ **Other hand ignored** completely
- ✅ Cursor follows closest hand only
- ✅ Hand landmarks drawn on closest hand only

**How to Switch Hands**:
```
Method 1: Move preferred hand closer
- Bring right hand to 30cm
- Left hand at 60cm
- Right hand will be tracked

Method 2: Hide other hand
- Remove left hand from view
- Only right hand visible
- Right hand will be tracked
```

**Verification**:
```
Check console output:
Hand: XX.X cm ✓ DETECTED

Lower number = closer hand = tracked hand
```

### Why Closest Hand?

**Advantages**:
- ✅ **Prevents confusion** (no ambiguity)
- ✅ **Natural interaction** (reach forward to control)
- ✅ **Consistent tracking** (no hand-switching)
- ✅ **Better performance** (single hand processing)

---

## 🔐 3D Biometric Signature Recording

### Overview

Record a unique 3D signature using your index finger movement in 3D space.

**Requirements**:
- ✅ 3 seconds of recording
- ✅ Minimum 30 points captured
- ✅ Z-variance ≥ 100 mm² (anti-spoofing)
- ✅ Must move hand forward/backward (depth changes)

---

### Step-by-Step Signature Recording

#### Step 1: Launch Recording Tool

```powershell
python record_signature.py
```

**Expected Output**:
```
======================================================================
  3D BIOMETRIC SIGNATURE RECORDING
======================================================================

📝 Instructions:
  1. Position your hand in front of the camera (30-60 cm)
  2. Press SPACE to start recording
  3. Draw your signature in 3D space for 3 seconds
  4. Move your finger in ALL 3 dimensions (X, Y, Z)
  5. The signature will auto-save when complete

⚠️  Important:
  - Move your hand FORWARD and BACKWARD (Z-axis) during signature
  - Flat 2D signatures will be rejected (anti-spoofing)
  - You need at least 100 mm² Z-variance

🎮 Controls:
  SPACE = Start recording
  Q     = Quit
======================================================================
```

#### Step 2: Position Your Hand

```
Distance: 30-60 cm from camera
Hand: RIGHT hand
Finger: INDEX finger extended
Position: Center of camera view
```

**What You'll See**:
- OpenCV window showing camera feed
- Hand landmarks drawn on your hand
- "Press SPACE to start recording" text

#### Step 3: Start Recording

**Action**: Press **SPACE** key

**What Happens**:
- ✅ Red text: "● RECORDING: 0%"
- ✅ Progress bar appears
- ✅ Point counter starts
- ✅ 3-second countdown begins

#### Step 4: Draw Your Signature

**IMPORTANT**: Move in **ALL 3 DIMENSIONS**!

**Good Signature Patterns**:
```
Pattern 1: Figure-8 with Depth
- Draw figure-8 in air
- Move hand closer/farther during drawing
- Creates 3D spiral effect

Pattern 2: Circle with Pulse
- Draw circle in air
- Push forward and pull back rhythmically
- Creates depth variation

Pattern 3: Wave with Depth
- Wave hand left-right
- Simultaneously move forward-backward
- Creates 3D wave pattern

Pattern 4: Your Initials in 3D
- Draw your initials
- Vary depth while drawing
- Unique and memorable
```

**BAD Patterns** (Will be REJECTED):
```
❌ Flat circle (no depth change)
❌ Horizontal line (2D only)
❌ Vertical line (2D only)
❌ Any pattern without Z-axis movement
```

#### Step 5: Watch Progress

**During Recording**:
```
● RECORDING: 33%  ████████░░░░░░░░░░░░░░
Points: 28

● RECORDING: 66%  ████████████████░░░░░░░░
Points: 57

● RECORDING: 100% ████████████████████████
Points: 87
```

#### Step 6: Signature Validation

**After 3 Seconds**:

**If SUCCESSFUL**:
```
[Signature] VALID - 87 points, Z-variance OK
[Signature] Z-variance: 2547.3 mm², Z-range: 245.8 mm
[Signature] Saved to: signatures/my_signature.json

✅ Signature saved successfully!
   File: signatures/my_signature.json

   You can now:
   1. Close this window (press Q)
   2. Enable security in main.py
   3. Run Aether-Link with biometric authentication
```

**If REJECTED**:
```
[Signature] REJECTED - Flat signature (possible video spoof)
[Signature] Required Z-variance: 100 mm², Got: 45.2 mm²

❌ Signature rejected! Please try again.
   - Move your hand FORWARD and BACKWARD
   - Don't just draw in 2D
   - Create depth variation
```

#### Step 7: Verify Signature File

```powershell
# Check if file exists
dir signatures\my_signature.json

# View signature data
type signatures\my_signature.json
```

**Expected JSON Structure**:
```json
{
  "version": "1.0",
  "recorded_at": "2026-04-18 13:45:30",
  "duration": 3.0,
  "num_points": 87,
  "metadata": {
    "z_variance": 2547.3,
    "z_range": 245.8,
    "z_mean": 487.2
  },
  "path": [
    {"x": 320.5, "y": 240.8, "z": 450.2, "timestamp": 0.0},
    {"x": 322.1, "y": 238.3, "z": 455.7, "timestamp": 0.033},
    ...
  ]
}
```

**Key Metrics**:
- `num_points`: Should be 60-90 (at 30 FPS)
- `z_variance`: Should be > 100 (higher = more 3D movement)
- `z_range`: Depth variation in mm

---

### Tips for Good Signatures

#### ✅ DO:
1. **Move in 3D**: Forward/backward is crucial
2. **Smooth motions**: Avoid jerky movements
3. **Consistent speed**: Not too fast, not too slow
4. **Repeatable pattern**: Something you can remember
5. **Good lighting**: Avoid shadows on hand

#### ❌ DON'T:
1. **Flat signatures**: No 2D-only patterns
2. **Too fast**: Causes tracking loss
3. **Too slow**: Not enough points
4. **Random movements**: Hard to repeat
5. **Poor lighting**: Causes tracking errors

---

### Enable Biometric Security

After recording signature, enable it in main app:

**Edit `main.py`** (around line 46):
```python
# Change this line:
self.state_machine = StateMachine(require_auth=False)

# To this:
self.state_machine = StateMachine(require_auth=True)

# Add verifier (after state_machine):
from security import SignatureVerifier
self.signature_verifier = SignatureVerifier(
    reference_path='signatures/my_signature.json',
    threshold=50.0  # Adjust for strictness
)
```

**Add verification handler** (in `handle_gestures` method):
```python
# At the start of handle_gestures():
if self.state_machine.is_locked():
    self.handle_locked_mode(air_push)
    return
```

**Add locked mode handler**:
```python
def handle_locked_mode(self, air_push):
    """Handle LOCKED state - require signature verification."""
    if not hasattr(self, 'verification_recorder'):
        from security import SignatureRecorder
        self.verification_recorder = SignatureRecorder(duration=3.0)
    
    # Start recording on air-push
    if air_push and not self.verification_recorder.recording:
        self.verification_recorder.start_recording()
        print("[Security] Draw your signature to unlock...")
        return
    
    # Collect points
    if self.verification_recorder.recording:
        complete = self.verification_recorder.add_point(self.current_hand_data)
        
        if complete:
            # Verify signature
            result = self.signature_verifier.verify(
                self.verification_recorder.signature_path
            )
            
            if result['verified']:
                print("✓ Signature verified - unlocking system")
                self.state_machine.unlock()
            else:
                print(f"✗ Verification failed: {result['reason']}")
                print("Try again...")
            
            # Reset for next attempt
            self.verification_recorder = SignatureRecorder(duration=3.0)
```

**Test Locked Mode**:
```powershell
python main.py
# App starts in LOCKED state
# Air-push to start signature recording
# Draw your signature
# System unlocks if signature matches!
```

---

## 🐛 Troubleshooting

### Issue 1: No Hand Detected

**Symptoms**:
- Gray cursor (not green)
- "Hand: NOT DETECTED" in status bar
- No hand landmarks in OpenCV window

**Solutions**:
```
1. Check distance (30-60 cm is optimal)
2. Improve lighting (avoid backlighting)
3. Show palm to camera (not back of hand)
4. Use RIGHT hand (configured for right hand)
5. Spread fingers naturally
6. Check camera is not blocked
```

### Issue 2: Cursor Jumpy/Unstable

**Symptoms**:
- Cursor jumps around
- Tracking lost frequently
- Hand landmarks flicker

**Solutions**:
```
1. Improve lighting (add desk lamp)
2. Reduce background clutter
3. Move hand slower
4. Stay in center of camera view
5. Check camera is stable (not moving)
```

### Issue 3: Air-Push Not Detected

**Symptoms**:
- No ripple animation
- No console output
- Clicks don't register

**Solutions**:
```
1. Push hand FORWARD (toward camera)
2. Push faster (quick motion)
3. Minimum 30mm depth change required
4. Check console for "Air-Push!" messages
5. Try exaggerated push motion
```

### Issue 4: Signature Rejected

**Symptoms**:
```
[Signature] REJECTED - Flat signature
[Signature] Z-variance: 45.2 mm² (need 100+)
```

**Solutions**:
```
1. Move hand FORWARD and BACKWARD more
2. Create depth variation during signature
3. Don't draw flat 2D patterns
4. Try figure-8 with depth changes
5. Check Z-variance in saved JSON (should be >500 for good signatures)
```

### Issue 5: Keyboard Doesn't Appear

**Symptoms**:
- Click text field in Chrome
- No keyboard overlay appears

**Solutions**:
```
1. Install pygetwindow: pip install pygetwindow
2. Check window title contains "chrome", "edge", etc.
3. Click in content area (not menu bar)
4. Try double-clicking text field
5. Check console for text detection messages
```

---

## ✅ Testing Checklist

### Basic Functionality
- [ ] App launches without errors
- [ ] Camera initializes successfully
- [ ] Hand detected (green orb)
- [ ] Cursor follows hand smoothly
- [ ] Air-push triggers ripple
- [ ] Dwell timer works (1.5s)
- [ ] All 5 modes accessible

### Premium UI Features
- [ ] Energy orb pulsates
- [ ] Sparkle orbits core
- [ ] Ripple animation on click
- [ ] Circular dwell timer
- [ ] Glassmorphic buttons
- [ ] Semi-transparent overlays
- [ ] 60 FPS smooth animations

### Mode Testing
- [ ] Media Control (play/pause, volume)
- [ ] Air Mouse (cursor, click)
- [ ] Context-aware keyboard
- [ ] Tab Switcher (next/prev/close)
- [ ] Window Switcher (all 4 gestures)

### 2-Hand Scenario
- [ ] Closest hand tracked
- [ ] Other hand ignored
- [ ] Can switch by moving closer

### Biometric Security
- [ ] Signature recorded successfully
- [ ] Z-variance > 100 mm²
- [ ] JSON file created
- [ ] Signature can be verified
- [ ] Locked mode works

---

## 📊 Performance Metrics

### Expected Performance
```
Frame Rate: 55-60 FPS
CPU Usage: 15-25%
Memory: ~300 MB
Latency: <50ms (hand to cursor)
```

### Check Performance
```powershell
# Monitor in Task Manager:
- Python.exe CPU usage
- Python.exe Memory usage
- Check for lag in cursor movement
```

---

## 🎓 Pro Tips

### For Best Experience
1. **Lighting**: Bright, even lighting (no shadows)
2. **Background**: Plain wall behind you
3. **Distance**: 40-50 cm is sweet spot
4. **Hand**: Right hand, palm facing camera
5. **Gestures**: Exaggerate motions initially
6. **Patience**: Let dwell timer work (don't rush)

### For Demos
1. **Start with HOME**: Show all 5 modes
2. **Demo Media**: Play/pause is impressive
3. **Show Mouse**: Context-aware keyboard is wow factor
4. **Ripple effects**: Air-push for visual impact
5. **Dwell timer**: Let it fill completely once

---

**Testing Complete!** 🎉

You now have everything you need to test all features, handle 2-hand scenarios, and record biometric signatures!
