from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
import os
import PyPDF2
import docx
import re
import nltk
import spacy
from nltk.tokenize import word_tokenize
import json
from textblob import TextBlob
from industry_analyzer import IndustryAnalyzer
from career_path_analyzer import CareerPathAnalyzer
from models import db, User, Admin, ResumeAnalysis
from dotenv import load_dotenv

# Import BERT analyzer (optional dependency)
BERT_ENABLED = False
try:
    from bert_analyzer import analyze_with_bert, get_bert_analyzer
    BERT_ENABLED = True
    print("BERT analyzer loaded successfully")
except (ImportError, ValueError, ModuleNotFoundError) as e:
    BERT_ENABLED = False
    print(f"BERT analyzer not available: {e}")
    if "tf-keras" in str(e):
        print("Fix: pip install tf-keras")
    else:
        print("Install BERT dependencies with: pip install -r bert_requirements.txt")

# Load environment variables
load_dotenv()

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

nlp = spacy.load('en_core_web_sm')

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///resume_analyzer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration for better compatibility and persistence
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'resume_analyzer_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
app.config['SESSION_PERMANENT'] = True

# Flask-Login configuration
app.config['REMEMBER_COOKIE_DURATION'] = 86400  # 24 hours
app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Cookie"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Set-Cookie"])
db.init_app(app)
bcrypt = Bcrypt(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.remember_cookie_duration = 86400  # 24 hours

@login_manager.unauthorized_handler
def unauthorized():
    # Return JSON for API calls, redirect for regular pages
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required'}), 401
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    # Try to load as regular user first, then as admin
    user = User.query.get(int(user_id))
    if user:
        return user
    return Admin.query.get(int(user_id))

# Import and register blueprints after app initialization
from auth import auth_bp
from dashboard import dashboard_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_sections(text):
    # Simple section extraction based on common headings
    sections = {}
    print(f"DEBUG: Resume text length: {len(text)}")
    print(f"DEBUG: First 200 chars: {text[:200]}")
    
    # Education section
    education_pattern = r'(?i)(EDUCATION|ACADEMIC BACKGROUND).*?(?=(EXPERIENCE|SKILLS|PROJECTS|$))'
    education_match = re.search(education_pattern, text, re.DOTALL)
    sections['education'] = education_match.group(0) if education_match else ""
    
    # Experience section
    experience_pattern = r'(?i)(EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT).*?(?=(EDUCATION|SKILLS|PROJECTS|$))'
    experience_match = re.search(experience_pattern, text, re.DOTALL)
    sections['experience'] = experience_match.group(0) if experience_match else ""
    
    # Skills section
    skills_pattern = r'(?i)(SKILLS|TECHNICAL SKILLS|EXPERTISE).*?(?=(EDUCATION|EXPERIENCE|PROJECTS|$))'
    skills_match = re.search(skills_pattern, text, re.DOTALL)
    sections['skills'] = skills_match.group(0) if skills_match else ""
    
    # Projects section
    projects_pattern = r'(?i)(PROJECTS|PERSONAL PROJECTS).*?(?=(EDUCATION|EXPERIENCE|SKILLS|$))'
    projects_match = re.search(projects_pattern, text, re.DOTALL)
    sections['projects'] = projects_match.group(0) if projects_match else ""
    
    print(f"DEBUG: Sections found: {[k for k, v in sections.items() if v]}")
    return sections

def analyze_resume(text,filename=None):
    # Extract basic information
    sections = extract_sections(text)
    
    # Analyze the content
    results = {
        "overall_score": 0,
        "sections": {},
        "suggestions": [],
        "strengths": [],
        "word_count": len(word_tokenize(text))
    }
    
    # Check if essential sections exist and analyze them
    section_weights = {
        "education": 20,
        "experience": 35,
        "skills": 25,
        "projects": 20
    }
    
    total_score = 0
    
    # Add some variability based on resume content
    content_factors = {
        'length_factor': min(100, max(50, len(text) / 10)),  # Length affects score
        'keyword_density': len([word for word in text.lower().split() if word in ['experience', 'skills', 'project', 'education']]) / max(1, len(text.split())) * 1000,
        'professional_terms': len(re.findall(r'\b(developed|managed|led|created|implemented|designed|analyzed|optimized)\b', text.lower()))
    }
    
    print(f"DEBUG: Content factors - Length: {content_factors['length_factor']}, Keywords: {content_factors['keyword_density']}, Prof terms: {content_factors['professional_terms']}")
    
    # Analyze education section
    if sections['education']:
        edu_score, edu_feedback = analyze_education(sections['education'])
        results["sections"]["education"] = {
            "exists": True,
            "score": edu_score,
            "feedback": edu_feedback
        }
        total_score += edu_score * section_weights["education"] / 100
    else:
        results["sections"]["education"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Education section is missing"]
        }
        results["suggestions"].append("Add an Education section with your degrees, institutions, and graduation dates")
    
    # Analyze experience section
    if sections['experience']:
        exp_score, exp_feedback = analyze_experience(sections['experience'])
        results["sections"]["experience"] = {
            "exists": True,
            "score": exp_score,
            "feedback": exp_feedback
        }
        total_score += exp_score * section_weights["experience"] / 100
    else:
        results["sections"]["experience"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Experience section is missing"]
        }
        results["suggestions"].append("Add a Work Experience section with your job titles, employers, and achievements")
    
    # Analyze skills section
    if sections['skills']:
        skills_score, skills_feedback = analyze_skills(sections['skills'])
        results["sections"]["skills"] = {
            "exists": True,
            "score": skills_score,
            "feedback": skills_feedback
        }
        total_score += skills_score * section_weights["skills"] / 100
    else:
        results["sections"]["skills"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Skills section is missing"]
        }
        results["suggestions"].append("Add a Skills section highlighting your technical and soft skills")
    
    # Analyze projects section
    if sections['projects']:
        proj_score, proj_feedback = analyze_projects(sections['projects'])
        results["sections"]["projects"] = {
            "exists": True,
            "score": proj_score,
            "feedback": proj_feedback
        }
        total_score += proj_score * section_weights["projects"] / 100
    else:
        results["sections"]["projects"] = {
            "exists": False,
            "score": 0,
            "feedback": ["Projects section is missing or not clearly defined"]
        }
        results["suggestions"].append("Consider adding a Projects section to showcase your practical skills")
    
    # Calculate overall score (out of 100)
    results["overall_score"] = round(total_score)
    
    # Debug logging for scoring
    print(f"DEBUG SCORING - Filename: {filename}")
    print(f"  Education Score: {results['sections'].get('education', {}).get('score', 'Missing')} (Weight: 20%)")
    print(f"  Experience Score: {results['sections'].get('experience', {}).get('score', 'Missing')} (Weight: 35%)")
    print(f"  Skills Score: {results['sections'].get('skills', {}).get('score', 'Missing')} (Weight: 25%)")
    print(f"  Projects Score: {results['sections'].get('projects', {}).get('score', 'Missing')} (Weight: 20%)")
    print(f"  Total Weighted Score: {total_score}")
    print(f"  Final Overall Score: {results['overall_score']}")
    print(f"  Word Count: {results['word_count']}")
    print("---")
    
    # Check for action verbs
    action_verbs = check_action_verbs(text)
    if action_verbs["score"] < 70:
        results["suggestions"].append("Use more strong action verbs to describe your achievements")
    else:
        results["strengths"].append("Good use of action verbs")
    
    # Check for keywords
    keywords = extract_keywords(text)
    if len(keywords) < 10:
        results["suggestions"].append("Include more industry-specific keywords to pass ATS screening")
    else:
        results["strengths"].append("Good use of industry keywords")
    
    # Check resume length
    if results["word_count"] < 300:
        results["suggestions"].append("Your resume seems too short. Consider adding more details about your experience and skills")
    elif results["word_count"] > 700:
        results["suggestions"].append("Your resume may be too lengthy. Try to make it more concise")
    else:
        results["strengths"].append("Resume has an appropriate length")
    
    # Add Career Path Analysis
    try:
        career_analyzer = CareerPathAnalyzer()
        # Extract skills from sections if available
        extracted_skills = []
        if 'skills' in sections:
            skills_text = sections.get('skills', '')
            if skills_text:
                # Simple skill extraction - this can be enhanced
                tech_skills = ["python", "java", "javascript", "html", "css", "react", "angular", 
                             "vue", "node", "nodejs", "sql", "database", "mongodb", "postgresql", 
                             "mysql", "aws", "azure", "gcp", "cloud", "docker", "kubernetes", 
                             "git", "agile", "scrum", "machine learning", "ai", "c++", "c", 
                             "flask", "django", "spring", "tensorflow", "pytorch", "pandas", 
                             "numpy", "scikit-learn", "bootstrap", "typescript", "redux", 
                             "rest", "api", "microservices", "devops", "ci/cd", "jenkins"]
                
                for skill in tech_skills:
                    if skill.lower() in skills_text.lower():
                        extracted_skills.append(skill)
        
        career_analysis_data = {
            'text': text,
            'skills': extracted_skills,
            'sections': sections  # Pass sections for more context
        }
        career_analysis = career_analyzer.analyze_career_paths(career_analysis_data)
        results["career_path_analysis"] = career_analysis
        print(f"DEBUG: Career path analysis completed successfully with {len(extracted_skills)} skills")
    except Exception as e:
        print(f"DEBUG: Career path analysis error: {e}")
        results["career_path_analysis"] = {
            "error": str(e),
            "career_recommendations": [],
            "total_experience_years": 0,
            "total_skills_analyzed": 0,
            "analysis_summary": {
                "top_career_match": "Analysis unavailable",
                "recommended_level": "Entry Level",
                "skill_development_priority": []
            }
        }
        
    return results

def analyze_education(text):
    score = 100  # Base score
    feedback = []
    
    # Check for degree mentions
    degree_keywords = [
    "bachelor", "master", "phd", "doctorate", "diploma", "certificate", "degree",
    "btech", "b.tech", "b.e", "be", "beng", "b.eng",
    "mtech", "m.tech", "m.e", "me", "meng", "m.eng",
    "bca", "mca",
    "bsc", "b.sc", "msc", "m.sc",
    "bcom", "b.com", "mcom", "m.com",
    "bba", "mba", "pgdm", "pgdbm",
    "ba", "b.a", "ma", "m.a",
    "llb", "ll.m", "llm",
    "mbbs", "bds", "b.pharm", "m.pharm", "bpt", "bams", "bhms",
    "b.ed", "bed", "m.ed", "med",
    "associate", "undergraduate", "postgraduate",
    "high school", "hsc", "ssc", "10th", "12th"
    ]
    has_degree = any(keyword in text.lower() for keyword in degree_keywords)
    
    if not has_degree:
        score -= 20
        feedback.append("No clear mention of degree type")
    
    # Check for dates
    date_pattern = r'(19|20)\d{2}'
    dates = re.findall(date_pattern, text)
    
    if not dates:
        score -= 15
        feedback.append("No graduation dates mentioned")
    
    # Check for institutions
    institution_keywords = ["university", "college", "institute", "school"]
    has_institution = any(keyword in text.lower() for keyword in institution_keywords)
    
    if not has_institution:
        score -= 15
        feedback.append("No clear mention of educational institutions")
    
    # Check for GPA or honors
    gpa_pattern = r'(gpa|grade point average|cum laude|honors|distinction)'
    has_gpa = re.search(gpa_pattern, text.lower())
    
    if not has_gpa:
        feedback.append("Consider adding GPA or academic honors if they're strong")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Education section is well-structured")
    
    return score, feedback

def parse_employment_dates_traditional(text):
    """Parse employment dates for traditional analysis (simplified version of BERT method)"""
    from datetime import datetime
    import calendar
    
    # Month mappings
    month_mappings = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'sept': 9
    }
    
    current_date = datetime.now()
    
    # Simplified date patterns for traditional analysis
    date_patterns = [
        # "March 2024 - October 2025"
        r'(?P<start_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))\s+(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|Present|Current|Now)\s*(?P<end_year>20\d{2})?',
        
        # "March 2024 - Present"
        r'(?P<start_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))\s+(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_present>Present|Current|Now)',
        
        # "2024 - 2025"
        r'(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_year>20\d{2})|(?P<start_year2>20\d{2})\s*[-–—]\s*(?P<end_present>Present|Current|Now)'
    ]
    
    total_months = 0
    employment_periods = []
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            try:
                groups = match.groupdict()
                
                # Parse start date
                start_month = 1  # Default to January
                start_year = None
                
                if groups.get('start_month'):
                    start_month = month_mappings.get(groups['start_month'].lower(), 1)
                    start_year = int(groups['start_year'])
                elif groups.get('start_year2'):
                    start_year = int(groups['start_year2'])
                elif groups.get('start_year'):
                    start_year = int(groups['start_year'])
                
                # Parse end date
                end_month = 12  # Default to December
                end_year = None
                is_current = False
                
                if groups.get('end_present'):
                    is_current = True
                    end_month = current_date.month
                    end_year = current_date.year
                elif groups.get('end_month') and groups.get('end_year'):
                    end_month = month_mappings.get(groups['end_month'].lower(), 12)
                    end_year = int(groups['end_year'])
                elif groups.get('end_year'):
                    end_year = int(groups['end_year'])
                
                # Calculate duration
                if start_year and end_year:
                    months = (end_year - start_year) * 12 + (end_month - start_month) + 1
                    if months > 0:
                        total_months += months
                        employment_periods.append({
                            "duration_months": months,
                            "duration_years": round(months / 12, 1),
                            "is_current": is_current,
                            "raw_text": match.group()
                        })
            
            except Exception as e:
                continue
    
    return {
        "total_experience_months": total_months,
        "total_experience_years": round(total_months / 12, 1),
        "employment_periods": employment_periods,
        "number_of_positions": len(employment_periods)
    }

