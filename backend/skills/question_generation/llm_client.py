from openai import OpenAI

from backend.config.settings import settings


class LLMClient:
    """
    Wrapper around the OpenAI client.
    """

    def __init__(self):
        if not settings.llm_api_key:
            raise ValueError(
                "LLM_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.llm_api_key
        )

    def generate(self, prompt):
        response = self.client.responses.create(
            model=settings.llm_model,
            input=prompt
        )

        return response.output_text