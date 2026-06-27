from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class SkillRecommendation(BaseModel):
    skill: str = Field(description="The missing skill name")
    importance: str = Field(description="Why this skill is highly valued across the target internships")
    detailed_explanation: str = Field(description="In-depth explanation of this skill, core concepts, and industrial relevance")
    learning_resources: List[str] = Field(description="Specific, high-quality courses, documentation, or textbooks to study this skill")
    project_blueprint: str = Field(description="Step-by-step blueprint of a mini-project the user can build to demonstrate hands-on mastery of this skill")

class ResumeSuggestion(BaseModel):
    section: str = Field(description="The section of the resume to modify (e.g., Projects, Experience, Skills, Summary)")
    associated_skills: List[str] = Field(description="The specific missing skills this resume change aims to address")
    rationale: str = Field(description="The reasoning behind making this change and what recruiters look for")
    before_example: str = Field(description="A typical weak, original bullet point or description representing the current state")
    after_example: str = Field(description="The newly drafted, high-impact, keyword-rich bullet point that highlights the missing skill")

class SuggestionOutput(BaseModel):
    recommended_skills: List[SkillRecommendation] = Field(description="Detailed recommendations for acquiring the missing skills")
    resume_changes: List[ResumeSuggestion] = Field(description="Detailed suggestions for modifying the resume to reflect these skills")

