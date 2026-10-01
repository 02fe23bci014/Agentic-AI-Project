from backend.agents.question_generation_agent import QuestionGenerationAgent


agent = QuestionGenerationAgent()

question = agent.generate_question(
    topic="Arrays",
    difficulty="Easy",
    language="C++",
    marks=10,
)

print("\n===== GENERATED QUESTION =====\n")

for key, value in question.items():
    print(f"{key}: {value}")