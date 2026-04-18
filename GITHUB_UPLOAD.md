# 📤 Upload to GitHub Guide

## Step-by-Step Instructions

### 1. Initialize Git Repository (if not already done)

```powershell
cd c:\Users\HP\Documents\Project\Aether-Link

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Aether-Link touchless gesture interface"
```

### 2. Connect to GitHub Repository

```powershell
# Add remote repository
git remote add origin https://github.com/ShaluKesharwani20030421/AirControler.git

# Verify remote
git remote -v
```

### 3. Push to GitHub

```powershell
# Push to main branch
git push -u origin main
```

**If you get an error about branch name**, try:
```powershell
# Rename branch to main
git branch -M main

# Then push
git push -u origin main
```

### 4. If Repository Already Has Content

If the GitHub repo already exists with files:

```powershell
# Pull first (merge remote changes)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

**Or force push** (⚠️ WARNING: This will overwrite remote):
```powershell
git push -u origin main --force
```

---

## 🔐 Authentication

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Copy token
5. When prompted for password, paste token

### Option 2: GitHub CLI

```powershell
# Install GitHub CLI
winget install --id GitHub.cli

# Login
gh auth login

# Push
git push -u origin main
```

---

## 📝 Before Uploading - Checklist

### ✅ Files to Include
- [x] All source code (`.py` files)
- [x] `requirements.txt`
- [x] `README_GITHUB.md` (rename to `README.md`)
- [x] `.gitignore`
- [x] Documentation files (`.md`)
- [x] `models/hand_landmarker.task` (if < 100MB)

### ❌ Files to Exclude (Already in .gitignore)
- [x] `signatures/` folder (personal biometric data)
- [x] `__pycache__/` folders
- [x] `.pyc`, `.pyo` files
- [x] `venv/` folder
- [x] `.vscode/`, `.idea/` folders

---

## 🎯 Quick Upload Script

Save this as `upload_to_github.ps1`:

```powershell
# Navigate to project
cd c:\Users\HP\Documents\Project\Aether-Link

# Rename README for GitHub
if (Test-Path "README_GITHUB.md") {
    Copy-Item "README_GITHUB.md" "README.md" -Force
    Write-Host "✅ README.md created from README_GITHUB.md"
}

# Initialize git if needed
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git initialized"
}

# Add all files
git add .
Write-Host "✅ Files staged"

# Commit
$commitMsg = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Update: Aether-Link touchless interface"
}
git commit -m $commitMsg
Write-Host "✅ Changes committed"

# Add remote if not exists
$remoteExists = git remote | Select-String "origin"
if (-not $remoteExists) {
    git remote add origin https://github.com/ShaluKesharwani20030421/AirControler.git
    Write-Host "✅ Remote added"
}

# Rename branch to main
git branch -M main
Write-Host "✅ Branch renamed to main"

# Push
Write-Host "🚀 Pushing to GitHub..."
git push -u origin main

Write-Host ""
Write-Host "================================================================"
Write-Host "  ✅ Upload Complete!"
Write-Host "  🌐 View at: https://github.com/ShaluKesharwani20030421/AirControler"
Write-Host "================================================================"
```

**Run it**:
```powershell
.\upload_to_github.ps1
```

---

## 🔄 Updating After First Upload

After initial upload, use this for updates:

```powershell
# Stage changes
git add .

# Commit
git commit -m "Update: [describe your changes]"

# Push
git push
```

---

## 📦 Large Files (>100MB)

If `models/hand_landmarker.task` is >100MB, use Git LFS:

```powershell
# Install Git LFS
git lfs install

# Track large files
git lfs track "models/*.task"

# Add .gitattributes
git add .gitattributes

# Commit and push
git add models/hand_landmarker.task
git commit -m "Add MediaPipe model with LFS"
git push
```

---

## 🆘 Common Issues

### Issue: "fatal: remote origin already exists"
```powershell
# Remove existing remote
git remote remove origin

# Add again
git remote add origin https://github.com/ShaluKesharwani20030421/AirControler.git
```

### Issue: "Updates were rejected"
```powershell
# Pull first
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

### Issue: "Authentication failed"
- Use Personal Access Token instead of password
- Or use GitHub CLI: `gh auth login`

### Issue: "Large files detected"
- Use Git LFS (see above)
- Or add to `.gitignore` and provide download link in README

---

## 📋 Post-Upload Tasks

After successful upload:

1. **Add Repository Description**
   - Go to GitHub repo page
   - Click "About" settings (gear icon)
   - Add: "Touchless gesture interface using 3D hand tracking and depth camera"
   - Add topics: `gesture-recognition`, `mediapipe`, `computer-vision`, `touchless-interface`, `depth-camera`

2. **Add Repository Image**
   - Take screenshot of HUD
   - Upload to repo as `screenshot.png`
   - Set as social preview image

3. **Enable GitHub Pages** (Optional)
   - Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/docs` or `/` (root)

4. **Create Releases**
   - Go to Releases
   - Create new release
   - Tag: `v1.0.0`
   - Title: "Aether-Link v1.0 - Initial Release"
   - Description: List features and changes

---

## ✅ Verification

After upload, verify:

1. **All files uploaded**
   ```
   https://github.com/ShaluKesharwani20030421/AirControler
   ```

2. **README displays correctly**
   - Should show formatted markdown
   - Images/badges should load

3. **Clone test**
   ```powershell
   cd c:\temp
   git clone https://github.com/ShaluKesharwani20030421/AirControler.git
   cd AirControler
   python main.py
   ```

---

## 🎉 You're Done!

Your project is now live on GitHub! 🚀

**Share it**:
- LinkedIn
- Twitter
- Reddit (r/Python, r/computervision)
- Dev.to
- Hacker News

**Next steps**:
- Add CI/CD (GitHub Actions)
- Create demo video
- Write blog post
- Submit to Awesome Lists

---

**Need help?** Open an issue on GitHub or contact support.
