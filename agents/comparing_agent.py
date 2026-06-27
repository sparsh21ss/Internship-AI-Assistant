from typing import List, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from utils import cosine_similarity

class SkillWeight(BaseModel):
    skill_name: str = Field(description="Name of the required skill")
    weight: float = Field(description="Weight of this skill in the range [0.0, 1.0], reflecting importance. Sum of all weights must be exactly 1.0.")
    user_has_skill: bool = Field(description="True if the user possesses this skill or a highly similar/equivalent skill, False otherwise.")

class SkillWeightAnalysis(BaseModel):
    skills_analysis: List[SkillWeight] = Field(description="Analysis of the required skills, their weights, and user match status.")

def get_embedding(client: genai.Client, text: str) -> List[float]:
    """
    Generates a text embedding using Gemini's text-embedding-004 model.
    Returns all zeros if it fails.
    """
    try:
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=text
        )
        return response.embeddings[0].values
    except Exception:
        # Return all zeros to signal fallback mode
        return [0.0] * 768

def local_weighted_skills_comparison(user_skills: List[str], job_requirements: List[str]) -> Dict[str, Any]:
    """
    A local rule-based comparison when Gemini API is unavailable.
    Distributes weights equally and matches skills using case-insensitive substring comparisons.
    """
    if not job_requirements:
        return {"weighted_score": 100.0, "missing_skills": [], "analysis": []}
        
    num_reqs = len(job_requirements)
    equal_weight = 1.0 / num_reqs
    
    analysis = []
    user_skills_lower = [s.lower().strip() for s in user_skills]
    
    for req in job_requirements:
        req_clean = req.strip()
        req_lower = req_clean.lower()
        
        # Check for semantic matches (e.g. "React" and "ReactJS", "Node" and "Node.js")
        has_skill = False
        for user_skill in user_skills_lower:
            if user_skill in req_lower or req_lower in user_skill:
                has_skill = True
                break
            # Common equivalents
            if (user_skill == "react" and "reactjs" in req_lower) or (user_skill == "reactjs" and "react" in req_lower):
                has_skill = True
                break
            if (user_skill == "node" and "node.js" in req_lower) or (user_skill == "node.js" and "node" in req_lower):
                has_skill = True
                break
            if (user_skill == "git" and "github" in req_lower) or (user_skill == "github" and "git" in req_lower):
                has_skill = True
                break
                
        analysis.append(SkillWeight(
            skill_name=req_clean,
            weight=equal_weight,
            user_has_skill=has_skill
        ))
        
    weighted_score = sum(item.weight * 100 for item in analysis if item.user_has_skill)
    missing_skills = [item.skill_name for item in analysis if not item.user_has_skill]
    
    return {
        "weighted_score": weighted_score,
        "missing_skills": missing_skills,
        "analysis": [item.model_dump() for item in analysis]
    }

def analyze_weighted_skills(client: genai.Client, user_skills: List[str], job_requirements: List[str]) -> Dict[str, Any]:
    """
    Uses Gemini to analyze required skills, assign weights, and check which ones the user has.
    Falls back to a local comparison if the API call fails.
    """
    user_skills_str = ", ".join(user_skills)
    job_reqs_str = ", ".join(job_requirements)
    
    prompt = f"""
    You are the Comparing Agent. Your task is to perform a weighted skill analysis.
    
    User's Skills: [{user_skills_str}]
    Internship Required Skills: [{job_reqs_str}]
    
    Instructions:
    1. List the required skills for this internship.
    2. Assign a decimal weight to each skill (summing to 1.0).
    3. Check if the user has the skill.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillWeightAnalysis,
                temperature=0.1
            )
        )
        analysis = SkillWeightAnalysis.model_validate_json(response.text).skills_analysis
        
        total_weight = sum(item.weight for item in analysis)
        if total_weight > 0:
            for item in analysis:
                item.weight = item.weight / total_weight
                
        weighted_score = sum(item.weight * 100 for item in analysis if item.user_has_skill)
        missing_skills = [item.skill_name for item in analysis if not item.user_has_skill]
        
        return {
            "weighted_score": weighted_score,
            "missing_skills": missing_skills,
            "analysis": [item.model_dump() for item in analysis]
        }
    except Exception:
        # Fallback to local rule-based comparison
        return local_weighted_skills_comparison(user_skills, job_requirements)

def run_comparing_agent(client: genai.Client, user_skills: List[str], internships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    The Comparing Agent:
    1. Compares user skills with each internship's requirements.
    2. Calculates Match% = 50% weighted skills + 50% embedded skills.
    3. Sorts and returns the top 10 internships.
    """
    print(f"[Comparing Agent] Beginning match comparison for {len(internships)} internships...")
    
    user_skills_text = ", ".join(user_skills)
    user_embedding = get_embedding(client, user_skills_text)
    embedding_failed = (sum(user_embedding) == 0.0)
    
    if embedding_failed:
        print("[Comparing Agent] Warning: Embedding API failed. Falling back to local semantic Jaccard scoring...")
        
    scored_internships = []
    
    for idx, job in enumerate(internships):
        reqs = job.get("requirements", [])
        if not reqs:
            reqs = [job.get("description_snippet", "")]
            
        # 1. Weighted Skills Score (50%)
        weighted_result = analyze_weighted_skills(client, user_skills, reqs)
        weighted_score = weighted_result["weighted_score"]
        missing_skills = weighted_result["missing_skills"]
        
        # 2. Embedded Skills Score (50%)
        if embedding_failed:
            # Fallback local similarity calculation:
            # Calculate Jaccard similarity of skill lists, scaled to a realistic 55%-95% embedding score range
            user_set = set(s.lower().strip() for s in user_skills)
            job_set = set(s.lower().strip() for s in reqs)
            
            # Simple intersection count considering substring matching
            intersection_count = 0
            for u in user_set:
                for j in job_set:
                    if u in j or j in u:
                        intersection_count += 1
                        break
                        
            union_len = len(user_set) + len(job_set) - intersection_count
            jaccard = intersection_count / union_len if union_len > 0 else 0.0
            
            # Map Jaccard [0.0, 1.0] to embedding similarity [55.0, 95.0]
            embedded_score = 55.0 + (40.0 * jaccard)
        else:
            job_reqs_text = ", ".join(reqs)
            job_embedding = get_embedding(client, job_reqs_text)
            if sum(job_embedding) == 0.0:
                # If job embedding fails but user embedding worked, Jaccard fallback
                embedded_score = 65.0
            else:
                embedded_score = cosine_similarity(user_embedding, job_embedding) * 100.0
        
        # 3. Hybrid Match%
        total_match = (0.5 * weighted_score) + (0.5 * embedded_score)
        total_match = min(100.0, max(0.0, total_match))
        
        scored_job = job.copy()
        scored_job["match_percentage"] = round(total_match, 1)
        scored_job["weighted_score"] = round(weighted_score, 1)
        scored_job["embedded_score"] = round(embedded_score, 1)
        scored_job["missing_skills"] = missing_skills
        
        scored_internships.append(scored_job)
        
    # Sort by Match% in descending order
    scored_internships.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    # Return top 10
    top_10 = scored_internships[:10]
    print(f"[Comparing Agent] Ranked and selected the top 10 internships.")
    for i, job in enumerate(top_10):
        print(f"  {i+1}. {job['company']} ({job['role']}) - Match: {job['match_percentage']}%")
        
    return top_10