def analyze_experience(text):
    score = 100 # Base score
    feedback = []
    
    # NEW: Parse employment dates to calculate actual experience
    employment_data = parse_employment_dates_traditional(text)
    calculated_years = employment_data["total_experience_years"]
    
    # Check for company names
    company_pattern = r'(inc|llc|ltd|corporation|corp|company)'
    has_companies = re.search(company_pattern, text.lower())
    
    if not has_companies:
        score -= 10
        feedback.append("Company names may not be clearly mentioned")
    
    # Check for job titles
    job_keywords = ["manager", "developer", "engineer", "analyst", "assistant", "director", "coordinator", "specialist"]
    has_job_titles = any(keyword in text.lower() for keyword in job_keywords)
    
    if not has_job_titles:
        score -= 15
        feedback.append("Job titles are not clearly stated")
    
    # Enhanced date checking - now with actual date parsing
    if employment_data["number_of_positions"] == 0:
        score -= 20
        feedback.append("No clear employment date ranges found")
    elif employment_data["number_of_positions"] == 1:
        feedback.append("Single employment period detected")
    else:
        score += 5
        feedback.append(f"Multiple employment periods detected ({employment_data['number_of_positions']} positions)")
    
    # Experience duration feedback
    if calculated_years > 0:
        feedback.append(f"Total calculated experience: {calculated_years} years from {employment_data['number_of_positions']} position(s)")
        
        if calculated_years >= 5:
            score += 10
            feedback.append("Substantial work experience (5+ years)")
        elif calculated_years >= 2:
            score += 5
            feedback.append("Good work experience (2+ years)")
        elif calculated_years >= 1:
            feedback.append("Entry-level experience (1+ year)")
        else:
            feedback.append("Limited work experience (less than 1 year)")
    
    # Check for bullet points
    bullet_pattern = r'•|\*|\-'
    bullets = re.findall(bullet_pattern, text)
    
    if len(bullets) < 3:
        score -= 10
        feedback.append("Consider using bullet points to highlight achievements")
    
    # Check for metrics and achievements
    metrics_pattern = r'(\d+%|\d+ percent|increased|decreased|improved|reduced|led|managed|created)'
    metrics = re.findall(metrics_pattern, text.lower())
    
    if len(metrics) < 3:
        score -= 15
        feedback.append("Add more quantifiable achievements with metrics")
    else:
        score += 10
        feedback.append("Good use of quantifiable metrics")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Experience section effectively highlights your work history")
    
    return score, feedback

