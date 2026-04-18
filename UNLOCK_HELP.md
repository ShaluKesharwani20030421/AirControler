# 🆘 LOCKED OUT? - Emergency Unlock Guide

## If You Forgot Your Signature

### ⚡ Quick Fix (30 seconds)

**Option 1: Double-click the batch file**
```
RESET_SIGNATURE.bat
```
✅ Done! Signature deleted, app will start unlocked.

**Option 2: PowerShell script**
```powershell
.\reset_signature.ps1
```

**Option 3: Manual delete**
```powershell
del signatures\my_signature.json
```

Then restart the app:
```powershell
python main.py
```

---

## Understanding the Lock System

### How It Works
1. **Signature exists** → App starts **LOCKED** 🔒
2. **No signature** → App starts **UNLOCKED** 🔓

### Current Settings (User-Friendly)
- **Threshold**: 350 (very forgiving)
- **Failed attempts**: Shows counter
- **After 3 fails**: Emergency bypass instructions appear
- **Unlimited tries**: No permanent lockout

---

## Tips for Success

### ✅ Good Signature Patterns
- **Circle** - Draw a circle, move hand forward/back
- **Figure-8** - Draw "8" shape with depth variation
- **Triangle** - 3 corners, push/pull at each corner
- **Your Initials** - Draw letters with 3D motion

### ❌ Bad Patterns (Will Fail)
- Flat 2D shapes (no depth)
- Random movements
- Too fast (tracking lost)
- Different pattern each time

### 💡 Pro Tips
1. **Practice first** - Do the pattern 3-4 times before recording
2. **Keep it simple** - Complex patterns are hard to repeat
3. **Exaggerate depth** - Move forward/backward clearly
4. **Smooth motions** - Don't jerk your hand
5. **Same speed** - Try to match recording speed

---

## Current Threshold Explained

**DTW Distance** measures how different your pattern is:
- **0-100**: Nearly identical ✅
- **100-250**: Very similar ✅
- **250-350**: Similar (current threshold) ✅
- **350-500**: Somewhat similar ⚠️
- **500+**: Different pattern ❌

**Your threshold: 350** (forgiving)

If you want **stricter** security, edit `main.py` line 63:
```python
threshold=200.0,  # Stricter
```

If you want **more forgiving**, increase it:
```python
threshold=500.0,  # Very forgiving
```

---

## Troubleshooting

### "Always rejected, even with same pattern"
**Solution**: Increase threshold
```python
# In main.py line 63
threshold=500.0,  # or even 1000.0
```

### "Want to disable signature completely"
**Solution**: Just delete the file
```powershell
del signatures\my_signature.json
```
App will start unlocked every time.

### "Want to re-record signature"
**Solution**: Delete old one, record new
```powershell
del signatures\my_signature.json
python record_signature.py
```

### "Locked out right now, need access NOW"
**Solution**: Emergency bypass
```powershell
# Quick delete
del signatures\my_signature.json

# Or use batch file
RESET_SIGNATURE.bat

# Then restart
python main.py
```

---

## Making It Optional

If you want signature lock to be **optional** (not automatic):

### Edit `main.py` line 58:
```python
# BEFORE (auto-lock if file exists):
self.state_machine = StateMachine(require_auth=sig_exists)

# AFTER (always unlocked):
self.state_machine = StateMachine(require_auth=False)
```

Then signature file is ignored, app always starts unlocked.

---

## Quick Commands

```powershell
# Reset signature (emergency)
RESET_SIGNATURE.bat

# Or manual
del signatures\my_signature.json

# Record new signature
python record_signature.py

# Run app
python main.py

# Check if signature exists
dir signatures\my_signature.json
```

---

## Summary

**Locked out?** → Run `RESET_SIGNATURE.bat` → Done!

**Want easier unlock?** → Increase threshold in `main.py` line 63

**Don't want lock?** → Delete signature file or set `require_auth=False`

**The system is now USER-FRIENDLY** ✅
- Shows attempt counter
- Gives helpful hints
- Emergency bypass after 3 fails
- More forgiving threshold (350)
- Easy reset scripts

**You're in control!** 🎉
