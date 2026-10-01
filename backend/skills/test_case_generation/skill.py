from backend.skills.question_generation.ollama_client import OllamaCloudClient
from backend.skills.test_case_generation.prompt_builder import TestCasePromptBuilder
from backend.skills.test_case_generation.validator import TestCaseValidator


class TestCaseGenerationSkill:
    """
    Skill for generating and validating programming test cases
    using Ollama Cloud.
    """

    def __init__(self):
        self.llm_client = OllamaCloudClient()
        self.prompt_builder = TestCasePromptBuilder()
        self.validator = TestCaseValidator()

    def generate(
        self,
        question: dict,
        test_type: str,
        number_of_cases: int = 3,
    ):
        prompt = self.prompt_builder.build(
            question=question,
            test_type=test_type,
            number_of_cases=number_of_cases,
        )

        data = self.llm_client.generate(prompt)

        if not self.validator.validate(data):
            raise ValueError(
                "Generated test cases failed validation."
            )

        return data["test_cases"]