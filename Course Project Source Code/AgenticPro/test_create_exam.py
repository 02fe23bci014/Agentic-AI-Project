from fastapi import HTTPException
from backend.api.exam_routes import ExamCreateRequest, create_exam, get_exam


exam_id = "exam-test-001"

request = ExamCreateRequest(
    id=exam_id,
    title="Python Programming Lab Test",
    duration_minutes=60,
    question_ids=[],
)

try:
    result = create_exam(request)
    print("Exam created successfully!")
    print(result.model_dump())

except HTTPException as error:
    if error.status_code == 409:
        print("Exam already exists. Retrieving the existing exam...")
    else:
        raise

print("\nVerifying saved exam...")

saved_exam = get_exam(exam_id)
print(saved_exam.model_dump())

print("\nExam creation and retrieval test completed.")