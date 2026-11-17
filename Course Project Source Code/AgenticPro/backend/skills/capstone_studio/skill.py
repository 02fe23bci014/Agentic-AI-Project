import json
import socket
import urllib.parse
from typing import Any
from backend.config.settings import settings
from backend.skills.capstone_studio.prompt_builder import CapstonePromptBuilder
from backend.skills.capstone_studio.synthesizer import CapstoneSynthesizer
from backend.skills.capstone_studio.validator import CapstoneValidator


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


class CapstoneStudioSkill:
    """Skill for autonomous team-owned Capstone Project Studio."""

    def __init__(self):
        self.builder = CapstonePromptBuilder()
        self.validator = CapstoneValidator()
        self.synthesizer = CapstoneSynthesizer()

    def generate(
        self,
        team_name: str,
        project_title: str,
        domain: str = "General Engineering",
        mission_statement: str = "",
        team_members: list[dict] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate comprehensive capstone project artifact across all 5 stages."""
        reachable = is_service_reachable(settings.ollama_base_url, timeout=0.5)

        if reachable:
            try:
                import requests
                prompt = self.builder.build_prompt(
                    team_name=team_name,
                    project_title=project_title,
                    domain=domain,
                    mission_statement=mission_statement,
                    team_members=team_members or [],
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
            team_name=team_name,
            project_title=project_title,
            domain=domain,
            mission_statement=mission_statement,
            team_members=team_members,
            user_id=user_id,
        )
