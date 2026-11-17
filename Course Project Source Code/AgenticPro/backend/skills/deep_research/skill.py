import logging
import socket
import urllib.parse
from typing import Any

from backend.config.settings import settings
from backend.skills.deep_research.prompt_builder import ResearchPromptBuilder
from backend.skills.deep_research.synthesizer import ResearchSynthesizer
from backend.skills.deep_research.validator import ResearchValidator

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


class DeepResearchSkill:
    """
    Skill for autonomous technical inquiry, evidence gathering, and topic briefing.
    Orchestrates prompt engineering, LLM inference, and validation with fallback.
    """

    def __init__(self):
        self.prompt_builder = ResearchPromptBuilder()
        self.validator = ResearchValidator()
        self.synthesizer = ResearchSynthesizer()

    def generate(
        self,
        topic: str,
        depth: str = "deep",
        focus_areas: list[str] | None = None,
        max_sources: int = 5,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """Generate a complete research briefing and evidence table."""
        clean_topic = topic.strip()
        if not clean_topic:
            raise ValueError("Research topic cannot be empty.")

        # Attempt LLM generation if configured, reachable, and enabled
        if use_llm and getattr(settings, "ollama_api_key", None):
            base_url = getattr(settings, "ollama_base_url", "https://ollama.com")
            if is_service_reachable(base_url, timeout=0.5):
                try:
                    from backend.skills.question_generation.ollama_client import OllamaCloudClient

                    client = OllamaCloudClient()
                    prompt = self.prompt_builder.build(
                        topic=clean_topic,
                        depth=depth,
                        focus_areas=focus_areas,
                        max_sources=max_sources,
                    )
                    data = client.generate(prompt)
                    if self.validator.validate(data):
                        logger.info("Successfully generated research briefing via LLM.")
                        return data
                except Exception as exc:
                    logger.warning(
                        "LLM generation failed (%s), applying robust research synthesizer.",
                        exc,
                    )
            else:
                logger.info(
                    "Ollama host (%s) unreachable or offline; using research synthesizer fallback.",
                    base_url,
                )

        # Fallback to deterministic domain synthesizer
        data = self.synthesizer.synthesize(
            topic=clean_topic,
            depth=depth,
            focus_areas=focus_areas,
            max_sources=max_sources,
        )

        if not self.validator.validate(data):
            raise ValueError("Synthesized research data failed validation.")

        return data
