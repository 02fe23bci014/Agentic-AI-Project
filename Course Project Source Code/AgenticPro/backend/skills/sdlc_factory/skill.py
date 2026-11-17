import logging
import socket
import urllib.parse
from typing import Any

from backend.config.settings import settings
from backend.skills.sdlc_factory.prompt_builder import SDLCFactoryPromptBuilder
from backend.skills.sdlc_factory.synthesizer import SDLCFactorySynthesizer
from backend.skills.sdlc_factory.validator import SDLCFactoryValidator

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


class SDLCFactorySkill:
    """
    Skill for autonomous end-to-end SDLC generation: Requirement -> Tested Implementation.
    """

    def __init__(self):
        self.prompt_builder = SDLCFactoryPromptBuilder()
        self.validator = SDLCFactoryValidator()
        self.synthesizer = SDLCFactorySynthesizer()

    def generate(
        self,
        project_name: str,
        requirement_text: str,
        target_language: str = "python",
        framework: str = "fastapi",
        architecture_style: str = "clean_architecture",
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """Synthesize user stories, architecture, source files, and unit tests."""
        clean_name = project_name.strip()
        if not clean_name:
            raise ValueError("Project name cannot be empty.")

        if not requirement_text or not requirement_text.strip():
            raise ValueError("Requirement text cannot be empty.")

        # Attempt LLM generation if reachable and configured
        if use_llm and getattr(settings, "ollama_api_key", None):
            base_url = getattr(settings, "ollama_base_url", "https://ollama.com")
            if is_service_reachable(base_url, timeout=0.5):
                try:
                    from backend.skills.question_generation.ollama_client import OllamaCloudClient

                    client = OllamaCloudClient()
                    prompt = self.prompt_builder.build(
                        project_name=clean_name,
                        requirement_text=requirement_text.strip(),
                        target_language=target_language,
                        framework=framework,
                        architecture_style=architecture_style,
                    )
                    data = client.generate(prompt)
                    if self.validator.validate(data):
                        logger.info("Successfully generated SDLC project via LLM.")
                        return data
                except Exception as exc:
                    logger.warning("LLM SDLC factory attempt failed (%s), using domain synthesizer.", exc)
            else:
                logger.info("Ollama host (%s) unreachable; using SDLC factory synthesizer fallback.", base_url)

        # High-fidelity domain synthesizer fallback
        data = self.synthesizer.synthesize(
            project_name=clean_name,
            requirement_text=requirement_text.strip(),
            target_language=target_language,
            framework=framework,
            architecture_style=architecture_style,
        )

        if not self.validator.validate(data):
            raise ValueError("Synthesized SDLC data failed validation.")

        return data
