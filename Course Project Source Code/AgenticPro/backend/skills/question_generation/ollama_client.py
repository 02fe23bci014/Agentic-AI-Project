import json
import logging

from ollama import Client

from backend.config.settings import settings


logger = logging.getLogger(__name__)


class OllamaCloudClient:
    """
    Client for communicating with Ollama Cloud.
    """

    def __init__(self):
        api_key = settings.ollama_api_key

        if not api_key:
            raise ValueError(
                "OLLAMA_API_KEY is not configured."
            )

        self.client = Client(
            host=settings.ollama_base_url,
            headers={
                "Authorization": f"Bearer {api_key}"
            },
        )

    def generate(self, prompt):
        """
        Send a prompt to Ollama Cloud and return
        the generated response as a Python dictionary.
        """

        last_error = None

        for attempt in range(3):
            try:
                logger.info(
                    "Sending request to Ollama Cloud. "
                    "model=%s attempt=%d",
                    settings.ollama_model,
                    attempt + 1,
                )

                response = self.client.chat(
                    model=settings.ollama_model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    format="json",
                )

                content = response["message"]["content"]

                try:
                    return json.loads(content)

                except json.JSONDecodeError as exc:
                    logger.error(
                        "Ollama returned invalid JSON: %s",
                        content,
                    )

                    raise ValueError(
                        "Ollama returned invalid JSON."
                    ) from exc

            except Exception as exc:
                last_error = exc

                logger.warning(
                    "Ollama Cloud request failed. "
                    "attempt=%d error=%s",
                    attempt + 1,
                    exc,
                )

                if attempt == 2:
                    raise RuntimeError(
                        "Ollama Cloud request failed after 3 attempts."
                    ) from last_error

        # This should never be reached.
        raise RuntimeError(
            "Ollama Cloud request failed."
        )