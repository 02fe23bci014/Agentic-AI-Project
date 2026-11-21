"""
AgenticPro - Student Submissions & Score Viewer
Run this script to inspect live student submissions and evaluations stored in the SQLite database.
Usage:
    python show_student_data.py
"""
import sqlite3
import json
from pathlib import Path

# Locate database
db_candidates = [
    Path("database/evaluations.db"),
    Path("backend/database/evaluations.db"),
    Path("Course Project Source Code/AgenticPro/database/evaluations.db"),
    Path("../database/evaluations.db"),
]

db_path = None
for p in db_candidates:
    if p.exists():
        db_path = p
        break

if not db_path:
    print("Database file evaluations.db not found in standard paths.")
    exit(1)

print("=" * 80)
print(f"  AGENTICPRO DATABASE VIEWER - {db_path}")
print("=" * 80)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Inspect Submissions Table
print("\n" + "—" * 80)
print("1. TABLE: submissions (Where student code is stored)")
print("—" * 80)
submissions = cur.execute("SELECT id, exam_id, question_id, student_id, language, source_code, submitted_at FROM submissions ORDER BY submitted_at DESC LIMIT 5").fetchall()

if not submissions:
    print("No submissions recorded yet. (Submit a solution in the UI to see live rows)")
else:
    for sub in submissions:
        print(f"\n[Submission ID: {sub['id']}]")
        print(f"  • Student ID:   {sub['student_id']}")
        print(f"  • Exam ID:      {sub['exam_id']}")
        print(f"  • Question ID:  {sub['question_id']}")
        print(f"  • Language:     {sub['language']}")
        print(f"  • Submitted At: {sub['submitted_at']}")
        print(f"  • Source Code:\n      " + "\n      ".join(sub['source_code'].strip().split("\n")[:4]))

# 2. Inspect Evaluations Table
print("\n" + "—" * 80)
print("2. TABLE: evaluations (Where multi-agent scores and insights are stored)")
print("—" * 80)
evaluations = cur.execute("SELECT submission_id, passed, total, score, status, feedback, agent_insights FROM evaluations LIMIT 5").fetchall()

if not evaluations:
    print("No evaluations recorded yet.")
else:
    for ev in evaluations:
        print(f"\n[Evaluation for: {ev['submission_id']}]")
        print(f"  • Test Cases: {ev['passed']} / {ev['total']} Passed")
        print(f"  • Score:      {ev['score']} pts")
        print(f"  • Status:     {ev['status']}")
        print(f"  • Feedback:   {ev['feedback']}")
        if ev['agent_insights']:
            try:
                insights = json.loads(ev['agent_insights'])
                print(f"  • Multi-Agent Insights: {list(insights.keys())}")
            except Exception:
                pass

# 3. Inspect Results Table
print("\n" + "—" * 80)
print("3. TABLE: results (Official Faculty Gradebook)")
print("—" * 80)
results = cur.execute("SELECT student_id, exam_id, score, max_score, published FROM results LIMIT 10").fetchall()

if not results:
    print("No published results yet.")
else:
    for res in results:
        status = "PUBLISHED" if res['published'] else "DRAFT"
        print(f"  • Student: {res['student_id']:<12} | Exam: {res['exam_id']:<15} | Score: {res['score']}/{res['max_score']} pts | Status: {status}")

print("\n" + "=" * 80)
conn.close()
