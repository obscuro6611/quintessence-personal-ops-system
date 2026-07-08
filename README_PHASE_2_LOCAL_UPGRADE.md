# Quintessence Phase 2 — Local-Only Operating System Upgrade

This patch keeps Quintessence local-only and single-user, while upgrading both the UX and the local utility layer.

## What this upgrade adds

- Observatory aesthetic polish: navy, gold, celestial/compass accents, serif headings, glass panels.
- Backup and restore scripts.
- Export script and backend export endpoint.
- Global local search.
- Better Evidence Engine support: evidence scoring, STAR draft, resume bullet bank endpoint.
- Better linking API for Evidence -> Capabilities/Projects/Tasks/FGAs/Opportunities.
- Local file utility endpoints and storage/data folder scripts.
- Weekly Review archive: save and review prior snapshots.
- Activity timeline.
- Capability progress and history support.
- Settings page/API.
- Additional Windows launcher utilities.

## How to apply

1. Close existing Quintessence backend/frontend terminal windows.
2. Extract this upgrade ZIP.
3. Copy all contents of `quintessence_phase_2_local_upgrade` into your existing Quintessence root folder.
4. Choose **Replace files in destination**.

Your root folder is likely:

```text
C:\Users\rm118\OneDrive\Desktop\Personal Organizer\quintessence
```

## One-time frontend reset

```powershell
cd "C:\Users\rm118\OneDrive\Desktop\Personal Organizer\quintessence\frontend"
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
```

## Launch

Double-click:

```text
Launch Quintessence.bat
```

## Recommended first actions after launch

1. Open **Settings** and confirm local folders.
2. Open **Backup / Export** and run a backup.
3. Open **Global Search** and search across existing seed data.
4. Open **Evidence** and review evidence quality/completeness fields.
5. Save a Weekly Review snapshot.
