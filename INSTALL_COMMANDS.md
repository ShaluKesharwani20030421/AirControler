# Installation Commands - Quick Reference

## 🚀 Quick Install (All Dependencies)

### Option 1: PowerShell Script (Recommended)
```powershell
# Run the automated installer
.\install_dependencies.ps1
```

### Option 2: Manual Installation
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all at once
pip install pyorbbecsdk2==2.0.18 opencv-python==4.8.1.78 numpy==1.26.2 mediapipe==0.10.14 PyQt6==6.6.1 pyautogui==0.9.54 fastdtw==0.3.4 scipy==1.11.4 pygetwindow==0.0.9
```

### Option 3: From requirements.txt
```powershell
pip install -r requirements.txt
```

---

## 📦 Individual Package Installation

### Core Dependencies
```powershell
# Orbbec Camera SDK
pip install pyorbbecsdk2==2.0.18

# Computer Vision
pip install opencv-python==4.8.1.78

# Numerical Computing
pip install numpy==1.26.2

# Hand Tracking AI
pip install mediapipe==0.10.14

# GUI Framework
pip install PyQt6==6.6.1

# System Automation
pip install pyautogui==0.9.54
```

### Security Dependencies (3D Biometric)
```powershell
# Dynamic Time Warping
pip install fastdtw==0.3.4

# Scientific Computing
pip install scipy==1.11.4
```

### Optional Dependencies
```powershell
# Window Detection (for context-aware keyboard)
pip install pygetwindow==0.0.9
```

---

## 🗑️ Uninstall Commands

### Option 1: PowerShell Script
```powershell
# Run the automated uninstaller
.\uninstall_dependencies.ps1
```

### Option 2: Manual Uninstall
```powershell
# Uninstall all Aether-Link dependencies
pip uninstall -y pyorbbecsdk2 opencv-python numpy mediapipe PyQt6 pyautogui fastdtw scipy pygetwindow
```

### Option 3: Individual Uninstall
```powershell
# Uninstall one by one
pip uninstall pyorbbecsdk2
pip uninstall opencv-python
pip uninstall numpy
pip uninstall mediapipe
pip uninstall PyQt6
pip uninstall pyautogui
pip uninstall fastdtw
pip uninstall scipy
pip uninstall pygetwindow
```

---

## 🔄 Update Commands

### Update All Dependencies
```powershell
# Update to latest compatible versions
pip install --upgrade pyorbbecsdk2 opencv-python numpy mediapipe PyQt6 pyautogui fastdtw scipy pygetwindow
```

### Update Specific Package
```powershell
# Example: Update MediaPipe
pip install --upgrade mediapipe
```

### Reinstall (Force)
```powershell
# Force reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

---

## 🔍 Verification Commands

### Check Installed Versions
```powershell
# List all installed packages
pip list

# Check specific package
pip show mediapipe

# Check Aether-Link packages only
pip list | Select-String -Pattern "pyorbbecsdk2|opencv-python|numpy|mediapipe|PyQt6|pyautogui|fastdtw|scipy|pygetwindow"
```

### Test Imports
```powershell
# Test if all packages can be imported
python -c "import pyorbbecsdk; import cv2; import numpy; import mediapipe; import PyQt6; import pyautogui; import fastdtw; import scipy; print('All imports successful!')"
```

---

## 🐍 Virtual Environment Commands

### Create Virtual Environment
```powershell
# Create venv
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (CMD)
venv\Scripts\activate.bat
```

### Deactivate Virtual Environment
```powershell
deactivate
```

### Delete Virtual Environment
```powershell
# Deactivate first, then delete folder
Remove-Item -Recurse -Force venv
```

---

## 🛠️ Troubleshooting Commands

### Fix Pip Issues
```powershell
# Repair pip
python -m ensurepip --upgrade
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge
```

### Fix Package Conflicts
```powershell
# Uninstall all, then reinstall
pip freeze > temp_packages.txt
pip uninstall -y -r temp_packages.txt
pip install -r requirements.txt
Remove-Item temp_packages.txt
```

### Fix Visual C++ Issues (for scipy, fastdtw)
```powershell
# Install pre-built wheels
pip install --only-binary :all: scipy fastdtw
```

---

## 📋 Quick Copy-Paste Commands

### Fresh Install (Copy All)
```powershell
python -m pip install --upgrade pip
pip install pyorbbecsdk2==2.0.18
pip install opencv-python==4.8.1.78
pip install numpy==1.26.2
pip install mediapipe==0.10.14
pip install PyQt6==6.6.1
pip install pyautogui==0.9.54
pip install fastdtw==0.3.4
pip install scipy==1.11.4
pip install pygetwindow==0.0.9
```

### Complete Uninstall (Copy All)
```powershell
pip uninstall -y pyorbbecsdk2
pip uninstall -y opencv-python
pip uninstall -y numpy
pip uninstall -y mediapipe
pip uninstall -y PyQt6
pip uninstall -y pyautogui
pip uninstall -y fastdtw
pip uninstall -y scipy
pip uninstall -y pygetwindow
```

---

## 🎯 Platform-Specific Notes

### Windows
```powershell
# Enable script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run PowerShell scripts
.\install_dependencies.ps1
```

### Linux/Mac (if porting)
```bash
# Use bash instead of PowerShell
chmod +x install_dependencies.sh
./install_dependencies.sh
```

---

## 📊 Dependency Tree

```
Aether-Link
├── Core
│   ├── pyorbbecsdk2 (camera)
│   ├── opencv-python (image processing)
│   ├── numpy (arrays)
│   ├── mediapipe (hand tracking)
│   ├── PyQt6 (GUI)
│   └── pyautogui (system control)
├── Security
│   ├── fastdtw (signature matching)
│   └── scipy (scientific computing)
└── Optional
    └── pygetwindow (window detection)
```

---

## ✅ Installation Checklist

- [ ] Python 3.12.x installed
- [ ] Pip upgraded to latest
- [ ] Virtual environment created (optional)
- [ ] Core dependencies installed
- [ ] Security dependencies installed
- [ ] Optional dependencies installed
- [ ] All imports tested successfully
- [ ] Orbbec camera connected
- [ ] Test run: `python main.py`

---

**Last Updated**: April 18, 2026  
**Python Version**: 3.12.0  
**Total Dependencies**: 9 packages
