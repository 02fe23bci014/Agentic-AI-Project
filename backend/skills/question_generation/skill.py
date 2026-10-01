from backend.skills.question_generation.ollama_client import OllamaCloudClient
from backend.skills.question_generation.prompt_builder import QuestionPromptBuilder
from backend.skills.question_generation.validator import QuestionValidator


class QuestionGenerationSkill:
    """
    Skill for generating and validating programming questions
    using Ollama Cloud.
    """

    def __init__(self):
        self.llm_client = OllamaCloudClient()
        self.prompt_builder = QuestionPromptBuilder()
        self.validator = QuestionValidator()

    def generate(
        self,
        topic: str,
        difficulty: str,
        language: str,
        marks: int,
    ):
        prompt = self.prompt_builder.build(
            topic=topic,
            difficulty=difficulty,
            language=language,
            marks=marks,
        )

        question = self.llm_client.generate(prompt)

        if not self.validator.validate(question):
            raise ValueError(
                "Generated question failed validation."
            )

        return question