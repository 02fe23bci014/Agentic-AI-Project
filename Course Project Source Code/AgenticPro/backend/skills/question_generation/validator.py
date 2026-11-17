class QuestionValidator:
    """
    Validates AI-generated programming questions.
    """

    REQUIRED_FIELDS = {
        "title",
        "description",
        "input_format",
        "output_format",
        "constraints",
        "difficulty",
        "topic",
        "examples",
        "tags"
    }

    def validate(self, question):
        if not isinstance(question, dict):
            return False

        missing_fields = self.REQUIRED_FIELDS - question.keys()

        if missing_fields:
            return False

        for field in self.REQUIRED_FIELDS:
            if question[field] is None:
                return False

        if not isinstance(question["examples"], list):
            return False

        if not isinstance(question["tags"], list):
            return False

        return True