def analyze_skills(text):
    score = 100 # Base score
    feedback = []
    
    # Count number of skills
    text = text.lower()
    
    # Technical skills
    tech_skills = ["python", "java", "javascript", "html", "css", "react", "angular", 
                   "node", "sql", "database", "aws", "azure", "cloud", "docker", 
                   "kubernetes", "git", "agile", "scrum", "machine learning", "ai","c++","c"]
    
    tech_count = sum(1 for skill in tech_skills if skill in text)
    
    # Soft skills
    soft_skills = ["communication", "leadership", "teamwork", "problem solving", 
                   "critical thinking", "time management", "project management", 
                   "collaboration", "adaptability", "creativity"]
    
    soft_count = sum(1 for skill in soft_skills if skill in text)
    
    if tech_count < 5:
        score -= 15
        feedback.append("Add more technical skills relevant to your field")
    
    if soft_count < 3:
        score -= 10
        feedback.append("Include some soft skills to show your workplace effectiveness")
    
    # Check organization of skills section
    organization_patterns = [r',', r'•', r'\|', r'\\']
    has_organization = any(re.search(pattern, text) for pattern in organization_patterns)
    
    if not has_organization:
        score -= 10
        feedback.append("Organize your skills better (e.g., using categories or separators)")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if tech_count >= 8 and soft_count >= 5:
        score += 10
        feedback.append("Excellent variety of skills listed")
    
    return score, feedback

