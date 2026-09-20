import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from analyst.web import app


class AskTests(unittest.TestCase):
    def test_missing_key_returns_actionable_error_without_running_graph(self):
        for key in (None, "", "   "):
            with self.subTest(key=key), patch.dict(os.environ), patch(
                "analyst.web.graph.invoke"
            ) as invoke:
                if key is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = key
                response = TestClient(app).post("/ask", json={"question": "Apple revenue?"})
                self.assertEqual(response.status_code, 503)
                self.assertIn("OpenAI API key is missing", response.json()["detail"])
                self.assertIn("restart the server", response.json()["detail"])
                invoke.assert_not_called()

    def test_configured_key_runs_graph(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), patch(
            "analyst.web.graph.invoke", return_value={"final_message": "Answer"}
        ) as invoke:
            response = TestClient(app).post("/ask", json={"question": "Apple revenue?"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"final_message": "Answer"})
            invoke.assert_called_once()