# A premium, highly detailed database of skill acquisition paths and resume modifications
# Used as a fallback when the Gemini API is blocked or fails
LOCAL_SKILL_DATABASE = {
    "Kubernetes": {
        "importance": "The industry-standard container orchestration platform. Powering modern cloud microservices, it ensures auto-scaling, self-healing, and high availability.",
        "detailed_explanation": "Kubernetes (K8s) is critical for managing containerized applications across clusters of hosts. Understanding Pods, Services, Deployments, Ingress controllers, and config management is crucial. Employers value it because it shows you understand modern cloud architecture, continuous deployment, and infrastructure-as-code.",
        "learning_resources": [
            "Kubernetes for the Absolute Beginners (KodeKloud / Udemy)",
            "Official Kubernetes documentation tutorials (kubernetes.io/docs/tutorials/)",
            "Kelsey Hightower's 'Kubernetes The Hard Way' (Advanced GitHub repository)"
        ],
        "project_blueprint": "Create a multi-container deployment: 1. Deploy a Node.js API container and a PostgreSQL database container locally. 2. Write Kubernetes YAML manifests for Deployments and Services. 3. Use Minikube or Kind to run them. 4. Configure a ConfigMap for database credentials and a PersistentVolumeClaim to persist PostgreSQL data. 5. Show that database data survives Pod restarts.",
        "section": "Projects / Developer Tools",
        "associated_skills": ["Kubernetes", "Docker", "DevOps"],
        "rationale": "Adding container orchestration immediately signals to hiring managers that you possess DevOps awareness and are capable of working in production-scale engineering environments.",
        "before_example": "- Built a web app and ran it in containers.",
        "after_example": "- Orchestrated a multi-container application deployment on a local Kubernetes cluster (Minikube), writing YAML manifests for Pods, Services, and PersistentVolumeClaims to ensure database durability and zero-downtime scaling."
    },
    "Docker": {
        "importance": "The foundation of containerization, isolating applications from underlying OS environments and eliminating 'it works on my machine' errors.",
        "detailed_explanation": "Docker package code and all its dependencies into a single container image. It is the absolute prerequisite for modern CI/CD and cloud hosting. Mastery of Docker includes writing efficient multi-stage Dockerfiles, managing container networks, caching layers, and coordinating microservices with Docker Compose.",
        "learning_resources": [
            "Docker Mastery: The Complete Toolset by Bret Fisher (Udemy)",
            "Docker Curriculum (docker-curriculum.com - Free guide)",
            "Official Docker Docs (docs.docker.com/get-started/)"
        ],
        "project_blueprint": "Dockerize a full-stack MERN (MongoDB, Express, React, Node) application: 1. Write a multi-stage Dockerfile for the React frontend to keep the image size under 50MB. 2. Write a Dockerfile for the Express backend. 3. Configure a `docker-compose.yml` file to spin up the frontend, backend, and MongoDB service on a single bridge network. 4. Configure bind mounts to enable hot-reloading in local development.",
        "section": "Projects / Developer Tools",
        "associated_skills": ["Docker", "Containers", "DevOps"],
        "rationale": "Recruiters expect modern software engineering interns to know how to containerize their local code so it integrates smoothly into automated build pipelines.",
        "before_example": "- Ran my app locally using npm start and node index.js.",
        "after_example": "- Containerized the application ecosystem (React frontend & Node.js backend) using multi-stage Dockerfiles and Docker Compose, reducing production image sizes by 65% and standardizing local developer onboarding."
    },
    "AWS": {
        "importance": "The global market leader in cloud computing. Knowledge of cloud resources is essential for deploying, monitoring, and scaling production software.",
        "detailed_explanation": "Amazon Web Services provides virtual servers, storage, databases, and serverless runtimes. Knowing how to leverage AWS S3 for asset storage, AWS EC2 for hosting, and AWS IAM for secure credential management is incredibly attractive to hiring managers who deploy their entire stacks in the cloud.",
        "learning_resources": [
            "AWS Certified Cloud Practitioner Course by Stephane Maarek (Udemy)",
            "AWS Free Tier Project Tutorials (aws.amazon.com/getting-started/hands-on/)",
            "TinyDevops cloud hosting guides"
        ],
        "project_blueprint": "Cloud-deployed dynamic application: 1. Build a web app that allows users to upload files. 2. Write Python code using the `boto3` SDK to upload files directly to an AWS S3 bucket. 3. Configure S3 bucket policies to allow public reads but secure, authenticated writes. 4. Deploy the application backend on an AWS EC2 instance, setting up a reverse proxy with Nginx.",
        "section": "Technical Skills / Experience",
        "associated_skills": ["AWS", "Cloud Computing", "Infrastructure"],
        "rationale": "Hiring managers look for developers who understand deployment lifecycles and security policies in cloud platforms.",
        "before_example": "- Uploaded images to my local server folder.",
        "after_example": "- Architected a secure, cloud-native file storage system by integrating the AWS Boto3 SDK, routing user uploads directly to private AWS S3 buckets, and configuring IAM policies to secure database credentials."
    },
    "Go": {
        "importance": "Google's programming language, highly favored for backend microservices, network tools, and high-concurrency systems due to its speed and goroutines.",
        "detailed_explanation": "Go (Golang) combines the development speed of Python with the execution speed of C++. It is widely used by Stripe, Uber, and Google for high-throughput network services. Learning Go requires understanding statically-typed structures, pointers, channels, and lightweight concurrency (goroutines).",
        "learning_resources": [
            "A Tour of Go (tour.golang.org - Interactive tutorial)",
            "Learn How To Code: Google's Go Programming Language by Todd McLeod (Udemy)",
            "Go by Example (gobyexample.com)"
        ],
        "project_blueprint": "Build a high-concurrency web scraper in Go: 1. Write a scraper that fetches data from multiple URLs. 2. Utilize Go channels and Goroutines to scrape up to 50 URLs concurrently. 3. Implement a worker pool to limit resource exhaustion. 4. Measure execution time and compare it against a single-threaded Python scraper to demonstrate a 5x-10x performance speedup.",
        "section": "Technical Skills / Languages",
        "associated_skills": ["Go (Golang)", "Concurrency", "Backend Engineering"],
        "rationale": "Having Go on your resume immediately makes you eligible for high-performance systems backend roles at companies like Uber, Stripe, and Google.",
        "before_example": "- Wrote a python script to scrape web pages.",
        "after_example": "- Engineered a high-throughput web scraper in Go (Golang) utilizing Goroutines and channels for concurrent worker execution, increasing data ingestion rate by 400% compared to single-threaded scripts."
    },
    "Java": {
        "importance": "The backbone of enterprise software, Android development, and large-scale banking systems. Highly structured and object-oriented.",
        "detailed_explanation": "Java remains one of the most widely used programming languages in the corporate world (Amazon, banks, enterprise IT). Mastering Java requires deep knowledge of Object-Oriented Programming (OOP) design patterns, JVM memory management, and enterprise frameworks like Spring Boot.",
        "learning_resources": [
            "Java Programming Masterclass by Tim Buchalka (Udemy)",
            "Spring Boot Microservices Course on Amigoscode",
            "Effective Java by Joshua Bloch (Book)"
        ],
        "project_blueprint": "Build a secure RESTful API with Spring Boot: 1. Set up a Spring Boot project with Spring Web and Spring Data JPA. 2. Integrate a PostgreSQL database. 3. Implement full JWT authentication and role-based access control (RBAC). 4. Write unit and integration tests using JUnit and Mockito to achieve 80% code coverage.",
        "section": "Technical Skills / Programming Languages",
        "associated_skills": ["Java", "Spring Boot", "OOP Design"],
        "rationale": "Enterprise companies look for strong OOP foundations and familiarity with Java/Spring Boot ecosystems for their backend internships.",
        "before_example": "- Wrote some Java classes in school.",
        "after_example": "- Built a secure, role-based backend API using Java and Spring Boot, integrating Spring Security and JWT authentication, resulting in a robust, test-driven backend with 85% JUnit test coverage."
    },
    "GraphQL": {
        "importance": "An elegant query language for APIs, allowing clients to request exactly the data they need and avoiding over-fetching/under-fetching.",
        "detailed_explanation": "GraphQL was created by Meta to solve mobile network bottlenecks. Unlike REST, which requires hitting multiple endpoints, GraphQL retrieves all nested resources in a single network request. Mastering GraphQL involves writing clean schemas, resolving queries, and managing Apollo client caches.",
        "learning_resources": [
            "GraphQL with React: The Complete Developer's Guide by Stephen Grider (Udemy)",
            "Official Apollo GraphQL Tutorials (apollographql.com/tutorials/)",
            "How to GraphQL (howtographql.com - Free curriculum)"
        ],
        "project_blueprint": "GraphQL social media dashboard API: 1. Set up an Apollo Server with Node.js. 2. Define a schema containing complex nested relations (Users -> Posts -> Comments). 3. Write efficient database resolvers using DataLoader in JavaScript to prevent the N+1 query problem. 4. Integrate Apollo Client in a React frontend to fetch and cache query results dynamically.",
        "section": "Technical Skills / Web Development",
        "associated_skills": ["GraphQL", "Apollo Server", "API Design"],
        "rationale": "Modern web product teams (Meta, GitHub, Shopify) heavily rely on GraphQL. Knowing how to write resolvers shows advanced API design capability.",
        "before_example": "- Wrote REST endpoints to fetch user profiles and posts.",
        "after_example": "- Designed and implemented a GraphQL API utilizing Apollo Server and DataLoader, resolving the N+1 query problem and reducing client-server payload sizes by 45% compared to legacy REST endpoints."
    },
    "C++": {
        "importance": "A high-performance, statically-typed compiled language, fundamental to game engines, operating systems, compilers, and databases.",
        "detailed_explanation": "C++ offers low-level memory manipulation and high performance, making it the language of choice for systems engineering, database kernels, and high-frequency trading platforms. Learning C++ requires mastering pointers, manual memory allocation, smart pointers, and the Standard Template Library (STL).",
        "learning_resources": [
            "Beginning C++ Programming - From Beginner to Beyond (Udemy)",
            "The Cherno's C++ Series (YouTube - High quality video series)",
            "Effective Modern C++ by Scott Meyers (Book)"
        ],
        "project_blueprint": "High-performance custom memory allocator in C++: 1. Write a custom allocator that manages a pre-allocated memory pool (arena allocator). 2. Implement customized `malloc` and `free` logic. 3. Compare execution times and heap fragmentation against standard heap allocations. 4. Verify memory leaks using Valgrind on a Linux terminal.",
        "section": "Technical Skills / Languages",
        "associated_skills": ["C++", "Systems Programming", "Memory Management"],
        "rationale": "High-performance systems companies (Snowflake, Databricks, trading firms) value candidates who understand pointer mechanics, CPU caches, and low-level optimization.",
        "before_example": "- Wrote basic C++ console games in university.",
        "after_example": "- Developed a high-performance custom Arena Memory Allocator in C++17, bypassing standard runtime heap allocation bottlenecks and achieving a 3x speedup for high-frequency allocation patterns."
    }
}

