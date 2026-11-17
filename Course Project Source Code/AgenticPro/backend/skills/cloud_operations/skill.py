import logging
import socket
import urllib.parse
from typing import Any

from backend.config.settings import settings
from backend.skills.cloud_operations.prompt_builder import CloudOpsPromptBuilder
from backend.skills.cloud_operations.synthesizer import CloudOpsSynthesizer
from backend.skills.cloud_operations.validator import CloudOpsValidator

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


class CloudOperationsSkill:
    """
    Skill for autonomous diagnosis and remediation synthesis for failed cloud deployments.
    """

    def __init__(self):
        self.prompt_builder = CloudOpsPromptBuilder()
        self.validator = CloudOpsValidator()
        self.synthesizer = CloudOpsSynthesizer()

    def generate(
        self,
        service_name: str,
        environment: str = "production",
        deployment_target: str = "kubernetes",
        raw_logs: str = "",
        deployment_config: str | None = None,
        incident_type: str | None = None,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """Diagnose failed deployment logs and return RCA, steps, and patch artifacts."""
        clean_name = service_name.strip()
        if not clean_name:
            raise ValueError("Service name cannot be empty.")

        if not raw_logs or not raw_logs.strip():
            raise ValueError("Deployment crash logs cannot be empty.")

        # Attempt LLM generation if reachable and configured
        if use_llm and getattr(settings, "ollama_api_key", None):
            base_url = getattr(settings, "ollama_base_url", "https://ollama.com")
            if is_service_reachable(base_url, timeout=0.5):
                try:
                    from backend.skills.question_generation.ollama_client import OllamaCloudClient

                    client = OllamaCloudClient()
                    prompt = self.prompt_builder.build(
                        service_name=clean_name,
                        environment=environment,
                        deployment_target=deployment_target,
                        raw_logs=raw_logs,
                        deployment_config=deployment_config,
                        incident_type=incident_type,
                    )
                    data = client.generate(prompt)
                    if self.validator.validate(data):
                        logger.info("Successfully diagnosed cloud deployment failure via LLM.")
                        return data
                except Exception as exc:
                    logger.warning("LLM diagnostic attempt failed (%s), using synthesizer.", exc)
            else:
                logger.info("Ollama host (%s) unreachable; using CloudOps synthesizer.", base_url)

        # High-fidelity domain synthesizer fallback
        data = self.synthesizer.synthesize(
            service_name=clean_name,
            environment=environment,
            deployment_target=deployment_target,
            raw_logs=raw_logs,
            deployment_config=deployment_config,
            incident_type=incident_type,
        )

        if not self.validator.validate(data):
            raise ValueError("Synthesized diagnosis data failed validation.")

        return data
