"""HTTP integration tests for the local GhostQueue demo."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from web_demo import Handler

class WebDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        data = response.read()
        status = response.status
        csp = response.getheader("Content-Security-Policy")
        conn.close()
        return status, data, csp

    def test_frontend_and_assets(self):
        for path, marker in [("/", b"GHOSTQUEUE"), ("/static/app.js", b"/api/analyze"), ("/static/style.css", b".hero"), ("/api/examples", b"job-103")]:
            status, data, csp = self.request("GET", path)
            self.assertEqual(status, 200, path)
            self.assertIn(marker, data)
            self.assertIn("default-src 'self'", csp)

    def test_no_arbitrary_files(self):
        for path in ["/ghostqueue/core.py", "/static/../train.py", "/api/private"]:
            status, _, _ = self.request("GET", path)
            self.assertEqual(status, 404)

    def test_real_triage_function_is_called(self):
        sample = {"id": "test", "message": "payment approval", "external_side_effect": True}
        expected = {"suggested_state": "review", "executed_actions": 0, "model": {"label": "complete", "confidence": .7}}
        with patch("web_demo.triage", return_value=expected) as called:
            status, data, _ = self.request("POST", "/api/analyze", json.dumps(sample), {"Content-Type":"application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data), expected)
        called.assert_called_once_with(sample)

    def test_invalid_requests_rejected(self):
        for body in [b"", b"not-json", b'{"message":""}', b'{"message":"x","trusted":"yes"}', b"x"*12001]:
            status, _, _ = self.request("POST", "/api/analyze", body, {"Content-Type":"application/json"})
            self.assertEqual(status, 400)

    def test_unknown_endpoint(self):
        status, _, _ = self.request("POST", "/api/execute", b"{}")
        self.assertEqual(status, 404)

if __name__ == "__main__":
    unittest.main()
