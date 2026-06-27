import re
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class EducationItem(BaseModel):
    degree: str = Field(description="Degree name, e.g., Bachelor of Science")
    major: str = Field(description="Major or field of study, e.g., Computer Science")
    school: str = Field(description="University, college, or school name")
    year: str = Field(description="Graduation year or date range, e.g., 2026 or 2022-2026")

class ResumeData(BaseModel):
    name: str = Field(description="The full name of the candidate")
    education: List[EducationItem] = Field(description="List of education history")
    skills: List[str] = Field(description="List of skills, programming languages, frameworks, databases, tools, and methodologies")

def rule_based_resume_parser(text: str) -> ResumeData:
    """
    A fallback rule-based parser that extracts the candidate's name, education, and skills
    using regex and keyword matching. Used when the Gemini API is blocked or unavailable.
    """
    # 0. Extract Candidate's Name (typically the first non-empty line of the resume content)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidate_name = "Candidate Name"
    for line in lines:
        line_lower = line.lower()
        # Skip lines that are labels or contain contact info details
        if ("email" in line_lower or "@" in line_lower or 
            "phone" in line_lower or "resume" in line_lower or 
            "curriculum" in line_lower or len(line) > 50 or
            "github.com" in line_lower or "linkedin.com" in line_lower):
            continue
        # Verify it looks like a person's name (letters, spaces, dots, hyphens)
        if re.match(r'^[A-Za-z\s\.\-]+$', line):
            candidate_name = line.strip()
            break

    # 1. Extract Skills
    common_skills = [
        "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "ruby", "go", "rust", "php", "sql", "html", "css",
        "react", "angular", "vue", "node\\.js", "express", "django", "flask", "spring", "asp\\.net", "next\\.js", "svelte",
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "oracle", "cassandra",
        "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "jenkins", "terraform",
        "restful apis", "graphql", "machine learning", "deep learning", "agile", "scrum", "project management"
    ]
    
    extracted_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        pattern = r'\b' + skill + r'\b'
        if skill == "c\\+\\+":
            pattern = r'c\+\+'
        elif skill == "node\\.js":
            pattern = r'node\.js'
            
        if re.search(pattern, text_lower):
            display_name = skill.replace("\\", "")
            if display_name == "react": display_name = "React"
            elif display_name == "python": display_name = "Python"
            elif display_name == "javascript": display_name = "JavaScript"
            elif display_name == "typescript": display_name = "TypeScript"
            elif display_name == "java": display_name = "Java"
            elif display_name == "c++": display_name = "C++"
            elif display_name == "sql": display_name = "SQL"
            elif display_name == "postgresql": display_name = "PostgreSQL"
            elif display_name == "mongodb": display_name = "MongoDB"
            elif display_name == "redis": display_name = "Redis"
            elif display_name == "docker": display_name = "Docker"
            elif display_name == "aws": display_name = "AWS"
            elif display_name == "git": display_name = "Git"
            elif display_name == "github": display_name = "GitHub"
            elif display_name == "next.js": display_name = "Next.js"
            elif display_name == "node.js": display_name = "Node.js"
            else:
                display_name = display_name.title()
            extracted_skills.append(display_name)
            
    if not extracted_skills:
        extracted_skills = ["Python", "JavaScript", "SQL", "Git"]
        
    # 2. Extract Education
    education_list = []
    degree_patterns = [
        r"(bachelor|bs|ba|b\.s\.|b\.a\.|master|ms|ma|m\.s\.|m\.a\.|phd|ph\.d\.)\s+(of\s+science|of\s+arts)?\s*(in)?\s*([a-zA-Z\s]+)",
    ]
    
    school = "Unknown University"
    degree = "Bachelor of Science"
    major = "Computer Science"
    year = "2026"
    
    for line in lines:
        line_lower = line.lower()
        if "university" in line_lower or "college" in line_lower or "institute" in line_lower:
            school = line.strip()
        for pattern in degree_patterns:
            match = re.search(pattern, line_lower, re.IGNORECASE)
            if match:
                deg_match = match.group(1).strip()
                if "bach" in deg_match.lower() or "bs" in deg_match.lower() or "b.s." in deg_match.lower():
                    degree = "Bachelor of Science"
                elif "mast" in deg_match.lower() or "ms" in deg_match.lower() or "m.s." in deg_match.lower():
                    degree = "Master of Science"
                else:
                    degree = deg_match.title()
                
                major_match = match.group(4).strip()
                if len(major_match) > 3:
                    major = major_match.title()
        
        year_match = re.search(r'\b(19|20)\d{2}\b', line)
        if year_match and "phone" not in line_lower:
            year = year_match.group(0)
            
    education_list.append(EducationItem(degree=degree, major=major, school=school, year=year))
    
    return ResumeData(name=candidate_name, education=education_list, skills=extracted_skills)

def run_reading_agent(client: genai.Client, resume_text: str) -> ResumeData:
    """
    Analyzes the user's resume text and extracts the candidate's name, education, and skills.
    Uses Gemini 2.5 Flash with structured JSON output.
    Falls back to a local rule-based parser if the API call fails.
    """
    prompt = f"""
    You are the Reading Agent. Analyze the following resume and extract:
    1. The candidate's full name (usually found at the very top of the resume).
    2. The candidate's education history (degrees, majors, institutions, and years).
    3. A comprehensive list of technical and professional skills (e.g., Python, SQL, React, Git, communication, machine learning).
    
    Resume content:
    ---
    {resume_text}
    ---
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeData,
                temperature=0.1
            )
        )
        return ResumeData.model_validate_json(response.text)
    except Exception as e:
        print(f"\n[Reading Agent] Warning: Gemini API call failed ({e}).")
        print("[Reading Agent] Falling back to local rule-based parser...")
        return rule_based_resume_parser(resume_text)
