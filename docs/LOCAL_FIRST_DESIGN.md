# Local-First Design

Quintessence is intentionally local-first.

It is designed to live on one person's machine as a private personal operations system.

## Why Local-First?

The system manages potentially sensitive personal information:

- career opportunities
- evidence artifacts
- decisions
- notes
- personal goals
- weekly reviews
- capability development history

For that reason, the first design constraint is local ownership.

## Local-Only Principles

Quintessence follows these principles:

1. Private by default  
   Data lives on the local machine unless the user chooses otherwise.

2. No cloud requirement  
   The app does not require cloud storage, external authentication, or hosted services.

3. No external AI dependency  
   AI Workspace is storage-first. Evidence draft generation is template/rule-based in the MVP.

4. Portable data  
   Backup and export utilities are included so data is not trapped inside the app.

5. Single-user simplicity  
   The app is designed for one user, not a multi-user organisation.

6. Evidence ownership  
   Artifacts and evidence files are stored locally under backend/storage.

## Data Safety

The GitHub portfolio version should not contain real personal data.

Excluded from Git:

- backend/.env
- frontend/.env
- backend/data/
- backend/storage/
- backend/backups/
- backend/exports/
- database files
- zip files
- uploaded evidence
- backups
- exports

## Local Runtime Flow

Launch Quintessence.bat starts the backend, starts the frontend, and opens the browser at localhost.

The app is used through:

http://localhost:5173

## Design Trade-Offs

Quintessence deliberately avoids:

- cloud sync
- multi-user accounts
- role-based permissions
- enterprise administration
- external AI provider requirements
- complex deployment pipelines

These are not weaknesses for this project. They are intentional constraints that support the purpose of the tool.

## Intended Use

Quintessence is intended to become a private operational hub for:

- execution
- capability growth
- evidence generation
- career preparation
- decision traceability
- weekly review
- knowledge management
