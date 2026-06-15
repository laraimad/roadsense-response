import json
import tempfile
import unittest
from pathlib import Path

from app import create_app


class RoadSenseAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "incidents.json"
        self.app = create_app(self.data_path)
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_and_incident_list(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.get_json()), 6)

    def test_workflow_update_persists(self):
        response = self.client.patch(
            "/api/incidents/RS-1051",
            data=json.dumps({"status": "scheduled", "assignee": "Team C", "notes": "Booked"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        saved = {item["id"]: item for item in self.client.get("/api/incidents").get_json()}
        self.assertEqual(saved["RS-1051"]["status"], "scheduled")
        self.assertEqual(saved["RS-1051"]["assignee"], "Team C")
        self.assertIn("Status changed to scheduled", saved["RS-1051"]["history"][-1]["summary"])

    def test_invalid_status_is_rejected(self):
        response = self.client.patch(
            "/api/incidents/RS-1051",
            json={"status": "unknown"},
        )
        self.assertEqual(response.status_code, 400)

    def test_scheduling_requires_an_assignee(self):
        response = self.client.patch(
            "/api/incidents/RS-1051",
            json={"status": "scheduled", "assignee": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("assign a team", response.get_json()["error"])

    def test_export_is_csv(self):
        response = self.client.get("/api/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.content_type)
        self.assertIn(b"RS-1042", response.data)

    def test_security_headers_are_present(self):
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")


if __name__ == "__main__":
    unittest.main()
