import base64
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock automático dos pacotes GCP caso o ambiente local não os tenha instalados
for mod_name in [
    "functions_framework",
    "vertexai",
    "vertexai.generative_models",
    "google",
    "google.cloud",
    "google.cloud.firestore",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

sys.modules["functions_framework"].cloud_event = lambda f: f

# Adiciona a pasta src ao path para importação direta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import main  # noqa: E402


class TestTriageAgentExameEspecial(unittest.TestCase):
    def _make_cloud_event(self, payload_dict: dict):
        encoded = base64.b64encode(json.dumps(payload_dict).encode("utf-8")).decode("utf-8")
        event = MagicMock()
        event.data = {"message": {"data": encoded}}
        return event

    def test_local_get_build_logs_known_builds(self):
        self.assertIn("timeout", main.local_get_build_logs("build-101").lower())
        self.assertIn("syntaxerror", main.local_get_build_logs("build-202").lower())

    # ========================================================================
    # TODO (Etapa 3 - 15 pts): Escreva os testes unitários abaixo:
    # 1. `test_local_get_build_logs_critical_build_303`:
    #    Valide que `main.local_get_build_logs("build-303")` retorna um erro CRITICAL.
    # 2. `test_local_notify_oncall_team`:
    #    Valide que `main.local_notify_oncall_team("build-303", "CRITICAL", "DB error")`
    #    retorna uma mensagem de confirmação contendo o `build-303`.
    # 3. `test_idempotency_skips_already_triaged_build`:
    #    Use `@patch("main.get_db")` e `@patch("main.GenerativeModel")` para simular
    #    um documento no Firestore onde `doc_snapshot.exists = True` e
    #    `doc_snapshot.to_dict.return_value = {"status": "TRIAGED"}`.
    #    Chame `main.triage_agent_event_driven(event)` e verifique que
    #    `GenerativeModel` NÃO foi chamado (`mock_model.assert_not_called()`).
    # ========================================================================


if __name__ == "__main__":
    unittest.main()
