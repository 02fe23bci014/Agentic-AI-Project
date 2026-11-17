import logging
import socket
import urllib.parse
from typing import Any

from backend.config.settings import settings
from backend.skills.safety_governance.prompt_builder import SafetyGovernancePromptBuilder
from backend.skills.safety_governance.synthesizer import SafetyGovernanceSynthesizer
from backend.skills.safety_governance.validator import SafetyGovernanceValidator

logger = logging.getLogger(__name__)


def is_service_reachable(base_url: str, timeout: float = 0.5) -> bool:
    """Fast pre-flight network reachability probe."""
    try:
        parsed = urllib.parse.urlparse(base_url)
        host = parsed.hostname or base_url
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


class SafetyGovernanceSkill:
    """
    Skill for autonomous risk assessment, policy evaluation, and rollback synthesis.
    """

    def __init__(self):
        self.prompt_builder = SafetyGovernancePromptBuilder()
        self.validator = SafetyGovernanceValidator()
        self.synthesizer = SafetyGovernanceSynthesizer()

    def generate(
        self,
        action_title: str,
        target_system: str = "production",
        proposed_payload: str = "",
        initiator: str = "agent",
        declared_purpose: str = "",
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """Assess safety, compute risk score, and generate rollback plan."""
        clean_title = action_title.strip()
        if not clean_title:
            raise ValueError("Action title cannot be empty.")

        if not proposed_payload or not proposed_payload.strip():
            raise ValueError("Proposed payload/code cannot be empty.")

        # Attempt LLM generation if reachable and configured
        if use_llm and getattr(settings, "ollama_api_key", None):
            base_url = getattr(settings, "ollama_base_url", "https://ollama.com")
            if is_service_reachable(base_url, timeout=0.5):
                try:
                    from backend.skills.question_generation.ollama_client import OllamaCloudClient

                    client = OllamaCloudClient()
                    prompt = self.prompt_builder.build(
                        action_title=clean_title,
                        target_system=target_system,
                        proposed_payload=proposed_payload.strip(),
                        initiator=initiator,
                        declared_purpose=declared_purpose,
                    )
                    data = client.generate(prompt)
                    if self.validator.validate(data):
                        logger.info("Successfully assessed safety and governance via LLM.")
                        return data
                except Exception as exc:
                    logger.warning("LLM governance evaluation failed (%s), using domain synthesizer.", exc)
            else:
                logger.info("Ollama host (%s) unreachable; using SafetyGovernance synthesizer fallback.", base_url)

        # High-fidelity domain synthesizer fallback
        data = self.synthesizer.synthesize(
            action_title=clean_title,
            target_system=target_system,
            proposed_payload=proposed_payload.strip(),
            initiator=initiator,
            declared_purpose=declared_purpose,
        )

        if not self.validator.validate(data):
            raise ValueError("Synthesized governance assessment failed validation.")

        return data
