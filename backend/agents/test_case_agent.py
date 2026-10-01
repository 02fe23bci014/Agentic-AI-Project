from backend.tools.test_case_tool import TestCaseTool
from backend.skills.test_case_generation.skill import TestCaseGenerationSkill


class TestCaseAgent:
    """
    Agent responsible for generating and validating
    test cases for programming questions.
    """

    def __init__(self):
        self.test_case_tool = TestCaseTool()
        self.test_case_skill = TestCaseGenerationSkill()

    def generate_test_cases(
        self,
        question,
        test_type="public",
        number_of_cases=3,
    ):
        generated_cases = self.test_case_skill.generate(
            question=question,
            test_type=test_type,
            number_of_cases=number_of_cases,
        )

        validated_cases = []

        for generated_case in generated_cases:
            test_case = self.test_case_tool.create_test_case(
                input_data=generated_case["input"],
                expected_output=generated_case["expected_output"],
                test_type=test_type,
            )

            if not self.test_case_tool.validate_test_case(test_case):
                raise ValueError(
                    "Generated test case is invalid."
                )

            validated_cases.append(test_case)

        return validated_cases