def local_suggesting_agent(user_skills: List[str], top_internships: List[dict]) -> SuggestionOutput:
    """
    A local rule-based suggesting agent that operates when Gemini is unavailable.
    Uses the LOCAL_SKILL_DATABASE to generate highly detailed, premium recommendations
    and before/after resume updates based on the unique missing skills.
    """
    all_missing_skills = set()
    for job in top_internships:
        for skill in job.get("missing_skills", []):
            all_missing_skills.add(skill)
            
    # Filter out empty strings
    missing_skills_list = [s.strip() for s in all_missing_skills if s.strip()]
    if not missing_skills_list:
        missing_skills_list = ["Kubernetes", "Docker"] # Fallback default if none
        
    # Deduplicate and sort to ensure clean processing
    missing_skills_list = sorted(list(set(missing_skills_list)))
    
    recommended_skills = []
    resume_changes = []
    added_sections = set()
    
    for skill in missing_skills_list:
        # Perform fuzzy match against the database
        db_match = None
        for key in LOCAL_SKILL_DATABASE:
            if key.lower() in skill.lower() or skill.lower() in key.lower():
                db_match = LOCAL_SKILL_DATABASE[key]
                break
                
        if db_match:
            recommended_skills.append(SkillRecommendation(
                skill=skill,
                importance=db_match["importance"],
                detailed_explanation=db_match["detailed_explanation"],
                learning_resources=db_match["learning_resources"],
                project_blueprint=db_match["project_blueprint"]
            ))
            
            section = db_match["section"]
            # Allow multiple resume changes if they address different skills in different sections
            section_key = f"{section}_{skill}"
            if section_key not in added_sections:
                added_sections.add(section_key)
                resume_changes.append(ResumeSuggestion(
                    section=section,
                    associated_skills=db_match["associated_skills"],
                    rationale=db_match["rationale"],
                    before_example=db_match["before_example"],
                    after_example=db_match["after_example"]
                ))
        else:
            # Generate a highly detailed generic recommendation for unmatched skills
            recommended_skills.append(SkillRecommendation(
                skill=skill,
                importance=f"This specialized skill is crucial for roles matching this internship's profile, enabling you to build, debug, and optimize systems tailored to their tech stack.",
                detailed_explanation=f"Proficiency in {skill} is a strong differentiator. It proves to recruiters that you can jump directly into their existing codebase and contribute from day one without extensive training.",
                learning_resources=[
                    f"Official {skill} Documentation & Guides (Quick Start Guides)",
                    f"Top-rated {skill} Complete Crash Course (YouTube / Udemy)",
                    f"GitHub open-source repositories featuring {skill} implementations"
                ],
                project_blueprint=f"Build a dedicated portfolio project: 1. Initialize a new application and integrate {skill}. 2. Create a specific feature that utilizes this tool's unique advantages (e.g., if it's a library, implement a core algorithm; if it's a tool, configure an automation script). 3. Document the setup in a README and push the code to GitHub."
            ))
            
            section = "Projects / Technical Skills"
            section_key = f"{section}_{skill}"
            if section_key not in added_sections:
                added_sections.add(section_key)
                resume_changes.append(ResumeSuggestion(
                    section=section,
                    associated_skills=[skill],
                    rationale=f"Integrating hands-on experience with {skill} directly into your projects section demonstrates practical competence, moving beyond a simple list of keywords.",
                    before_example=f"- Worked on a project that required {skill}.",
                    after_example=f"- Integrated {skill} into a core personal project, writing clean modular code and implementing automated test suites, resulting in a highly reliable application architecture."
                ))
                
    # If no suggestions were generated, provide a premium resume booster
    if not resume_changes:
        resume_changes.append(ResumeSuggestion(
            section="Projects (Formatting Upgrade)",
            associated_skills=["Resume Optimization"],
            rationale="Your skills match the target internships perfectly. To stand out, rewrite your existing bullets to focus on metrics, scale, and business impact.",
            before_example="- Developed a task manager website using React and Node.",
            after_example="- Developed a responsive full-stack task manager utilizing React and Node.js, implementing custom state management and securing APIs, resulting in 100% data consistency and a 30% reduction in API response times."
        ))
        
    return SuggestionOutput(recommended_skills=recommended_skills, resume_changes=resume_changes)

