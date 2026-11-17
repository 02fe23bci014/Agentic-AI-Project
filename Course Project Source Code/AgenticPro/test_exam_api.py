from fastapi import HTTPException

from backend.api.exam_routes import get_exam


try:
    result = get_exam("nonexistent-exam")
    print("Unexpected result:", result)

except HTTPException as error:
    print("HTTP status:", error.status_code)
    print("Detail:", error.detail)