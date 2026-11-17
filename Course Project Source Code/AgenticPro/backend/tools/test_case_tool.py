from backend.models.test_case import TestCase

class TestCaseTool:
    """
    Tool responsible for creating and validating
    test cases for programming questions.
    """

    VALID_TYPES = {
        "public",
        "hidden",
        "edge",
        "boundary"
    }

    def create_test_case(
        self,
        input_data,
        expected_output,
        test_type="public"
    ):
        if test_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid test type: {test_type}"
            )

        test_case = {
            "input": input_data,
            "expected_output": expected_output,
            "type": test_type,
            "hidden": test_type != "public"
        }

        return test_case

    def validate_test_case(self, test_case):
        required_fields = [
            "input",
            "expected_output",
            "type",
            "hidden"
        ]

        for field in required_fields:
            if field not in test_case:
                return False

        if test_case["type"] not in self.VALID_TYPES:
            return False

        if test_case["input"] is None:
            return False

        if test_case["expected_output"] is None:
            return False

        return True




def get_test_cases(question_id: str) -> list[TestCase]:
    return [
        TestCase(
            id="demo-test-1",
            question_id=question_id,
            stdin="2 3",
            expected_stdout="5",
            points=1,
            is_hidden=False,
        ),
        TestCase(
            id="demo-test-2",
            question_id=question_id,
            stdin="10 20",
            expected_stdout="30",
            points=1,
            is_hidden=True,
        ),
    ]