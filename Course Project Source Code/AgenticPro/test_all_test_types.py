from backend.agents.test_case_agent import TestCaseAgent

agent = TestCaseAgent()

question = {
    "title": "Find Maximum",
    "description": "Find the maximum element in an array.",
    "input_format": "First line contains N. Second line contains N integers.",
    "output_format": "Print the maximum element.",
    "constraints": "1 <= N <= 1000",
    "difficulty": "Easy",
    "topic": "Arrays",
}

for test_type in ["public", "hidden", "edge", "boundary"]:
    test_cases = agent.generate_test_cases(
        question=question,
        test_type=test_type,
        number_of_cases=2,
    )

    print(f"\n===== {test_type.upper()} =====")

    for case in test_cases:
        print("Type:", case["type"])
        print("Hidden:", case["hidden"])