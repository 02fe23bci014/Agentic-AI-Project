class QuestionTool:
    """
    Tool responsible for creating and validating programming questions.
    """

    def create_question(
        self,
        title,
        description,
        input_format,
        output_format,
        constraints,
        difficulty,
        language,
        marks,
        topic,
        examples=None,
        tags=None
    ):
        question = {
            "question_id": None,
            "title": title,
            "description": description,
            "input_format": input_format,
            "output_format": output_format,
            "constraints": constraints,
            "difficulty": difficulty,
            "language": language,
            "marks": marks,
            "topic": topic,
            "examples": examples or [],
            "tags": tags or []
        }

        return question

    def validate_question(self, question):
        required_fields = [
            "title",
            "description",
            "input_format",
            "output_format",
            "constraints",
            "difficulty",
            "language",
            "marks",
            "topic"
        ]

        for field in required_fields:
            if field not in question:
                return False

            if question[field] is None:
                return False

            if isinstance(question[field], str) and not question[field].strip():
                return False

        if not isinstance(question["marks"], (int, float)):
            return False

        if question["marks"] <= 0:
            return False

        return True