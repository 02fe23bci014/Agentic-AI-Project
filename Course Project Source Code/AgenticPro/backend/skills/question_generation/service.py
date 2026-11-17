from backend.skills.question_generation.request import QuestionGenerationRequest
from backend.skills.question_generation.prompt_builder import QuestionPromptBuilder
from backend.skills.question_generation.skill import QuestionGenerationSkill


class QuestionGenerationService:
    """
    Coordinates the question-generation components.
    """

    def __init__(self):
        self.prompt_builder = QuestionPromptBuilder()
        self.skill = QuestionGenerationSkill()

    def generate(self, request):
        if not isinstance(request, QuestionGenerationRequest):
            raise TypeError(
                "request must be a QuestionGenerationRequest"
            )

        prompt = self.prompt_builder.build(request)

        question = self.skill.generate(request)

        return {
            "prompt": prompt,
            "question": question
        }