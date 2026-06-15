# Privacy and FYP Protection Review

Reviewed on June 15, 2026 before submission packaging.

## Included images

All six copied demo images were visually reviewed.

- No identifiable faces are visible.
- No readable vehicle number plates are visible.
- No personal names, student IDs, account details, or confidential documents are visible.
- No API keys, passwords, serial-port details, or private configuration are included.

## Location data

- Demo coordinates are rounded to four decimal places.
- The app uses a relative illustrated map rather than an external live-map service.
- Road names and general Cyberjaya/MMU-area labels are included only to make the prototype understandable.

## FYP isolation

- The app does not import parent FYP Python modules.
- Model weights, raw logs, telemetry, labels, configuration, and hardware settings are excluded.
- Mutable state is confined to `runtime/`, which is ignored by Git and Docker.
- The source ZIP contains only the challenge folder's prepared files.

Supervisor or university approval remains an external policy check and cannot be completed by the software itself.
