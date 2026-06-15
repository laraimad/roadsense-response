# RoadSense Response

RoadSense Response is a standalone web prototype for the Shortcut Asia Internship Challenge 2026. It turns vehicle-based pothole detections into an explainable incident queue that a road maintenance operator can verify, assign, track, and export.

## Key features

1. Evidence-based incident triage
   - Relative incident map and searchable, filterable, sortable repair queue.
   - Camera evidence, model confidence, impact strength, vehicle speed, and recurrence.
   - Explainable severity score and recommended action.

2. Repair workflow
   - Statuses from new through resolved or dismissed.
   - Team assignment and operator notes.
   - Validation for repair handoffs and timestamped activity history.
   - Local JSON persistence, resettable demo state, and CSV export.

## Run locally

Requirements: Python 3.10 or newer.

```powershell
cd C:\Users\larae\OneDrive\pothole_fyp\shortcut_asia_challenge_2026
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5051`.

You can also run `powershell -ExecutionPolicy Bypass -File .\run.ps1` to perform the same isolated setup.

## Deploy

The repository includes a Render blueprint and Dockerfile.

Render:

1. Push this folder to a separate GitHub repository.
2. In Render, choose **New > Blueprint** and connect the repository.
3. Render reads `render.yaml`, installs the dependencies, starts Gunicorn, and checks `/api/health`.

Docker:

```powershell
docker build -t roadsense-response .
docker run --rm -p 5051:5051 roadsense-response
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Isolation from the FYP

This folder is self-contained. The app does not import or modify any parent FYP module, model, configuration, labels, logs, or live sensor data. It contains only copied demo screenshots and a small manually prepared seed dataset. All app changes are written to `runtime/incidents.json` inside this folder.

For submission, publish this folder as its own repository. Do not publish the parent FYP repository unless your supervisor and university policy allow it.

## Submission files

- `CHALLENGE_REQUIREMENTS.md`: verified requirements from the supplied brief.
- `SUBMISSION_CHECKLIST.md`: final links and checks needed before submitting.
- `REPOSITORY_SETUP.md`: exact repository and deployment handoff steps.
- `VERIFICATION_REPORT.md`: clean-environment, browser, test, and package evidence.
- `PRIVACY_REVIEW.md`: image, location, and FYP-isolation review.
- `docs/SUBMISSION_DOCUMENTATION.md`: approach, decisions, architecture, and flows.
- `docs/DEMO_SCRIPT.md`: a 3-5 minute video plan.
- `output/pdf/RoadSense_Response_Documentation.pdf`: two-page submission document.
- `output/source/RoadSense_Response_Source.zip`: repository-ready source archive.

## Tech stack

- Python and Flask
- HTML, CSS, and vanilla JavaScript
- JSON file persistence
- Gunicorn for Linux deployment
- Python `unittest`

The prototype intentionally avoids cloud services and external databases so reviewers can run it quickly.
