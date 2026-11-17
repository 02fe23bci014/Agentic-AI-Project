from backend.skills.test_case_generation.validator import TestCaseValidator

validator = TestCaseValidator()

valid_data = {
    "test_cases": [
        {
            "input": "5\n1 2 3 4 5",
            "expected_output": "5"
        }
    ]
}

print(validator.validate(valid_data))