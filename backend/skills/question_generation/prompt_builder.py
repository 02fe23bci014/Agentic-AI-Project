class QuestionPromptBuilder:
    """
    Builds structured prompts for programming question generation.
    """

    def build(
        self,
        topic: str,
        difficulty: str,
        language: str,
        marks: int,
    ) -> str:
        return f"""
You are an expert programming-lab question setter.

Generate one programming problem using these requirements:

Topic: {topic}
Difficulty: {difficulty}
Programming Language: {language}
Marks: {marks}

The problem must be suitable for a CS programming laboratory examination.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "title": "string",
    "description": "string",
    "input_format": "string",
    "output_format": "string",
    "constraints": "string",
    "difficulty": "{difficulty}",
    "topic": "{topic}",
    "examples": [
        {{
            "input": "string",
            "output": "string"
        }}
    ],
    "tags": ["string"]
}}

Requirements:
- The description must clearly explain the programming task.
- Input and output formats must be unambiguous.
- Include realistic constraints.
- Include at least one example.
- The problem must be solvable using {language}.
- Do not include explanations outside the JSON.
"""