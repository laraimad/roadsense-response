# Verification Report

Completed on June 15, 2026.

## Automated tests

Six Python `unittest` tests pass:

- Health endpoint and incident loading.
- Workflow updates persist.
- Invalid statuses are rejected.
- Scheduling without an assignee is rejected.
- CSV export contains incident data.
- Security headers are present.

JavaScript syntax was checked with Node.js.

## Clean environment

A new Python 3.12.13 virtual environment was created outside the project. Only `requirements.txt` was installed. The app started on a separate port and `/api/health` returned `{"status":"ok"}`.

## Browser workflow

The app was exercised at a real 390 by 844 mobile viewport:

- Viewport width: 390 pixels.
- Document width: 390 pixels; no horizontal overflow.
- Six incident rows rendered.
- Searching `Jalan Teknokrat` returned `RS-1038` and `RS-1036`.
- Scheduling without a team produced the expected validation message.
- A valid status, team, and note update succeeded.
- The update and activity history persisted after reload.
- CSV export returned the expected records and `updated_at` field.
- Desktop and mobile screenshots were visually reviewed.

## Submission package

- File: `output/source/RoadSense_Response_Source.zip`
- Entries: 29
- SHA-256 checksum: `output/source/RoadSense_Response_Source.sha256`
- Confirmed absent: `.venv`, `runtime`, `__pycache__`, and `.pyc` files.
