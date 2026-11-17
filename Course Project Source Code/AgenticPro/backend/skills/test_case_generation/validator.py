class TestCaseValidator:
    """
    Validates AI-generated test-case data.
    """

    def validate(self, data):
        if not isinstance(data, dict):
            return False

        if "test_cases" not in data:
            return False

        test_cases = data["test_cases"]

        if not isinstance(test_cases, list):
            return False

        if len(test_cases) == 0:
            return False

        for test_case in test_cases:
            if not isinstance(test_case, dict):
                return False

            if "input" not in test_case:
                return False

            if "expected_output" not in test_case:
                return False

            if test_case["input"] is None:
                return False

            if test_case["expected_output"] is None:
                return False

        return True