def analyze_projects(text):
    score = 100  # Base score
    feedback = []
    
    # Check for project titles
    project_count = len(re.findall(r'(?:^|\n)([A-Z][^\n]+)(?:\n|$)', text))
    
    if project_count < 2:
        score -= 15
        feedback.append("Include more projects to showcase your abilities")
    
    # Check for technologies used
    tech_pattern = r'(tech stack|tools used|using|with|built on|developed in|utilizing) ([^.]*)'
    has_tech = re.search(tech_pattern, text.lower())
    
    if not has_tech:
        score -= 15
        feedback.append("Mention technologies used in each project")
    
    # Check for project descriptions
    if len(text.split('\n')) < 5:
        score -= 10
        feedback.append("Add more detailed descriptions of your projects")
    
    # Check for results or impact
    impact_pattern = r'(resulted in|improved|increased|decreased|reduced|enhanced)'
    has_impact = re.search(impact_pattern, text.lower())
    
    if not has_impact:
        score -= 10
        feedback.append("Describe the impact or results of your projects")
    
    # Return the results (cap score between 0-100)
    score = max(0, min(100, score))
    
    if score >= 80:
        feedback.append("Project section effectively demonstrates your practical skills")
    
    return score, feedback

def check_action_verbs(text):
    action_verbs = [
        "achieved", "improved", "trained", "maintained", "managed", "created",
        "resolved", "volunteered", "influenced", "increased", "decreased",
        "researched", "authored", "developed", "launched", "designed",
        "implemented", "established", "coordinated", "generated", "delivered",
        "produced", "performed", "directed", "organized", "supervised"
    ]
    
    # Count occurrences of action verbs
    text_lower = text.lower()
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    
    # Calculate score based on number of unique action verbs found
    score = min(100, verb_count * 5)
    
    return {
        "score": score,
        "count": verb_count,
        "suggested_verbs": action_verbs[:10]  # Return some suggested verbs
    }

