# Aether-Link: Deep Testing & Operations Guide

This document provides a step-by-step walkthrough to test every feature of the Aether-Link hybrid interface. Follow these phases to verify the system is working at 100% performance.

---

## 🛠️ Phase 0: Preparation & Deep Startup

### 1. Hardware Check
*   **Camera:** Connect the **Orbbec Gemini 335** to a USB 3.0 port.
*   **Microphone:** Ensure your PC's default microphone is active and not muted.

### 2. Environment Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Ensure Vosk Model is present in:
# models/vosk-model-small-en-us-0.15/
```

### 3. Deep Startup
Run the project:
```powershell
python main.py
```
**Watch the Terminal for these Success Markers:**
*   `[Security] Signature loaded` — Indicates biometric lock is active.
*   `[Voice] Vosk model loaded` — Indicates voice engine is ready.
*   `Camera ready — streaming started` — Indicates Gemini 335 is active.

---

## 🔒 Phase 1: Security & Biometric Unlocking

The system starts in **LOCKED** mode. 
*   **Action:** Move your hand in front of the camera.
*   **Trigger:** Perform an **Air-Push** (push your index finger forward 5cm quickly).
*   **Feedback:** You will see the HUD flash, and the terminal will say `[Security] Recording started`.
*   **Action:** Draw your unique 3D signature in the air for 3 seconds.
*   **Verification:** 
    *   If correct: Terminal says `✅ Signature VERIFIED`. System switches to **HOME**.
    *   If wrong: Terminal says `❌ Verification FAILED`. Try again with an air-push.
*   **Voice Test:** Try saying `"go to mouse"` while locked. **It should be ignored.** Voice is blocked until you unlock.

---

## 🧭 Phase 2: Navigation & Mode Switching

Now that you are in the **HOME** menu:

### 1. Point & Select (Camera)
*   **Hover:** Move your hand to position the cursor over the **Media** or **Mouse** button.
*   **Dwell Test:** Keep the cursor still on the button for **1.5 seconds**. You will see a white arc fill up around the cursor. Once full, the mode switches.
*   **Push Test:** Instead of dwelling, perform an **Air-Push** while hovering a button. It should click instantly.

### 2. Instant Navigation (Voice)
*   Say: `"go to mouse"` — System jumps to Mouse mode.
*   Say: `"go to media"` — System jumps to Media mode.
*   Say: `"go back"` — Returns you to the HOME menu from anywhere.

---

## ⚡ Phase 3: Spatial Performance (The "Feel" Test)

### 1. Z-Gain Scaling (Distance Test)
*   **Close (30cm):** Move your hand near the camera. The cursor should move slowly and precisely.
*   **Far (1.5m):** Lean back. Perform a small wrist flick. The cursor should travel across the entire screen.
*   **Why:** This prevents "Gorilla Arm" fatigue by requiring less movement when you are further away.

### 2. 1 Euro Filter (Smoothing Test)
*   Hold your hand perfectly still. The cursor should be **rock-solid** with zero jitter.
*   Move your hand very fast. The cursor should follow with **zero lag**.

### 3. Hand Identity (Interference Test)
*   Have a second person wave their hand behind yours. The cursor should **not** jump to their hand.

---

## 🖱️ Phase 4: Mode-Specific Functionality

### 1. Mouse Mode
*   **Action:** Say `"click"` or `"select"`.
*   **Result:** A left-click happens at the cursor position.
*   **Action:** Say `"type Aether Link"`.
*   **Result:** The text "Aether Link" is typed instantly.

### 2. Media Mode
*   **Action:** **Open Palm** gesture (all 5 fingers out).
*   **Result:** Music/Video plays or pauses.
*   **Action:** **Swipe Up/Down**.
*   **Result:** Volume increases/decreases.
*   **Action:** **Swipe Right/Left**.
*   **Result:** Next/Previous track.

### 3. Tab & Window Mode
*   **Tab Mode:** Say `"next tab"` or `"close tab"`.
*   **Window Mode:** Say `"minimize window"` or perform a **Swipe Down**.

---

## 🎙️ Phase 5: Voice Command Audit

Test these specific safe phrases (exact words only):
1.  `"show keyboard"` — Does the air-keyboard appear?
2.  `"take screenshot"` — Does the screen flash?
3.  `"mute audio"` — Does your system volume mute?
4.  `"lock system"` — Does it return to the Signature screen?
5.  `"exit app"` — Does the program shut down cleanly?

---

## ⌨️ Phase 6: Keyboard Overlay

*   **Trigger:** Perform a **Pinch** gesture (touch thumb and index finger).
*   **Interaction:** 
    *   Hover over a key (e.g., 'A') and **Air-Push**.
    *   The letter 'A' should be typed into your active window.
*   **Dismiss:** Pinch again to hide the keyboard.

---

## 🆘 Troubleshooting & Emergency Reset

*   **If Signature Fails 3x:** The terminal will show an emergency bypass.
*   **To Reset Signature:** Close the app and delete `signatures/my_signature.json`. On next start, the app will be unlocked and let you record a new one.
*   **Mic Not Responding:** Check the terminal. If it says `[Voice] Listen loop error`, check if another app is using your microphone.
