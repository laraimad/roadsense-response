from __future__ import annotations

import csv
import io
import json
import os
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file


BASE_DIR = Path(__file__).resolve().parent
SEED_DATA = BASE_DIR / "data" / "incidents.seed.json"
RUNTIME_DATA = BASE_DIR / "runtime" / "incidents.json"
VALID_STATUSES = {"new", "verified", "scheduled", "in_repair", "resolved", "dismissed"}
EDITABLE_FIELDS = {"status", "assignee", "notes"}
ASSIGNEE_REQUIRED_STATUSES = {"scheduled", "in_repair", "resolved"}


class IncidentStore:
    def __init__(self, path: Path = RUNTIME_DATA, seed_path: Path = SEED_DATA) -> None:
        self.path = path
        self.seed_path = seed_path
        self._lock = threading.Lock()
        self._ensure_data()

    def _ensure_data(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            shutil.copyfile(self.seed_path, self.path)

    def _read(self) -> list[dict[str, Any]]:
        self._ensure_data()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, incidents: list[dict[str, Any]]) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(incidents, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._read()

    def update(self, incident_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        unknown = set(changes) - EDITABLE_FIELDS
        if unknown:
            raise ValueError(f"unsupported fields: {', '.join(sorted(unknown))}")

        for field in EDITABLE_FIELDS:
            if field in changes and not isinstance(changes[field], str):
                raise ValueError(f"{field} must be text")

        status = changes.get("status")
        if status is not None and status not in VALID_STATUSES:
            raise ValueError("invalid status")

        with self._lock:
            incidents = self._read()
            for incident in incidents:
                if incident["id"] != incident_id:
                    continue
                next_status = changes.get("status", incident.get("status", "new")).strip()
                next_assignee = changes.get("assignee", incident.get("assignee", "")).strip()[:120]
                if next_status in ASSIGNEE_REQUIRED_STATUSES and not next_assignee:
                    raise ValueError("assign a team before scheduling, repairing, or resolving an incident")

                changes_made: list[str] = []
                for field in EDITABLE_FIELDS:
                    if field in changes:
                        limit = 120 if field == "assignee" else 1000
                        value = changes[field].strip()[:limit]
                        if incident.get(field, "") != value:
                            changes_made.append(field)
                            incident[field] = value

                if not changes_made:
                    return incident

                updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
                incident["updated_at"] = updated_at
                history = incident.setdefault("history", [])
                history.append({
                    "timestamp": updated_at,
                    "status": incident["status"],
                    "assignee": incident.get("assignee", ""),
                    "summary": self._history_summary(changes_made, incident),
                })
                incident["history"] = history[-50:]
                self._write(incidents)
                return incident
        raise KeyError(incident_id)

    @staticmethod
    def _history_summary(changes_made: list[str], incident: dict[str, Any]) -> str:
        descriptions = []
        if "status" in changes_made:
            descriptions.append(f"Status changed to {incident['status'].replace('_', ' ')}")
        if "assignee" in changes_made:
            descriptions.append(f"Assigned to {incident.get('assignee') or 'Unassigned'}")
        if "notes" in changes_made:
            descriptions.append("Operator notes updated")
        return ". ".join(descriptions) + "."

    def reset(self) -> list[dict[str, Any]]:
        with self._lock:
            shutil.copyfile(self.seed_path, self.path)
            return self._read()


def build_summary(incidents: list[dict[str, Any]]) -> dict[str, Any]:
    active = [item for item in incidents if item["status"] not in {"resolved", "dismissed"}]
    urgent = [item for item in active if item["severity_score"] >= 70]
    resolved = [item for item in incidents if item["status"] == "resolved"]
    return {
        "total": len(incidents),
        "active": len(active),
        "urgent": len(urgent),
        "resolved": len(resolved),
        "average_severity": round(
            sum(item["severity_score"] for item in incidents) / len(incidents), 1
        ) if incidents else 0,
    }


def create_app(data_path: Path | None = None) -> Flask:
    app = Flask(__name__)
    store = IncidentStore(data_path or RUNTIME_DATA)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/incidents")
    def incidents():
        return jsonify(store.list())

    @app.get("/api/summary")
    def summary():
        return jsonify(build_summary(store.list()))

    @app.patch("/api/incidents/<incident_id>")
    def update_incident(incident_id: str):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "JSON object required"}), 400
        try:
            incident = store.update(incident_id, payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except KeyError:
            return jsonify({"error": "incident not found"}), 404
        return jsonify(incident)

    @app.post("/api/reset")
    def reset():
        return jsonify({"incidents": store.reset()})

    @app.get("/api/export.csv")
    def export_csv():
        output = io.StringIO()
        fields = [
            "id", "road", "segment", "severity_level", "severity_score", "status",
            "assignee", "latitude", "longitude", "captured_at", "updated_at",
            "recommended_action", "notes",
        ]
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(store.list())
        payload = io.BytesIO(output.getvalue().encode("utf-8"))
        return send_file(
            payload,
            mimetype="text/csv",
            as_attachment=True,
            download_name="roadsense-repair-queue.csv",
        )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5051"))
    create_app().run(host="0.0.0.0", port=port, debug=False)