def run_suggesting_agent(client: genai.Client, user_skills: List[str], top_internships: List[dict]) -> SuggestionOutput:
    """
    The Suggesting Agent:
    1. Aggregates all missing skills across the top matching internships.
    2. Uses Gemini to generate actionable suggestions for acquiring these skills.
    3. Generates concrete recommendations for updating the resume to highlight these skills.
    Falls back to a local, highly detailed rule-based database if Gemini fails.
    """
    print("[Suggesting Agent] Analyzing missing skills and generating recommendations...")
    
    all_missing_skills = set()
    for job in top_internships:
        for skill in job.get("missing_skills", []):
            all_missing_skills.add(skill)
            
    missing_skills_list = [s.strip() for s in all_missing_skills if s.strip()]
    missing_skills_str = ", ".join(missing_skills_list)
    user_skills_str = ", ".join(user_skills)
    
    jobs_context = []
    for idx, job in enumerate(top_internships):
        jobs_context.append(f"Internship {idx+1}: {job['role']} at {job['company']} (Missing Skills: {', '.join(job.get('missing_skills', []))})")
    jobs_context_str = "\n".join(jobs_context)
    
    prompt = f"""
    You are the Suggesting Agent. Your objective is to help the candidate bridge the gap between their current skills and the requirements of the top internships we found.
    
    Candidate's Current Skills: [{user_skills_str}]
    
    Aggregated Missing Skills: [{missing_skills_str}]
    
    Target Internships Context:
    {jobs_context_str}
    
    Instructions:
    1. For each missing skill, write a comprehensive learning recommendation. Provide a detailed explanation of the skill, specific books/courses, and a detailed step-by-step project blueprint they can build.
    2. For each critical missing skill, write a detailed resume modification suggestion. Explain the section to change, the associated missing skills, the rationale, a weak "Before" example, and a highly optimized "After" example that highlights the skill.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SuggestionOutput,
                temperature=0.3
            )
        )
        return SuggestionOutput.model_validate_json(response.text)
    except Exception as e:
        print(f"[Suggesting Agent] Warning: Generating suggestions via Gemini failed ({e}).")
        print("[Suggesting Agent] Falling back to local premium rule-based database...")
        return local_suggesting_agent(user_skills, top_internships)
