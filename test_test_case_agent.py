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

test_cases = agent.generate_test_cases(
    question=question,
    test_type="hidden",
    number_of_cases=3,
)

print("===== GENERATED TEST CASES =====")

for index, test_case in enumerate(test_cases, start=1):
    print(f"\nTest Case {index}")
    print(f"Input: {test_case['input']}")
    print(f"Expected Output: {test_case['expected_output']}")
    print(f"Type: {test_case['type']}")
    print(f"Hidden: {test_case['hidden']}")