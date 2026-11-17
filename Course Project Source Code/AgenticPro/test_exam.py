from backend.agents.exam_agent import ExamAgent

agent = ExamAgent()

question_data = {
    "title": "Find Maximum Element",
    "description": "Given an array of integers, find the maximum element.",
    "input_format": "First line contains N. Second line contains N integers.",
    "output_format": "Print the maximum element.",
    "constraints": "1 <= N <= 1000",
    "difficulty": "Easy",
    "language": "C++",
    "marks": 10,
    "topic": "Arrays",
    "examples": [
        {
            "input": "5\n10 20 30 40 50",
            "output": "50"
        }
    ],
    "tags": ["array", "maximum", "iteration"]
}

test_cases = [
    {
        "input": "5\n10 20 30 40 50",
        "expected_output": "50",
        "test_type": "public"
    },
    {
        "input": "4\n-5 -2 -10 -1",
        "expected_output": "-1",
        "test_type": "hidden"
    },
    {
        "input": "1\n100",
        "expected_output": "100",
        "test_type": "edge"
    }
]

exam = agent.create_exam(question_data, test_cases)

print(exam)