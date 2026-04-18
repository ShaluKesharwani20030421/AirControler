# Aether-Link Architecture Refactor: Human-Centric Design

## 🎯 Refactor Overview

**Date**: April 18, 2026  
**Version**: 2.0 (Human-Centric Architecture)

This document describes the major architectural refactor from a flat state model to a human-centric, context-aware interaction model.

---

## 📊 Before vs. After

### Before (v1.0 - Flat State Model)
```
6 Equal States:
├── HOME
├── MEDIA
├── MOUSE
├── KEYBOARD  ← Treated as standalone mode
├── TAB
└── WINDOW

Issues:
❌ Keyboard is a mode, not a tool
❌ Must manually navigate to keyboard
❌ Can't type while in mouse mode
❌ Poor UX for text input scenarios
```

### After (v2.0 - Human-Centric Model)
```
5 Primary States (user-selected):
├── HOME
├── MEDIA
├── MOUSE
├── TAB
└── WINDOW

+ Overlay System (context-aware):
└── KEYBOARD_OVERLAY  ← Appears automatically when needed

Benefits:
✅ Keyboard is a tool that appears contextually
✅ Auto-triggers on text input clicks
✅ Can type while staying in mouse mode
✅ Natural, human-centric interaction
```

---

## 🏗️ New Architecture Components

### 1. State Machine Refactor (`core/state_machine.py`)

#### New Enum
```python
class AppState(Enum):
    HOME = 0
    MEDIA = 1
    MOUSE = 2
    TAB = 3      # Renumbered (was 4)
    WINDOW = 4   # Renumbered (was 5)
    # KEYBOARD removed as primary state
```

#### New Properties
```python
self.keyboard_overlay_active = False
self.overlay_trigger_reason = None  # 'text_input_click', 'manual', etc.
```

#### New Methods
```python
# Overlay Management
show_keyboard_overlay(reason='manual')
dismiss_keyboard_overlay()
toggle_keyboard_overlay()

# State Queries
has_keyboard_overlay()
get_effective_mode()  # Returns what user is actually interacting with
```

---

### 2. Context-Aware Text Detection (`modes/mouse_mode.py`)

#### New Method: `is_text_input_likely()`
Detects if a click was likely in a text input field using:

**Heuristics:**
1. **Active Window Detection**: Checks if current window is a text-heavy app
   - Browsers: Chrome, Edge, Firefox
   - Editors: Notepad, VS Code, Sublime
   - Communication: Outlook, Slack
   
2. **Click Position Analysis**: Avoids top menu bar (y > 100px)

3. **Fallback**: Conservative default if detection library unavailable

**Dependencies:**
- Optional: `pygetwindow` for window title detection
- Fallback: Simple pattern-based detection

---

### 3. Home Menu Redesign (`ui/menu_renderer.py`)

#### Before (6 buttons):
```
[Media]    [Mouse]
[Keyboard] [Tab]
[Window]   [Exit]
```

#### After (5 buttons):
```
[Media]  [Mouse]
[Tab]    [Window]
   [Exit]
```

**Keyboard removed** - now appears contextually in Mouse mode.

---

### 4. Gesture Handling Updates (`main.py`)

#### Mouse Mode Flow
```python
def handle_mouse_mode(air_push):
    # 1. Check if keyboard overlay is active
    if state_machine.has_keyboard_overlay():
        handle_keyboard_overlay()  # Keyboard takes priority
        return
    
    # 2. Normal mouse operations
    move_cursor()
    
    # 3. On click, check for text input context
    if air_push:
        mouse_mode.click()
        if mouse_mode.is_text_input_likely():
            state_machine.show_keyboard_overlay('text_input_click')
```

#### Keyboard Overlay Handling
```python
def handle_keyboard_overlay(air_push, sx, sy):
    # Dismiss gesture: Swipe down
    if detect_swipe_down():
        state_machine.dismiss_keyboard_overlay()
        return
    
    # Normal keyboard input
    handle_key_selection()
```

---

## 🎨 User Experience Flow

### Scenario 1: Typing in Browser
```
1. User enters Mouse Mode
2. User clicks on search bar in Chrome
   → Text input detected!
   → Keyboard overlay appears automatically
3. User types using virtual keyboard
4. User swipes down to dismiss keyboard
   → Returns to mouse control
```

### Scenario 2: Manual Keyboard Toggle
```
1. User in Mouse Mode
2. User performs special gesture (future: open palm + swipe up)
   → Keyboard overlay appears manually
3. User types
4. Swipe down to dismiss
```

---

## 🔧 Technical Implementation Details

### State Transitions

#### Primary State Changes
```python
# Changing primary state auto-dismisses keyboard overlay
def set_state(new_state):
    self.current_state = new_state
    self.dismiss_keyboard_overlay()  # Clean transition
```

