document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const cancelBtn = document.getElementById('cancelBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    const agentStepper = document.getElementById('agentStepper');
    const placeholderPanel = document.getElementById('placeholderPanel');
    const resultsPanel = document.getElementById('resultsPanel');
    
    const candidateName = document.getElementById('candidateName');
    const candidateEdu = document.getElementById('candidateEdu');
    const candidateSkills = document.getElementById('candidateSkills');
    
    const internshipList = document.getElementById('internshipList');
    const revisionCards = document.getElementById('revisionCards');
    const learningCards = document.getElementById('learningCards');
    
    // Tab Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    let selectedFile = null;
    let stepperInterval = null;

    // ==========================================================================
    // 1. FILE UPLOAD & DRAG-DROP HANDLERS
    // ==========================================================================
    
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    uploadZone.addEventListener('click', () => {
        if (!selectedFile) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', handleFileSelect);

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('dragover');
        }, false);
    });

    uploadZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });

    function handleFileSelect(e) {
        if (e.target.files.length > 0) {
            handleFiles(e.target.files);
        }
    }

    function handleFiles(files) {
        const file = files[0];
        const allowedExtensions = /(\.pdf|\.txt|\.md)$/i;
        
        if (!allowedExtensions.exec(file.name)) {
            alert('Invalid file type. Please upload a .pdf, .txt, or .md file.');
            return;
        }
        
        selectedFile = file;
        fileName.textContent = file.name;
        
        document.querySelector('.upload-content').style.display = 'none';
        fileInfo.style.display = 'flex';
    }

    cancelBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    function resetUpload() {
        selectedFile = null;
        fileInput.value = '';
        document.querySelector('.upload-content').style.display = 'block';
        fileInfo.style.display = 'none';
        agentStepper.style.display = 'none';
        resetStepperVisuals();
    }

    // ==========================================================================
    // 2. MULTI-AGENT PIPELINE ORCHESTRATION & API CALLS
    // ==========================================================================
    
    analyzeBtn.addEventListener('click', () => {
        if (!selectedFile) return;
        
        agentStepper.style.display = 'block';
        analyzeBtn.disabled = true;
        cancelBtn.style.display = 'none';
        
        animateStepperProgress();
        
        const formData = new FormData();
        formData.append('resume', selectedFile);
        
        fetch('/api/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'API call failed'); });
            }
            return response.json();
        })
        .then(data => {
            clearInterval(stepperInterval);
            completeAllSteps();
            
            setTimeout(() => {
                renderResults(data);
            }, 800);
        })
        .catch(err => {
            clearInterval(stepperInterval);
            resetStepperVisuals();
            agentStepper.style.display = 'none';
            analyzeBtn.disabled = false;
            cancelBtn.style.display = 'inline-block';
            alert(`Analysis failed: ${err.message}. The system is ready to try again.`);
        });
    });

    // ==========================================================================
    // 3. STEPPER ANIMATION LOGIC
    // ==========================================================================
    
    function resetStepperVisuals() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(id => {
            const el = document.getElementById(id);
            el.className = 'step';
            el.querySelector('.step-status').innerHTML = '<i class="fa-regular fa-circle"></i>';
        });
    }

    function animateStepperProgress() {
        resetStepperVisuals();
        setStepActive('step1');
        let currentStep = 1;
        
        stepperInterval = setInterval(() => {
            if (currentStep === 1) {
                setStepCompleted('step1');
                setStepActive('step2');
                currentStep = 2;
            } else if (currentStep === 2) {
                setStepCompleted('step2');
                setStepActive('step3');
                currentStep = 3;
            } else if (currentStep === 3) {
                setStepCompleted('step3');
                setStepActive('step4');
                currentStep = 4;
            }
        }, 4000);
    }

    function setStepActive(id) {
        const el = document.getElementById(id);
        el.className = 'step active';
        el.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
    }

    function setStepCompleted(id) {
        const el = document.getElementById(id);
        el.className = 'step completed';
        el.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-circle-check"></i>';
    }

    function completeAllSteps() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(id => setStepCompleted(id));
    }

    // ==========================================================================
    // 4. TAB NAVIGATION
    // ==========================================================================
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // ==========================================================================
    // 5. RENDER RESULTS IN DASHBOARD
    // ==========================================================================
    
    function renderResults(data) {
        placeholderPanel.style.display = 'none';
        resultsPanel.style.display = 'flex';
        
        analyzeBtn.disabled = false;
        cancelBtn.style.display = 'inline-block';
        
        // 1. Populate Candidate Profile
        let name = data.candidate.name;
        if (!name || name === "Candidate Name") {
            if (selectedFile) {
                name = selectedFile.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ").replace(/\b\w/g, c => c.toUpperCase());
                if (name.toLowerCase() === "resume" || name.toLowerCase() === "sample resume") {
                    name = "Alex Mercer";
                }
            } else {
                name = "Candidate Profile";
            }
        }
        candidateName.textContent = name;
        
        if (data.candidate.education && data.candidate.education.length > 0) {
            const edu = data.candidate.education[0];
            candidateEdu.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> ${edu.degree} in ${edu.major} from ${edu.school} (${edu.year})`;
        } else {
            candidateEdu.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> Technical Candidate`;
        }
        
        candidateSkills.innerHTML = '';
        data.candidate.skills.forEach(skill => {
            const span = document.createElement('span');
            span.className = 'badge badge-primary';
            span.textContent = skill;
            candidateSkills.appendChild(span);
        });
        
        // 2. Populate Top 10 Internships
        internshipList.innerHTML = '';
        data.internships.forEach((job, index) => {
            const card = document.createElement('div');
            card.className = 'job-card glass';
            
            const matchPercentage = job.match_percentage;
            const matchClass = matchPercentage >= 75 ? 'high-match' : 'mid-match';
            const strokeDashoffset = 226.2 * (1 - matchPercentage / 100);
            
            const missingBadges = job.missing_skills.length > 0 
                ? job.missing_skills.map(s => `<span class="badge badge-warning">${s}</span>`).join(' ')
                : '<span class="badge badge-success">None - Perfect Fit!</span>';
                
            card.innerHTML = `
                <div class="job-details">
                    <h3>${job.role}</h3>
                    <div class="company-name"><i class="fa-regular fa-building"></i> ${job.company}</div>
                    <div class="job-meta-row">
                        <div class="missing-skills-label">Missing Skills:</div>
                        <div class="skills-badges">${missingBadges}</div>
                    </div>
                </div>
                
                <div class="match-wheel ${matchClass}">
                    <svg>
                        <defs>
                            <linearGradient id="cyanBlueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#00f2fe"/>
                                <stop offset="100%" stop-color="#4facfe"/>
                            </linearGradient>
                            <linearGradient id="purplePinkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#7000ff"/>
                                <stop offset="100%" stop-color="#f355da"/>
                            </linearGradient>
                        </defs>
                        <circle class="bg-circle" cx="40" cy="40" r="36"/>
                        <circle class="progress-circle" cx="40" cy="40" r="36" style="stroke-dashoffset: ${strokeDashoffset}"/>
                    </svg>
                    <div class="match-wheel-label">${matchPercentage}<span>%</span></div>
                </div>
                
                <a href="${job.apply_link}" target="_blank" class="btn btn-primary" style="margin-left: auto;">
                    <i class="fa-solid fa-paper-plane"></i> Apply Now
                </a>
            `;
            
            internshipList.appendChild(card);
        });
        
        // 3. Populate Resume Revisions
        revisionCards.innerHTML = '';
        if (data.resume_changes && data.resume_changes.length > 0) {
            data.resume_changes.forEach((change, idx) => {
                const card = document.createElement('div');
                card.className = 'revision-card';
                
                const skillsBadges = change.associated_skills.map(s => 
                    `<span class="badge badge-warning" style="font-size: 10px; padding: 3px 8px; margin-right: 5px;">${s}</span>`
                ).join('');
                
                card.innerHTML = `
                    <div class="revision-card-header">
                        <h4><i class="fa-solid fa-pen-nib"></i> Section: ${change.section}</h4>
                        <div class="skills-badges" style="margin-top: 5px;">
                            ${skillsBadges}
                        </div>
                    </div>
                    <p style="font-size: 13px; color: var(--text-secondary); margin: 12px 0;">
                        <strong>Recruiter Rationale:</strong> ${change.rationale}
                    </p>
                    <div class="comparison-grid">
                        <div class="before-box">
                            <div class="box-label"><i class="fa-solid fa-circle-xmark"></i> Before (Original)</div>
                            <p>${change.before_example}</p>
                        </div>
                        <div class="after-box">
                            <div class="box-label"><i class="fa-solid fa-circle-check"></i> After (AI Optimized)</div>
                            <p id="revisionText_${idx}">${change.after_example}</p>
                            <button type="button" class="copy-btn" title="Copy Bullet Point" onclick="copyToClipboard('revisionText_${idx}', this)">
                                <i class="fa-regular fa-copy"></i>
                            </button>
                        </div>
                    </div>
                `;
                revisionCards.appendChild(card);
            });
        } else {
            revisionCards.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fa-solid fa-circle-check" style="font-size: 40px; color: var(--green); margin-bottom: 16px;"></i>
                    <h4>Your resume is fully optimized!</h4>
                    <p style="font-size: 13px; margin-top: 8px;">The suggesting agent did not find any critical missing skills across the top matches.</p>
                </div>
            `;
        }
        
        // 4. Populate Skill Enhancements
        learningCards.innerHTML = '';
        if (data.recommended_skills && data.recommended_skills.length > 0) {
            data.recommended_skills.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'learning-card';
                
                const resourcesHtml = rec.learning_resources.map(r => 
                    `<li style="margin-bottom: 5px; font-size: 12px; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-circle-play" style="color: var(--purple); font-size: 10px;"></i>
                        <span>${r}</span>
                     </li>`
                ).join('');
                
                card.innerHTML = `
                    <h4><i class="fa-solid fa-laptop-code"></i> ${rec.skill}</h4>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">
                        <strong>Market Importance:</strong> ${rec.importance}
                    </p>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">
                        <strong>Deep Dive:</strong> ${rec.detailed_explanation}
                    </p>
                    
                    <div class="resources-box" style="margin-bottom: 15px;">
                        <strong style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); display: block; margin-bottom: 6px;">
                            <i class="fa-solid fa-book-bookmark"></i> Recommended Curriculum
                        </strong>
                        <ul style="list-style: none;">
                            ${resourcesHtml}
                        </ul>
                    </div>
                    
                    <div class="learning-path-step" style="margin-top: auto;">
                        <strong style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--purple); display: block; margin-bottom: 6px;">
                            <i class="fa-solid fa-flask"></i> Hands-on Project Blueprint
                        </strong>
                        <p style="font-size: 12px; color: #a7b5cc; line-height: 1.5; white-space: pre-line;">
                            ${rec.project_blueprint}
                        </p>
                    </div>
                `;
                learningCards.appendChild(card);
            });
        } else {
            learningCards.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-secondary); grid-column: span 2;">
                    <i class="fa-solid fa-circle-check" style="font-size: 40px; color: var(--green); margin-bottom: 16px;"></i>
                    <h4>No skill gaps detected!</h4>
                    <p style="font-size: 13px; margin-top: 8px;">You already possess all the required skills for the top-matched internships.</p>
                </div>
            `;
        }
        
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }
});

// ==========================================================================
// 6. HELPER FUNCTIONS (GLOBAL SCOPE)
// ==========================================================================

function copyToClipboard(textElementId, buttonElement) {
    const text = document.getElementById(textElementId).innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        buttonElement.classList.add('copied');
        buttonElement.innerHTML = '<i class="fa-solid fa-check"></i>';
        
        setTimeout(() => {
            buttonElement.classList.remove('copied');
            buttonElement.innerHTML = '<i class="fa-regular fa-copy"></i>';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}
