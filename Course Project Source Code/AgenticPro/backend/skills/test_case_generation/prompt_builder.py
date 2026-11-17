class TestCasePromptBuilder:
    """
    Builds prompts for generating programming test cases.
    """

    def build(
        self,
        question: dict,
        test_type: str,
        number_of_cases: int = 3,
    ) -> str:
        return f"""
You are an expert programming-lab test-case designer.

Generate test cases for the following programming problem.

Problem:
Title: {question["title"]}

Description:
{question["description"]}

Input Format:
{question["input_format"]}

Output Format:
{question["output_format"]}

Constraints:
{question["constraints"]}

Difficulty:
{question["difficulty"]}

Topic:
{question["topic"]}

Required test type:
{test_type}

Number of test cases:
{number_of_cases}

Return ONLY valid JSON using exactly this structure:

{{
    "test_cases": [
        {{
            "input": "string",
            "expected_output": "string"
        }}
    ]
}}

Requirements:
- Generate exactly {number_of_cases} test cases.
- Every input must follow the problem's input format.
- Every expected output must be correct.
- Respect all stated constraints.
- For edge tests, focus on unusual valid cases.
- For boundary tests, focus on minimum or maximum constraints.
- For public tests, use representative normal cases.
- For hidden tests, use cases that thoroughly test correctness.
- Do not include explanations outside the JSON.
"""