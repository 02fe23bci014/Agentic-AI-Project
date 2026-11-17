from backend.agents.question_generation_agent import QuestionGenerationAgent

agent = QuestionGenerationAgent()

question = agent.generate_question(
    title="Find Maximum Element",
    description="Given an array of integers, find the maximum element.",
    input_format="First line contains N. Second line contains N integers.",
    output_format="Print the maximum element.",
    constraints="1 <= N <= 1000",
    difficulty="Easy",
    language="C++",
    marks=10,
    topic="Arrays",
    examples=[
        {
            "input": "5\n10 20 30 40 50",
            "output": "50"
        }
    ],
    tags=["array", "maximum", "iteration"]
)

print(question)