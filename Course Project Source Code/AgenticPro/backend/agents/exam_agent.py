from backend.agents.question_generation_agent import QuestionGenerationAgent
from backend.agents.test_case_agent import TestCaseAgent


class ExamAgent:
    """
    Agent responsible for creating a programming lab exam
    containing questions and their test cases.
    """

    def __init__(self):
        self.question_agent = QuestionGenerationAgent()
        self.test_case_agent = TestCaseAgent()

    def create_exam(self, question_data, test_cases):
        question = self.question_agent.generate_question(
            title=question_data["title"],
            description=question_data["description"],
            input_format=question_data["input_format"],
            output_format=question_data["output_format"],
            constraints=question_data["constraints"],
            difficulty=question_data["difficulty"],
            language=question_data["language"],
            marks=question_data["marks"],
            topic=question_data["topic"],
            examples=question_data.get("examples", []),
            tags=question_data.get("tags", [])
        )

        validated_test_cases = []

        for test_case in test_cases:
            validated_test_case = self.test_case_agent.create_test_case(
                input_data=test_case["input"],
                expected_output=test_case["expected_output"],
                test_type=test_case.get("test_type", "public")
            )

            validated_test_cases.append(validated_test_case)

        exam = {
            "question": question,
            "test_cases": validated_test_cases
        }

        return exam