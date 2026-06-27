import os
import sys
import argparse
from config import get_client
from utils import read_resume
from agents.reading_agent import run_reading_agent
from agents.search_agent import run_search_agent
from agents.comparing_agent import run_comparing_agent
from agents.suggesting_agent import run_suggesting_agent

def main():
    parser = argparse.ArgumentParser(description="Internship Assistant Multi-Agent System")
    parser.add_argument(
        "--resume", 
        type=str, 
        help="Path to the resume file (.pdf, .txt, or .md)",
        default="sample_resume.txt"
    )
    args = parser.parse_args()

    # 1. Initialize Gemini client
    client = get_client()

    # 2. Read resume file
    resume_path = args.resume
    if not os.path.exists(resume_path):
        if resume_path == "sample_resume.txt":
            print(f"[Orchestrator] Sample resume '{resume_path}' not found. Creating a default sample resume...")
            create_default_sample_resume()
        else:
            print(f"[Error] Resume file not found at: {resume_path}", file=sys.stderr)
            sys.exit(1)

    print(f"[Orchestrator] Reading resume from '{resume_path}'...")
    try:
        resume_text = read_resume(resume_path)
    except Exception as e:
        print(f"[Error] Failed to read resume: {e}", file=sys.stderr)
        sys.exit(1)

    if not resume_text.strip():
        print("[Error] Resume content is empty. Please provide a valid resume.", file=sys.stderr)
        sys.exit(1)

    # 3. Agent 1: Reading Agent
    print("\n=== Running Reading Agent ===")
    try:
        resume_data = run_reading_agent(client, resume_text)
        print(f"Extracted Education:")
        for edu in resume_data.education:
            print(f"  - {edu.degree} in {edu.major} from {edu.school} ({edu.year})")
        print(f"Extracted Skills: {', '.join(resume_data.skills)}")
    except Exception as e:
        print(f"[Error] Reading Agent failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Agent 2: Search Engine Agent
    print("\n=== Running Search Engine Agent ===")
    try:
        raw_internships = run_search_agent(client, resume_data.skills)
        if not raw_internships:
            print("[Error] No internships found or parsed. Exiting.", file=sys.stderr)
            sys.exit(1)
        print(f"Found and parsed {len(raw_internships)} internships.")
    except Exception as e:
        print(f"[Error] Search Engine Agent failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Agent 3: Comparing Agent
    print("\n=== Running Comparing Agent ===")
    try:
        top_internships = run_comparing_agent(client, resume_data.skills, raw_internships)
    except Exception as e:
        print(f"[Error] Comparing Agent failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 6. Agent 4: Suggesting Agent
    print("\n=== Running Suggesting Agent ===")
    try:
        suggestions = run_suggesting_agent(client, resume_data.skills, top_internships)
    except Exception as e:
        print(f"[Error] Suggesting Agent failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. Format and Print the exact output requested by the user
    print("\n" + "="*50)
    print("               FINAL OUTPUT RESULTS")
    print("="*50 + "\n")

    for i, job in enumerate(top_internships):
        print(f"Internship {i+1}: {job['company']}")
        print(f"Role: {job['role']}")
        print(f"Match%: {job['match_percentage']}%")
        print(f"Apply Link: {job['apply_link']}")
        missing_skills_str = ", ".join(job['missing_skills']) if job['missing_skills'] else "None"
        print(f"Missing Skills: {missing_skills_str}")
        print()  # Empty line between internships

    print("Suggestions for Change in Resume:")
    if suggestions.resume_changes:
        for change in suggestions.resume_changes:
            print(f"- Section: {change.section}")
            print(f"  Rationale: {change.rationale}")
            print(f"  Actionable Change: {change.actionable_change}")
            print()
    else:
        print("Your resume is highly optimized for these roles! No significant changes suggested.")

    # Also print skill acquisition recommendations
    if suggestions.recommended_skills:
        print("Recommended Skill Enhancements:")
        for rec in suggestions.recommended_skills:
            print(f"- Skill: {rec.skill}")
            print(f"  Importance: {rec.importance}")
            print(f"  How to Acquire: {rec.how_to_acquire}")
            print()

def create_default_sample_resume():
    """
    Creates a high-quality sample resume text file if not present.
    """
    sample_text = """John Doe
Email: john.doe@example.com | Phone: (123) 456-7890 | Web: github.com/johndoe

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
Graduation: May 2025

TECHNICAL SKILLS
- Programming Languages: Python, Java, C++
- Web Development: HTML, CSS, JavaScript
- Databases: PostgreSQL, SQLite
- Developer Tools: Git, VS Code, Docker
- Core Concepts: Object-Oriented Programming, Data Structures, Algorithms

PROJECTS
Personal Portfolio Website
- Built a responsive portfolio site using HTML, CSS, and vanilla JavaScript.
- Deployed the project on GitHub Pages, attracting over 500 unique visitors.

Database-driven Task Manager
- Designed a CLI task management application in Python using SQLite.
- Implemented core CRUD functionality to organize tasks, assign priorities, and track deadlines.
"""
    with open("sample_resume.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    print("[Orchestrator] Created 'sample_resume.txt' successfully.")

if __name__ == "__main__":
    main()