#### Overlay Activation
```python
# Keyboard can appear over any primary state
def show_keyboard_overlay(reason):
    self.keyboard_overlay_active = True
    self.overlay_trigger_reason = reason
    print(f"[Overlay] Keyboard activated ({reason}) over {current_state}")
```

### HUD Rendering Logic
```python
if state_machine.is_mouse():
    if state_machine.has_keyboard_overlay():
        # Show keyboard buttons
        set_state_text("MOUSE + KEYBOARD")
        set_info_text("Type with keyboard | Swipe down to dismiss")
    else:
        # Normal mouse mode
        set_state_text("AIR MOUSE")
        set_info_text("Click text fields for keyboard")
```

---

## 📝 Migration Guide

### For Developers

#### 1. State Enum Changes
```python
# OLD
AppState.KEYBOARD  # ❌ No longer exists

# NEW
state_machine.has_keyboard_overlay()  # ✅ Check overlay status
state_machine.get_effective_mode()    # ✅ Get actual interaction mode
```

#### 2. Home Menu Buttons
```python
# OLD
6 buttons: media, mouse, keyboard, tab, window, exit

# NEW
5 buttons: media, mouse, tab, window, exit
# Keyboard removed from menu
```

#### 3. Gesture Handling
```python
# OLD
if state_machine.is_keyboard():
    handle_keyboard_mode()

# NEW
# Keyboard handling is now part of mouse_mode when overlay is active
if state_machine.is_mouse():
    if state_machine.has_keyboard_overlay():
        handle_keyboard_overlay()
```

---

## 🚀 Future Enhancements

### Planned Features
1. **Smart Trigger Refinement**
   - Machine learning for better text input detection
   - User-specific calibration

2. **Multi-Overlay Support**
   - Emoji picker overlay
   - Quick actions overlay
   - Settings overlay

3. **Gesture Library**
   - Open palm + swipe up = manual keyboard toggle
   - Two-finger pinch = zoom overlay
   - Fist = quick dismiss all overlays

4. **Context Awareness++**
   - Detect specific input types (email, URL, number)
   - Auto-suggest keyboard layouts (numeric, symbols)
   - Remember user preferences per application

---

## 🧪 Testing Checklist

### Functional Tests
- [ ] Home menu shows 5 buttons (no keyboard)
- [ ] Mouse mode works normally without keyboard
- [ ] Clicking in Chrome/Edge triggers keyboard overlay
- [ ] Keyboard overlay appears over mouse mode
- [ ] Swipe down dismisses keyboard overlay
- [ ] Changing modes dismisses keyboard overlay
- [ ] BACK button always visible and functional
- [ ] State display shows "MOUSE + KEYBOARD" when overlay active

### Edge Cases
- [ ] Keyboard overlay in non-text apps (should not trigger)
- [ ] Rapid mode switching (overlay should dismiss cleanly)
- [ ] Keyboard overlay + back button interaction
- [ ] Multiple clicks in text field (should not re-trigger)

---

## 📚 Related Files

### Modified Files
- `core/state_machine.py` - Core refactor with overlay system
- `modes/mouse_mode.py` - Added text input detection
- `ui/menu_renderer.py` - Removed keyboard button
- `main.py` - Updated gesture handling and HUD logic

### Unchanged Files
- `modes/keyboard_mode.py` - Still used, just triggered differently
- `core/gesture_detector.py` - No changes needed
- `ui/hud_overlay.py` - Works with new state system
- All other mode files

---

## 🎓 Design Principles

### 1. Human-Centric
> "Tools should appear when needed, not when navigated to."

The keyboard is a tool for text input, not a destination. It should appear contextually based on user intent.

### 2. Minimal Cognitive Load
> "Fewer decisions = better UX."

Reducing from 6 to 5 modes simplifies the mental model. The keyboard "just works" when you need it.

### 3. Graceful Degradation
> "Always have a fallback."

If text detection fails, users can still manually trigger the keyboard (future feature) or use physical keyboard.

### 4. Consistent Interaction
> "Same gestures, different contexts."

Swipe down always means "dismiss" - whether it's dismissing keyboard overlay or going back in other contexts.

---

## 📊 Metrics & Success Criteria

### Before Refactor
- **Modes**: 6
- **Clicks to type**: 2-3 (Home → Keyboard → Type)
- **Context switches**: High
- **User confusion**: "Where's the keyboard?"

### After Refactor
- **Modes**: 5 (+ 1 overlay)
- **Clicks to type**: 0-1 (Auto-trigger or 1 manual)
- **Context switches**: Low
- **User delight**: "It just knew I wanted to type!"

---

## 🔗 References

- [Original State Machine](core/state_machine.py)
- [Mouse Mode Text Detection](modes/mouse_mode.py)
- [Home Menu Redesign](ui/menu_renderer.py)
- [Main Application Flow](main.py)

---

**Version**: 2.0  
**Status**: ✅ Implemented  
**Next Review**: After user testing feedback
