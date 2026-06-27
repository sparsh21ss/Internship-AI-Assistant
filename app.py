import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from config import get_client
from utils import read_resume
from agents.reading_agent import run_reading_agent
from agents.search_agent import run_search_agent
from agents.comparing_agent import run_comparing_agent
from agents.suggesting_agent import run_suggesting_agent

app = Flask(__name__, static_folder='static', template_folder='templates')

# Use /tmp on cloud (Render), local uploads/ folder for local dev
UPLOAD_FOLDER = os.path.join('/tmp', 'internship_uploads') if os.environ.get('RENDER') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Limit upload size to 8MB

@app.route('/')
def index():
    """Serves the main web interface."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Handles file upload, parses resume, searches for internships, matches, 
    and generates recommendations using the 4-agent system.
    """
    # 1. Verify file presence
    if 'resume' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file:
        return jsonify({"error": "Failed to upload file"}), 400

    # 2. Save file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 3. Read resume text
        resume_text = read_resume(filepath)
        if not resume_text.strip():
            return jsonify({"error": "Resume content is empty. Please upload a valid text or PDF file."}), 400

        # 4. Initialize Gemini Client
        client = get_client()

        # 5. Agent 1: Reading Agent
        print("[Web Backend] Running Reading Agent...")
        resume_data = run_reading_agent(client, resume_text)
        
        # 6. Agent 2: Internship Search Agent
        print("[Web Backend] Running Internship Search Agent...")
        raw_internships = run_search_agent(client, resume_data.skills)
        if not raw_internships:
            return jsonify({"error": "No internships found matching your skills."}), 404

        # 7. Agent 3: Comparing Agent
        print("[Web Backend] Running Comparing Agent...")
        top_internships = run_comparing_agent(client, resume_data.skills, raw_internships)

        # 8. Agent 4: Suggesting Agent
        print("[Web Backend] Running Suggesting Agent...")
        suggestions = run_suggesting_agent(client, resume_data.skills, top_internships)

        # 9. Format response data to match the updated Pydantic schemas
        response_data = {
            "status": "success",
            "candidate": {
                "name": resume_data.name,
                "skills": resume_data.skills,
                "education": [
                    {
                        "degree": edu.degree,
                        "major": edu.major,
                        "school": edu.school,
                        "year": edu.year
                    } for edu in resume_data.education
                ]
            },
            "internships": top_internships,
            "resume_changes": [
                {
                    "section": change.section,
                    "associated_skills": change.associated_skills,
                    "rationale": change.rationale,
                    "before_example": change.before_example,
                    "after_example": change.after_example
                } for change in suggestions.resume_changes
            ],
            "recommended_skills": [
                {
                    "skill": rec.skill,
                    "importance": rec.importance,
                    "detailed_explanation": rec.detailed_explanation,
                    "learning_resources": rec.learning_resources,
                    "project_blueprint": rec.project_blueprint
                } for rec in suggestions.recommended_skills
            ]
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"[Web Backend] Error during analysis: {e}")
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500
        
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as ex:
                print(f"[Web Backend] Warning: Failed to delete temp file {filepath}: {ex}")

if __name__ == '__main__':
    # Run server on port 5000
    # host='0.0.0.0' allows it to accept connections from Cloudflare Tunnel
    app.run(host='0.0.0.0', port=5000, debug=False)
