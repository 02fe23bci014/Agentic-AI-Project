from backend.tools.question_tool import QuestionTool
from backend.skills.question_generation.skill import QuestionGenerationSkill


class QuestionGenerationAgent:
    """
    Agent responsible for generating programming questions
    using Ollama Cloud and validating them through QuestionTool.
    """

    def __init__(self):
        self.question_tool = QuestionTool()
        self.question_skill = QuestionGenerationSkill()

    def generate_question(
        self,
        topic,
        difficulty,
        language,
        marks,
    ):
        # Generate the question using the LLM skill.
        generated_question = self.question_skill.generate(
            topic=topic,
            difficulty=difficulty,
            language=language,
            marks=marks,
        )

        # Pass the generated data through the project's
        # QuestionTool for final question creation/validation.
        question = self.question_tool.create_question(
            title=generated_question["title"],
            description=generated_question["description"],
            input_format=generated_question["input_format"],
            output_format=generated_question["output_format"],
            constraints=generated_question["constraints"],
            difficulty=generated_question["difficulty"],
            language=language,
            marks=marks,
            topic=generated_question["topic"],
            examples=generated_question["examples"],
            tags=generated_question["tags"],
        )

        if not self.question_tool.validate_question(question):
            raise ValueError("Generated question is invalid.")

        return question