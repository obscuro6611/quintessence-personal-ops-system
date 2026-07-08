# Phase 1.1 UX Polish Notes

This upgrade is intentionally frontend-friendly and does not redesign the product architecture.

## Changes

- Replaces raw JSON panels with module-specific cards.
- Adds modern Mission Control dashboard cards.
- Adds polished Evidence Repository cards with resume bullet and interview story sections.
- Adds visual fit bars for Career Pipeline.
- Adds badges for status, priority, completion, and evidence states.
- Adds basic search within modules.
- Pins Tailwind to v3.4.17 to avoid the Tailwind v4 PostCSS plugin mismatch.
- Adds Windows launch and stop batch files.

## Install

Copy the files in this upgrade zip into your existing Quintessence root folder and allow overwrite.

Then run:

```powershell
cd "path\to\quintessence\frontend"
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm install
```

Then double-click:

```text
Launch Quintessence.bat
```
