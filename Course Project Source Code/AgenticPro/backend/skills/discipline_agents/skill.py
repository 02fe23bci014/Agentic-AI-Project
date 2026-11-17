import json
import socket
import urllib.parse
from typing import Any
from backend.config.settings import settings
from backend.skills.discipline_agents.prompt_builder import DisciplinePromptBuilder
from backend.skills.discipline_agents.synthesizer import DisciplineSynthesizer
from backend.skills.discipline_agents.validator import DisciplineValidator


def is_service_reachable(url: str, timeout: float = 0.5) -> bool:
    """Fast probe to determine whether remote LLM endpoint is reachable without hanging."""
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False


class DisciplineSpecificSkill:
    """Skill for discipline-specific engineering worklets (ME, CE, EE)."""

    def __init__(self):
        self.builder = DisciplinePromptBuilder()
        self.validator = DisciplineValidator()
        self.synthesizer = DisciplineSynthesizer()

    def generate(
        self,
        discipline: str,
        worklet_type: str,
        title: str = "",
        parameters: dict[str, float] | None = None,
        problem_statement: str = "",
        unit_system: str = "SI",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate solved engineering worklet with derivations, KPIs, and code."""
        # Fast reachability check for Ollama / LLM
        reachable = is_service_reachable(settings.ollama_base_url, timeout=0.5)

        if reachable:
            try:
                import requests
                prompt = self.builder.build_prompt(
                    discipline=discipline,
                    worklet_type=worklet_type,
                    title=title,
                    parameters=parameters or {},
                    problem_statement=problem_statement,
                    unit_system=unit_system,
                )
                response = requests.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                    timeout=8.0,
                )
                if response.status_code == 200:
                    raw_text = response.json().get("response", "{}")
                    parsed = json.loads(raw_text)
                    if self.validator.validate(parsed):
                        return parsed
            except Exception:
                pass

        # High-fidelity domain synthesizer fallback
        return self.synthesizer.synthesize(
            discipline=discipline,
            worklet_type=worklet_type,
            title=title,
            parameters=parameters,
            problem_statement=problem_statement,
            unit_system=unit_system,
            user_id=user_id,
        )
