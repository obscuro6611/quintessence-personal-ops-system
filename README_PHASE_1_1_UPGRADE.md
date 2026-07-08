# Quintessence Phase 1.1 Upgrade

This patch improves the UX and adds a Windows double-click launcher.

## How to apply

1. Extract this zip.
2. Copy everything inside `quintessence_phase_1_1_upgrade` into your existing Quintessence root folder:

```text
C:\Users\rm118\OneDrive\Desktop\Personal Organizer\quintessence\quintessence
```

3. Choose **Replace files** when Windows asks.

## One-time frontend reinstall

Open PowerShell:

```powershell
cd "C:\Users\rm118\OneDrive\Desktop\Personal Organizer\quintessence\quintessence\frontend"
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
```

## Launch

Double-click:

```text
Launch Quintessence.bat
```

The launcher will:

- start the backend
- start the frontend
- open http://localhost:5173

## Stop

Double-click:

```text
Stop Quintessence.bat
```