def extract_keywords(text):
    # Extract potential keywords using NLP
    doc = nlp(text)
    
    # Extract noun phrases as potential keywords
    keywords = [chunk.text.lower() for chunk in doc.noun_chunks]
    
    # Filter out common words and keep only unique keywords
    stopwords = nltk.corpus.stopwords.words('english')
    keywords = [word for word in keywords if word not in stopwords and len(word) > 3]
    
    return list(set(keywords))[:20]  



@app.route('/api/bert/status', methods=['GET'])
def bert_status():
    """Check BERT analyzer status and capabilities"""
    if BERT_ENABLED:
        try:
            analyzer = get_bert_analyzer()
            return jsonify({
                "available": analyzer.is_available,
                "device": str(analyzer.device) if hasattr(analyzer, 'device') else "unknown",
                "models_loaded": analyzer.is_available,
                "version": "1.0.0"
            })
        except Exception as e:
            return jsonify({
                "available": False,
                "error": str(e),
                "message": "BERT analyzer initialization failed"
            })
    else:
        return jsonify({
            "available": False,
            "message": "BERT dependencies not installed",
            "install_command": "pip install -r bert_requirements.txt"
        })

@app.route('/api/bert/test', methods=['POST'])
def test_bert():
    """Test BERT analyzer with sample text"""
    if not BERT_ENABLED:
        return jsonify({"error": "BERT not available"}), 400
    
    try:
        from bert_analyzer import test_bert_analyzer
        result = test_bert_analyzer()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    industry = request.form.get('job_role') 
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Create unique filename to avoid conflicts
        import uuid
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filename)
        
        try:
            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(filename)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(filename)
            else:
                return jsonify({"error": "Unsupported file format"}), 400
            
            # Analyze the resume text
            analysis_results = analyze_resume(text, file.filename)
            print(f"DEBUG: Analysis results overall_score: {analysis_results.get('overall_score')}")
            
            # Add industry-specific analysis if requested
            if industry:
                industry_analyzer = IndustryAnalyzer()
                industry_analysis = industry_analyzer.analyze_for_industry(text, industry)
                analysis_results["industry_analysis"] = industry_analysis
                print(f"DEBUG: Industry analysis overall_score: {industry_analysis.get('overall_score')}")
            
            # Add BERT-based analysis if available
            if BERT_ENABLED:
                try:
                    bert_analysis = analyze_with_bert(text, industry)
                    if not bert_analysis.get('error'):
                        analysis_results["bert_analysis"] = bert_analysis
                        # Enhance overall score with BERT insights
                        if bert_analysis.get('overall_score'):
                            # Weighted average of traditional and BERT scores
                            traditional_score = analysis_results.get('overall_score', 0)
                            bert_score = bert_analysis.get('overall_score', 0)
                            analysis_results["enhanced_score"] = int((traditional_score * 0.6) + (bert_score * 0.4))
                        print(f"DEBUG: BERT analysis completed successfully")
                    else:
                        print(f"DEBUG: BERT analysis failed: {bert_analysis.get('error')}")
                except Exception as e:
                    print(f"DEBUG: BERT analysis error: {e}")
            else:
                analysis_results["bert_available"] = False
            
            # Add advanced NLP analysis
            blob = TextBlob(text)
            analysis_results["sentiment"] = {
                "polarity": round(blob.sentiment.polarity, 2),
                "subjectivity": round(blob.sentiment.subjectivity, 2)
            }
            
            # Save analysis to database (only for regular users, not admins)
            if isinstance(current_user, User):
                try:
                    # Get file size from saved file instead of reading again
                    file_size = os.path.getsize(filename)
                    resume_analysis = ResumeAnalysis(
                        user_id=current_user.id,
                        filename=file.filename,
                        file_size=file_size,
                        job_role=industry or 'general',
                        overall_score=analysis_results.get('overall_score'),
                        industry_score=analysis_results.get('industry_analysis', {}).get('overall_score'),
                        word_count=analysis_results.get('word_count'),
                        analysis_results=json.dumps(analysis_results),
                        suggestions=json.dumps(analysis_results.get('suggestions', [])),
                        strengths=json.dumps(analysis_results.get('strengths', []))
                    )
                    db.session.add(resume_analysis)
                    db.session.commit()
                    
                    # Add analysis ID to response
                    analysis_results['analysis_id'] = resume_analysis.id
                    
                except Exception as e:
                    # Don't fail the analysis if database save fails
                    print(f"Failed to save analysis to database: {e}")
                    db.session.rollback()
            
            print(f"DEBUG: Final analysis_results keys: {analysis_results.keys()}")
            print(f"DEBUG: Final overall_score: {analysis_results.get('overall_score')}")
            return jsonify(analysis_results)
            
        finally:
            # Clean up the uploaded file
            if os.path.exists(filename):
                os.remove(filename)
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/analysis/download/<int:analysis_id>', methods=['GET'])
@login_required
def download_analysis(analysis_id):
    """Return the stored analysis as a downloadable PDF report for the owner or admin."""
    try:
        # Try to find the analysis
        analysis = ResumeAnalysis.query.filter_by(id=analysis_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        # Only allow owner or admin
        if isinstance(current_user, User):
            if analysis.user_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403

        # Generate PDF report
        try:
            from pdf_generator import ResumeReportGenerator
            import io
            
            # Create PDF generator
            generator = ResumeReportGenerator()
            
            # Create buffer for PDF
            pdf_buffer = io.BytesIO()
            
            # Get analysis data
            analysis_data = analysis.to_dict()
            
            # Generate PDF
            generator.generate_report(analysis_data, pdf_buffer)
            pdf_buffer.seek(0)
            
            # Create response
            from flask import Response
            pdf_data = pdf_buffer.getvalue()
            resp = Response(pdf_data, mimetype='application/pdf')
            filename = f"resume_analysis_report_{analysis.id}.pdf"
            resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            resp.headers['Content-Type'] = 'application/pdf'
            resp.headers['Content-Length'] = str(len(pdf_data))
            
            return resp
            
        except ImportError:
            # Fallback to JSON if PDF generation fails
            content = analysis.to_dict()
            from flask import Response
            import json as _json
            json_data = _json.dumps(content, indent=2)
            resp = Response(json_data, mimetype='application/json')
            filename = f"analysis_{analysis.id}.json"
            resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            resp.headers['Content-Type'] = 'application/json'
            resp.headers['Content-Length'] = str(len(json_data.encode('utf-8')))
            return resp
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if it doesn't exist
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(
            username='admin',
            email='admin@resumeanalyzer.com',
            first_name='Admin',
            last_name='User',
            is_super_admin=True
        )
        admin.set_password('Admin123!')  # Change this in production
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='Admin123!'")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)