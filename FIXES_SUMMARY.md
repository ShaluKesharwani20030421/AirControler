# Latest Fixes - April 18, 2026

## ✅ Issue 1: Cursor X-Axis Inverted (FIXED)

### Problem
When moving hand **RIGHT**, cursor moved **LEFT** (inverted X-axis)

### Root Cause
MediaPipe returns normalized coordinates where:
- Hand at left edge → `x = 0.0`
- Hand at right edge → `x = 1.0`

But from camera's perspective, this is **mirrored** (like looking in a mirror).

### Solution
**Flipped X-axis** in `core/depth_lock.py` line 152:
```python
# Before: cursor follows camera view (inverted)
smooth_nx = cs * self.prev_norm_x + (1 - cs) * idx_lm.x

# After: mirror effect (natural for user)
flipped_x = 1.0 - idx_lm.x
smooth_nx = cs * self.prev_norm_x + (1 - cs) * flipped_x
```

### Result
✅ **Hand moves RIGHT → Cursor moves RIGHT** (natural, intuitive)

---

## ✅ Issue 2: Keyboard Not Accessible Everywhere (FIXED)

### Problem
- Keyboard was removed from HOME menu
- Only appeared automatically in Mouse mode on text input click
- User wanted **manual control** to call keyboard **anytime**

### Solution

#### 1. **Added Keyboard Back to HOME Menu**
`ui/menu_renderer.py` - Now shows **6 buttons** (2×3 grid):
```
┌─────────────┬─────────────┐
│   Media     │    Mouse    │
├─────────────┼─────────────┤
│    Tab      │   Window    │
├─────────────┼─────────────┤
│  Keyboard   │    Exit     │
└─────────────┴─────────────┘
```

#### 2. **Global Keyboard Shortcut - Open Palm**
Added **Open Palm** gesture to toggle keyboard from **ANY mode**:
- **Media mode** → Open Palm = Show Keyboard ⌨️
- **Tab mode** → Open Palm = Show Keyboard ⌨️
- **Window mode** → Open Palm = Show Keyboard ⌨️
- **Mouse mode** → Open Palm = Show Keyboard ⌨️ (plus auto-detect on text click)

#### 3. **How It Works**
```python
# In ANY mode (media, tab, window):
if self.gesture_detector.detect_open_palm(self.current_hand_data):
    self.state_machine.show_keyboard_overlay('manual')
    return
```

When keyboard overlay is active:
- All gestures go to keyboard
- **BACK button** dismisses keyboard
- Returns to previous mode

### Result
✅ **Keyboard accessible from EVERYWHERE**:
1. **HOME menu** → Click "Keyboard" button
2. **Any mode** → Open Palm gesture
3. **Mouse mode** → Auto-appears on text input click (still works)

---

## 🎮 Updated Gesture Map

### HOME Mode
| Gesture | Action |
|---------|--------|
| Air-Push on button | Select mode |
| Dwell 1.5s on button | Select mode (alternative) |

### Media Mode
| Gesture | Action |
|---------|--------|
| **Open Palm** | **Show Keyboard** ⌨️ |
| Swipe Up | Volume Up |
| Swipe Down | Volume Down |
| BACK button | Return to HOME |

### Mouse Mode
| Gesture | Action |
|---------|--------|
| Move hand | Move cursor |
| Air-Push | Click |
| **Open Palm** | **Show Keyboard** ⌨️ |
| Auto-detect | Keyboard on text input click |
| BACK button | Return to HOME |

### Tab Mode
| Gesture | Action |
|---------|--------|
| **Open Palm** | **Show Keyboard** ⌨️ |
| Swipe Right | Next Tab |
| Swipe Left | Previous Tab |
| Air-Push | Close Tab |
| BACK button | Return to HOME |

### Window Mode
| Gesture | Action |
|---------|--------|
| **Open Palm** | **Show Keyboard** ⌨️ |
| Swipe Right | Next Window |
| Swipe Left | Previous Window |
| Swipe Up | Task View |
| Swipe Down | Minimize |
| BACK button | Return to HOME |

### Keyboard Overlay (Active in ANY mode)
| Gesture | Action |
|---------|--------|
| Air-Push on key | Type character |
| Dwell 1.5s on key | Type character |
| BACK button | Dismiss keyboard |

---

## 🔧 Files Modified

### 1. `core/depth_lock.py`
**Line 152**: Flipped X-axis for natural cursor movement
```python
flipped_x = 1.0 - idx_lm.x  # Mirror effect
```

### 2. `ui/menu_renderer.py`
**Lines 17-45**: Added Keyboard button to HOME menu (2×3 grid)
```python
{'id': 'keyboard', 'text': '⌨️  Keyboard', ...}
```

### 3. `main.py`
**Multiple locations**: Added keyboard handling

- **Line 343**: HOME menu keyboard button handler
- **Lines 349-361**: Media mode keyboard overlay + Open Palm
- **Lines 417-429**: Tab mode keyboard overlay + Open Palm  
- **Lines 445-457**: Window mode keyboard overlay + Open Palm

---

## 🎯 User Experience Improvements

### Before
❌ Cursor inverted (confusing)  
❌ Keyboard only in HOME menu  
❌ No quick access to keyboard  
❌ Had to exit mode to type  

### After
✅ **Cursor natural** (hand right = cursor right)  
✅ **Keyboard in HOME menu** (6 buttons)  
✅ **Open Palm = Keyboard** (global shortcut)  
✅ **Type from anywhere** (no mode switching)  

---

## 📊 Testing Checklist

### Test Cursor Direction
- [ ] Move hand **RIGHT** → Cursor moves **RIGHT** ✅
- [ ] Move hand **LEFT** → Cursor moves **LEFT** ✅
- [ ] Move hand **UP** → Cursor moves **UP** ✅
- [ ] Move hand **DOWN** → Cursor moves **DOWN** ✅

### Test Keyboard Access
- [ ] HOME menu → Click "Keyboard" button → Keyboard appears ✅
- [ ] Media mode → Open Palm → Keyboard appears ✅
- [ ] Tab mode → Open Palm → Keyboard appears ✅
- [ ] Window mode → Open Palm → Keyboard appears ✅
- [ ] Mouse mode → Open Palm → Keyboard appears ✅
- [ ] Mouse mode → Click text field → Keyboard auto-appears ✅
- [ ] Keyboard active → BACK button → Keyboard dismisses ✅

---

## 🚀 Quick Test Commands

```powershell
# Delete signature to start unlocked (for testing)
del signatures\my_signature.json

# Run app
python main.py

# Test sequence:
# 1. Move hand right/left → Check cursor follows correctly
# 2. Go to Media mode → Open Palm → Keyboard should appear
# 3. Press BACK → Keyboard dismisses, back to Media
# 4. Go to Tab mode → Open Palm → Keyboard appears
# 5. Go to Mouse mode → Open Palm → Keyboard appears
```

---

## 💡 Pro Tips

### Cursor Control
- **Natural movement**: Like pointing at a mirror
- **Smooth tracking**: Triple EMA smoothing (depth + normalized + screen)
- **No jitter**: Comfortable for precise control

### Keyboard Access
- **Quick access**: Open Palm from anywhere
- **No mode switching**: Type without leaving current mode
- **Auto-detect**: Still works in Mouse mode for text fields
- **Easy dismiss**: BACK button or Open Palm again

---

## 📝 Summary

**Both issues resolved!**

1. ✅ **Cursor X-axis fixed** - Natural mirror-like movement
2. ✅ **Keyboard everywhere** - HOME button + Open Palm shortcut

**System is now intuitive and user-friendly!** 🎉
