class QuestionGenerationRequest:
    """
    Represents the input required to generate a programming question.
    """

    def __init__(
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
        self.title = title
        self.description = description
        self.input_format = input_format
        self.output_format = output_format
        self.constraints = constraints
        self.difficulty = difficulty
        self.language = language
        self.marks = marks
        self.topic = topic
        self.examples = examples or []
        self.tags = tags or []

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "constraints": self.constraints,
            "difficulty": self.difficulty,
            "language": self.language,
            "marks": self.marks,
            "topic": self.topic,
            "examples": self.examples,
            "tags": self.tags
        }