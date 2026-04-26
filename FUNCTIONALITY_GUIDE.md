# Aether-Link: Complete Functionality Guide

This guide provides a detailed breakdown of every feature, gesture, and mode within the Aether-Link system.

---

## 1. Core Concepts

- **State Machine**: The system operates in different **modes** (Home, Mouse, Media, etc.). You can only be in one primary mode at a time. The keyboard is an **overlay** that can appear on top of any mode.
- **HUD (Heads-Up Display)**: The semi-transparent interface on your screen. It shows:
    - Your current **Mode** (e.g., "MEDIA CONTROL").
    - **Info Text** explaining available gestures for that mode.
    - **Clickable Buttons** for mode-specific actions.
    - A **Cursor** showing where your hand is pointing.
    - A **BACK Button** at the top-center to return to the HOME menu.
- **Gestures vs. Buttons**: You can trigger actions either by performing a specific hand gesture (like a swipe) or by pointing your cursor at a button and performing an "Air-Push" gesture.

---

## 2. Global Gestures & Actions

These actions work in **almost every mode** (unless the keyboard is open).

| Gesture | Hand Shape | Action | Notes |
|---|---|---|---|
| **Air-Push** | Push hand forward 5cm | **Click / Select** | The primary action for pressing buttons. The threshold is high enough to prevent accidental clicks from hand tremor. |
| **Pinch** | Bring thumb and index finger tips together | **Toggle Keyboard** | The single, deliberate way to show or hide the virtual keyboard. This prevents it from appearing by accident. |
| **Peace Sign** | Extend index and middle finger (like a 'V') | **Take Screenshot** | Triggers `Win + PrintScreen` to save a screenshot to your Pictures folder. |
| **BACK Button** | Point at the top-center button and Air-Push | **Go to HOME Menu** | Your universal way to exit any mode and return to the main menu. |

---

## 3. Application Modes

You select these from the HOME Menu.

### A. HOME Menu
- **Purpose**: The main navigation hub.
- **Actions**: Point and Air-Push on a button to select a mode:
    - `MEDIA`: Control music and videos.
    - `MOUSE`: Control the system cursor.
    - `TAB`: Manage browser tabs.
    - `WINDOW`: Manage application windows.
    - `KEYBOARD`: Directly open the keyboard.
    - `EXIT`: Shut down the Aether-Link application.

### B. MOUSE Mode
- **Purpose**: Provides precise, low-latency cursor control.
- **Actions**:
    - **Move Cursor**: Simply move your hand.
    - **Left Click**: Perform an Air-Push.

### C. MEDIA Mode
- **Purpose**: Control media players (Spotify, YouTube, etc.).
- **Actions (Gestures)**:
    - `Swipe Up`: Volume Up
    - `Swipe Down`: Volume Down
    - `Swipe Right`: Next Track
    - `Swipe Left`: Previous Track
    - `Open Palm` (all 4 fingers extended): Play / Pause
- **Actions (Buttons)**: You can also Air-Push on the on-screen buttons for all of the above actions.

### D. TAB Mode
- **Purpose**: Manage tabs in your web browser.
- **Actions (Gestures)**:
    - `Swipe Right`: Next Tab
    - `Swipe Left`: Previous Tab
- **Actions (Buttons)**: 
    - `Next Tab`: Clickable button.
    - `Previous Tab`: Clickable button.
    - `Close Tab`: **SAFE** - only works by clicking the button. No more accidental closing!
    - `New Tab`: Clickable button.

### E. WINDOW Mode
- **Purpose**: Manage application windows on your desktop.
- **Actions (Gestures)**:
    - `Swipe Right`: Next Window (`Alt+Tab`)
    - `Swipe Left`: Previous Window (`Alt+Shift+Tab`)
    - `Swipe Up`: Task View (`Win+Tab`)
    - `Swipe Down`: Minimize Window
- **Actions (Buttons)**: You can also Air-Push on buttons for all of the above, plus a `Maximize` button.

---

## 4. Keyboard Overlay

- **How to Activate**: Make a **Pinch** gesture in any mode.
- **How to Dismiss**: Make a **Pinch** gesture again, or click the **BACK** button.
- **How to Type**: Point the cursor at a letter and Air-Push.

---

## 5. Security: Locked Mode

- **Purpose**: Prevents unauthorized use. The system starts in this mode if a signature is saved.
- **How to Unlock**: 
    1. Perform an **Air-Push** to begin recording.
    2. Draw your unique 3D hand signature in the air for 3 seconds.
    3. The system uses Dynamic Time Warping (DTW) to verify your signature against the saved one.
- **Forgot Signature?**: If you fail 3 times, a hint will appear. You must:
    1. Press 'Q' to quit the app.
    2. Manually delete the file at `signatures/my_signature.json`.
    3. Restart the application. It will now start in the unlocked HOME menu.
