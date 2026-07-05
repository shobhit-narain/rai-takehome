# Seed Data

## Overview

This directory stores deterministic seed files used to initialize the local SQLite database and the mock HCM external state.

Generated files:

- `users.csv`
- `leave_balances.csv`
- `leave_requests.csv`
- `hcm_configs.csv`
- `script_runs.csv`
- `audit_events.csv`
- `mock_hcm_state.json`

## Generate Seed Data

Run:

```bash
python scripts/generate_seed_data.py
```

This creates a default dataset with:

- 5 admins
- 250 managers
- 5000 employees
- balances for PTO and sick leave
- leave requests for a subset of employees
- HCM config rows
- sample script run history
- audit events
- external mock HCM state

## Custom Generation

Example with custom counts:

```bash
python scripts/generate_seed_data.py \
  --employee-count 3000 \
  --manager-count 150 \
  --admin-count 3 \
  --seed 20260705
```

## Determinism

The generator uses a fixed random seed by default. Running the script with the same parameters produces the same outputs.

## Import Flow

After generating the files, load them into the local DB with:

```bash
python scripts/reset_local_db.py
python scripts/seed_local_db.py
```