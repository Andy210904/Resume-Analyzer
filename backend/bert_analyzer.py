"""
BERT-Based IntelliResume Module

This module provides advanced NLP capabilities using BERT and other transformer models
for semantic understanding of resume content. It can be easily integrated or removed
without affecting the core functionality.

Features:
- Semantic skill extraction and matching
- Context-aware section parsing
- Intelligent keyword extraction
- Content quality assessment
- Experience level prediction
- Job role matching
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

# Optional imports - will gracefully degrade if not available
BERT_AVAILABLE = False
transformers = None
torch = None
SentenceTransformer = None
cosine_similarity = None

try:
    # First try to import core dependencies
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Then try transformers - this might fail due to tf-keras issue
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        pipeline, BertTokenizer, BertModel
    )
    
    # Finally try sentence transformers
    from sentence_transformers import SentenceTransformer
    
    BERT_AVAILABLE = True
    print("BERT modules loaded successfully")
    
except (ImportError, ValueError, ModuleNotFoundError) as e:
    BERT_AVAILABLE = False
    error_msg = str(e)
    
    if "tf-keras" in error_msg:
        print("BERT modules not available: Keras 3 compatibility issue")
        print("Fix: pip install tf-keras")
        print("Or downgrade: pip install keras==2.15.0")
    elif "torch" in error_msg:
        print("BERT modules not available: PyTorch not installed")
        print("Install with: pip install torch")
    elif "transformers" in error_msg:
        print("BERT modules not available: Transformers library issue")
        print("Install with: pip install transformers")
    elif "sentence_transformers" in error_msg:
        print("BERT modules not available: Sentence transformers issue")
        print("Install with: pip install sentence-transformers")
    else:
        print(f"BERT modules not available: {e}")
    
    print("The application will continue with traditional analysis methods.")

@dataclass
class SkillMatch:
    """Data class for skill matching results"""
    skill: str
    confidence: float
    context: str
    category: str

@dataclass
class BertAnalysisResult:
    """Data class for BERT analysis results"""
    overall_score: int
    skills_extracted: List[SkillMatch]
    experience_level: str
    content_quality: Dict[str, float]
    job_role_predictions: List[Dict[str, float]]
    semantic_suggestions: List[str]
    section_quality: Dict[str, Dict[str, Any]]

class BertResumeAnalyzer:
    """
    Advanced resume analyzer using BERT and transformer models for InteliResume
    """
    
    def __init__(self):
        """Initialize the BERT analyzer with pre-trained models"""
        self.is_available = BERT_AVAILABLE
        
        if not BERT_AVAILABLE:
            print("Warning: BERT analyzer initialized but transformers not available")
            return
        
        try:
            # Initialize models
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {self.device}")
            
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # BERT model for general text understanding
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = AutoModel.from_pretrained('bert-base-uncased')
            self.bert_model.to(self.device)
            
            # Classification pipeline for content analysis
            self.classifier = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Load skill database with embeddings
            self._load_skill_database()
            
            print("BERT IntelliResume Analyzer initialized successfully")
            
        except Exception as e:
            print(f"Error initializing BERT models: {e}")
            self.is_available = False
    
    def _load_skill_database(self):
        """Load and prepare comprehensive skill database with semantic embeddings"""
        self.skill_database = {
            "programming": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
                "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "Dart",
                "Perl", "Objective-C", "Assembly", "COBOL", "Fortran", "Haskell", "Erlang",
                "Clojure", "F#", "VB.NET", "PowerShell", "Bash", "Shell Scripting"
            ],
            "web_frameworks": [
                "React", "Angular", "Vue.js", "Next.js", "Django", "Flask", "Spring Boot",
                "Express.js", "FastAPI", "Laravel", "Ruby on Rails", "ASP.NET", "Svelte",
                "Nuxt.js", "Gatsby", "Bootstrap", "Tailwind CSS", "Material-UI", "Ant Design",
                "Chakra UI", "Semantic UI", "Foundation", "Bulma", "Styled Components"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
                "Oracle", "SQL Server", "Cassandra", "DynamoDB", "Neo4j", "CouchDB",
                "InfluxDB", "TimescaleDB", "Firebase", "Supabase", "PlanetScale", "Prisma",
                "GraphQL", "Apache Kafka", "RabbitMQ", "Apache Pulsar"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
                "Jenkins", "GitLab CI/CD", "GitHub Actions", "Ansible", "Chef", "Puppet",
                "Vagrant", "Helm", "Istio", "OpenShift", "Digital Ocean", "Heroku",
                "Vercel", "Netlify", "AWS Lambda", "Azure Functions", "Google Cloud Functions"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
                "NumPy", "Scikit-learn", "Jupyter", "Apache Spark", "Hadoop", "Tableau",
                "Power BI", "Looker", "D3.js", "Plotly", "Seaborn", "Matplotlib", "Keras",
                "XGBoost", "LightGBM", "CatBoost", "Apache Airflow", "MLflow", "Kubeflow",
                "TensorBoard", "Weights & Biases", "OpenCV", "NLTK", "spaCy", "Hugging Face"
            ],
            "mobile_development": [
                "React Native", "Flutter", "iOS Development", "Android Development",
                "Xamarin", "Ionic", "Cordova", "Swift UI", "Jetpack Compose", "Unity",
                "Unreal Engine", "ARCore", "ARKit", "Core Data", "Room Database"
            ],
            "devops_tools": [
                "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Maven", "Gradle", "npm",
                "Yarn", "Webpack", "Vite", "Parcel", "ESLint", "Prettier", "SonarQube",
                "JIRA", "Confluence", "Slack", "Microsoft Teams", "Trello", "Asana"
            ],
            "ai_ml_tools": [
                "OpenAI", "GPT", "BERT", "Transformer Models", "Computer Vision",
                "Natural Language Processing", "Reinforcement Learning", "AutoML",
                "MLOps", "Model Deployment", "A/B Testing", "Feature Engineering",
                "Data Pipeline", "ETL", "Data Warehousing", "Big Data Analytics"
            ],
            "blockchain_web3": [
                "Blockchain", "Ethereum", "Solidity", "Smart Contracts", "Web3",
                "DeFi", "NFT", "Cryptocurrency", "Bitcoin", "Hyperledger", "Truffle",
                "Hardhat", "Metamask", "IPFS", "Polygon", "Chainlink"
            ],
            "cybersecurity": [
                "Cybersecurity", "Information Security", "Network Security", "Penetration Testing",
                "Ethical Hacking", "CISSP", "CEH", "Security Auditing", "Vulnerability Assessment",
                "Firewall", "IDS", "IPS", "SIEM", "SOC", "Incident Response"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Problem Solving", "Team Work", "Teamwork",
                "Project Management", "Critical Thinking", "Adaptability", "Creativity",
                "Time Management", "Analytical Skills", "Decision Making", "Collaboration",
                "Mentoring", "Public Speaking", "Presentation Skills", "Negotiation",
                "Conflict Resolution", "Emotional Intelligence", "Strategic Planning"
            ],
            "certifications": [
                "AWS Certified", "Azure Certified", "Google Cloud Certified", "PMP",
                "Scrum Master", "Product Owner", "Six Sigma", "ITIL", "CompTIA",
                "Cisco Certified", "Oracle Certified", "Microsoft Certified", "Salesforce Certified"
            ]
        }
        
        # Create embeddings for all skills
        all_skills = []
        self.skill_categories = {}
        
        for category, skills in self.skill_database.items():
            for skill in skills:
                all_skills.append(skill.lower())
                self.skill_categories[skill.lower()] = category
        
        # Generate embeddings for skills
        self.skill_embeddings = self.sentence_model.encode(all_skills)
        self.skill_list = all_skills
    
    def analyze_resume(self, text: str, job_role: Optional[str] = None) -> Dict[str, Any]:
        """
        Main analysis function that provides comprehensive BERT-based analysis
        """
        if not self.is_available:
            return {
                "error": "BERT analyzer not available",
                "fallback": "Using traditional analysis methods"
            }
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Perform various analyses
            skills_analysis = self._extract_skills_semantically(cleaned_text)
            experience_analysis = self._analyze_experience_level(cleaned_text)
            content_quality = self._analyze_content_quality(cleaned_text)
            job_matching = self._predict_job_roles(cleaned_text, job_role)
            section_analysis = self._analyze_sections_semantically(cleaned_text)
            
            # Generate semantic suggestions
            suggestions = self._generate_semantic_suggestions(
                skills_analysis, content_quality, section_analysis
            )
            
            # Calculate overall score
            overall_score = self._calculate_bert_score(
                skills_analysis, content_quality, section_analysis
            )
            
            return {
                "bert_analysis": True,
                "overall_score": overall_score,
                "skills_analysis": skills_analysis,
                "experience_level": experience_analysis,
                "content_quality": content_quality,
                "job_role_matching": job_matching,
                "section_analysis": section_analysis,
                "semantic_suggestions": suggestions,
                "model_confidence": self._calculate_confidence(cleaned_text)
            }
            
        except Exception as e:
            print(f"Error in BERT analysis: {e}")
            return {
                "error": f"BERT analysis failed: {str(e)}",
                "fallback": "Using traditional analysis methods"
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess resume text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.,\-\(\)\[\]\/\+\#\@]', '', text)
        
        return text
    
    def _extract_skills_semantically(self, text: str) -> Dict[str, Any]:
        """Extract skills using enhanced semantic similarity with BERT embeddings"""
        # Split text into sentences and also analyze by phrases
        sentences = self._split_into_sentences(text)
        phrases = self._extract_phrases(text)  # New method for phrase extraction
        
        # Combine sentences and phrases for comprehensive analysis
        text_segments = sentences + phrases
        
        # Encode all text segments
        segment_embeddings = self.sentence_model.encode(text_segments)
        
        # Find semantic matches with skills using multiple approaches
        skill_matches = []
        
        # 1. Semantic similarity matching with lowered threshold
        for i, segment in enumerate(text_segments):
            segment_embedding = segment_embeddings[i].reshape(1, -1)
            
            # Calculate similarity with all skills
            similarities = cosine_similarity(segment_embedding, self.skill_embeddings)[0]
            
            # Find matches with lowered threshold for better recall
            for j, similarity in enumerate(similarities):
                if similarity > 0.45:  # Lowered from 0.6 to 0.45 for better skill detection
                    skill = self.skill_list[j]
                    category = self.skill_categories[skill]
                    
                    skill_match = SkillMatch(
                        skill=skill.title(),
                        confidence=float(similarity),
                        context=segment[:100] + "..." if len(segment) > 100 else segment,
                        category=category
                    )
                    skill_matches.append(skill_match)
        
        # 2. Direct keyword matching with fuzzy matching
        direct_matches = self._extract_skills_directly(text)
        skill_matches.extend(direct_matches)
        
        # 3. Context-aware skill extraction
        context_matches = self._extract_skills_by_context(text)
        skill_matches.extend(context_matches)
        
        # Remove duplicates and cluster similar skills
        unique_skills = self._cluster_and_deduplicate_skills(skill_matches)
        
        sorted_matches = sorted(unique_skills.values(), key=lambda x: x.confidence, reverse=True)
        
        # Categorize skills with improved organization
        skills_by_category = {}
        for match in sorted_matches:
            if match.category not in skills_by_category:
                skills_by_category[match.category] = []
            skills_by_category[match.category].append({
                "skill": match.skill,
                "confidence": round(match.confidence, 3),
                "context": match.context[:80] + "..." if len(match.context) > 80 else match.context
            })
        
        return {
            "total_skills_found": len(sorted_matches),
            "skills_by_category": skills_by_category,
            "top_skills": [
                {
                    "skill": match.skill,
                    "confidence": round(match.confidence, 3),
                    "category": match.category
                }
                for match in sorted_matches[:15]  # Increased from 10 to 15
            ],
            "skill_diversity_score": len(skills_by_category) * 12,  # Increased multiplier
            "extraction_methods": {
                "semantic_matches": len([m for m in skill_matches if m.confidence > 0.45]),
                "direct_matches": len(direct_matches),
                "context_matches": len(context_matches)
            }
        }
    
    def _analyze_experience_level(self, text: str) -> Dict[str, Any]:
        """Predict experience level using enhanced pattern matching and context analysis"""
        # Expanded keywords indicating different experience levels
        junior_indicators = [
            "intern", "internship", "entry level", "entry-level", "graduate", "junior", 
            "trainee", "fresher", "new grad", "recent graduate", "associate", "beginner",
            "starting", "first job", "college student", "university student"
        ]
        
        mid_indicators = [
            "3 years", "4 years", "5 years", "6 years", "7 years", "lead", "coordinator", 
            "specialist", "analyst", "developer", "engineer", "consultant", "team lead",
            "project lead", "software engineer", "full stack", "intermediate", "experienced"
        ]
        
        senior_indicators = [
            "senior", "manager", "director", "principal", "architect", "expert", "head of", 
            "vp", "vice president", "chief", "cto", "ceo", "founder", "co-founder",
            "team manager", "engineering manager", "technical lead", "tech lead",
            "8+ years", "9+ years", "10+ years", "15+ years", "20+ years", "veteran"
        ]
        
        text_lower = text.lower()
        
        # 1. Parse employment dates to calculate actual experience (NEW FEATURE)
        employment_data = self._parse_employment_dates(text)
        calculated_years = employment_data["total_experience_years"]
        
        # 2. Enhanced pattern matching for explicitly mentioned years of experience
        # More specific patterns to avoid false matches with dates and percentages
        years_patterns = [
            r'(?:^|\s)(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)(?:\s|$)',
            r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)(?:\s|$)',
            r'(?:with\s+|have\s+|over\s+)(\d+)\+?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp))?(?:\s|$)',
            r'over\s+(\d+)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp))?(?:\s|$)',
            r'more\s+than\s+(\d+)\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp))?(?:\s|$)',
            r'(\d+)\+\s*(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp))?(?:\s|$)'
        ]
        
        all_years = []
        for pattern in years_patterns:
            matches = re.findall(pattern, text_lower)
            all_years.extend([int(year) for year in matches])
        
        # Get the maximum years mentioned explicitly
        explicit_years = max(all_years) if all_years else 0
        
        # 3. Use calculated years from employment dates as primary source
        # Only fall back to explicit mentions if no employment dates were found
        if calculated_years > 0:
            total_years = calculated_years
        elif explicit_years > 0:
            total_years = explicit_years
        else:
            total_years = 0
            
        # Debug output
        print(f"DEBUG Experience Analysis:")
        print(f"  Calculated from dates: {calculated_years} years")
        print(f"  Explicit years found: {explicit_years} (from: {all_years})")
        print(f"  Final total years: {total_years}")
        
        # Count indicators with context awareness
        junior_count = sum(1 for indicator in junior_indicators if indicator in text_lower)
        mid_count = sum(1 for indicator in mid_indicators if indicator in text_lower)
        senior_count = sum(1 for indicator in senior_indicators if indicator in text_lower)
        
        # Analyze job titles for additional context
        job_titles = self._extract_job_titles(text)
        title_seniority = self._analyze_job_title_seniority(job_titles)
        
        # Analyze responsibilities complexity
        responsibility_level = self._analyze_responsibility_complexity(text)
        
        # Enhanced decision logic with multiple factors
        level_score = {
            "Entry-level": 0,
            "Mid-level": 0,
            "Senior": 0
        }
        
        # Years-based scoring (primary factor)
        if total_years >= 10:
            level_score["Senior"] += 50
        elif total_years >= 6:
            level_score["Senior"] += 30
            level_score["Mid-level"] += 20
        elif total_years >= 3:
            level_score["Mid-level"] += 40
            level_score["Senior"] += 10
        elif total_years >= 1:
            level_score["Mid-level"] += 20
            level_score["Entry-level"] += 20
        else:
            level_score["Entry-level"] += 30
        
        # Indicator-based scoring
        level_score["Entry-level"] += junior_count * 10
        level_score["Mid-level"] += mid_count * 8
        level_score["Senior"] += senior_count * 12
        
        # Job title seniority scoring
        level_score["Entry-level"] += title_seniority.get("junior", 0) * 15
        level_score["Mid-level"] += title_seniority.get("mid", 0) * 15
        level_score["Senior"] += title_seniority.get("senior", 0) * 20
        
        # Responsibility complexity scoring
        level_score["Entry-level"] += responsibility_level.get("entry", 0) * 5
        level_score["Mid-level"] += responsibility_level.get("mid", 0) * 5
        level_score["Senior"] += responsibility_level.get("senior", 0) * 8
        
        # Determine final level
        predicted_level = max(level_score, key=level_score.get)
        max_score = level_score[predicted_level]
        total_score = sum(level_score.values())
        
        # Calculate confidence based on score distribution
        confidence = (max_score / total_score) if total_score > 0 else 0.5
        confidence = min(0.95, max(0.4, confidence))
        
        return {
            "predicted_level": predicted_level,
            "confidence": round(confidence, 3),
            "years_experience": total_years,
            "calculated_from_dates": calculated_years,
            "explicit_years_mentioned": explicit_years,
            "all_years_mentioned": sorted(list(set(all_years)), reverse=True),
            "employment_history": {
                "total_positions": employment_data["number_of_positions"],
                "employment_periods": employment_data["employment_periods"],
                "has_current_position": employment_data["has_current_position"],
                "longest_position_duration": f"{employment_data['longest_position_months']} months ({round(employment_data['longest_position_months']/12, 1)} years)",
                "average_position_duration": f"{employment_data['average_position_duration']} months",
                "total_calculated_experience": f"{employment_data['total_experience_months']} months ({employment_data['total_experience_years']} years)"
            },
            "indicators": {
                "junior": junior_count,
                "mid": mid_count,
                "senior": senior_count
            },
            "job_title_analysis": title_seniority,
            "responsibility_analysis": responsibility_level,
            "level_scores": level_score,
            "experience_source": "calculated_from_dates" if calculated_years > explicit_years else "explicit_mention" if explicit_years > 0 else "indicator_based"
        }
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract potential job titles from resume text"""
        # Common job title patterns
        title_patterns = [
            r'(?:Position|Role|Title|Job)\s*[:\-]\s*([^\n,]+)',
            r'(?:^|\n)\s*([A-Z][^,\n]*(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Coordinator|Lead|Architect|Consultant))',
            r'(?:worked as|employed as|served as)\s+(?:a\s+)?([^,\n]+)',
        ]
        
        titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            titles.extend([title.strip() for title in matches if title.strip()])
        
        return titles[:5]  # Return top 5 most likely titles
    
    def _analyze_job_title_seniority(self, job_titles: List[str]) -> Dict[str, int]:
        """Analyze job titles to determine seniority level"""
        seniority = {"junior": 0, "mid": 0, "senior": 0}
        
        for title in job_titles:
            title_lower = title.lower()
            
            # Junior level titles
            if any(word in title_lower for word in ["junior", "associate", "trainee", "intern", "entry"]):
                seniority["junior"] += 1
            
            # Senior level titles
            elif any(word in title_lower for word in ["senior", "lead", "principal", "manager", "director", "head", "chief", "architect"]):
                seniority["senior"] += 1
            
            # Mid level (default for most professional titles)
            elif any(word in title_lower for word in ["engineer", "developer", "analyst", "specialist", "consultant"]):
                seniority["mid"] += 1
        
        return seniority
    
    def _analyze_responsibility_complexity(self, text: str) -> Dict[str, int]:
        """Analyze the complexity of responsibilities mentioned"""
        complexity = {"entry": 0, "mid": 0, "senior": 0}
        text_lower = text.lower()
        
        # Entry-level responsibility indicators
        entry_indicators = [
            "assisted", "supported", "learned", "trained", "shadowed", "observed",
            "helped", "contributed to", "participated in", "followed"
        ]
        
        # Mid-level responsibility indicators
        mid_indicators = [
            "developed", "implemented", "designed", "built", "created", "maintained",
            "analyzed", "optimized", "improved", "collaborated", "worked with"
        ]
        
        # Senior-level responsibility indicators
        senior_indicators = [
            "led", "managed", "directed", "architected", "established", "founded",
            "mentored", "coached", "guided", "strategized", "planned", "oversaw",
            "coordinated teams", "budget", "hiring", "stakeholder"
        ]
        
        complexity["entry"] = sum(1 for indicator in entry_indicators if indicator in text_lower)
        complexity["mid"] = sum(1 for indicator in mid_indicators if indicator in text_lower)
        complexity["senior"] = sum(1 for indicator in senior_indicators if indicator in text_lower)
        
        return complexity
    
    def _parse_employment_dates(self, text: str) -> Dict[str, Any]:
        """Parse employment dates and calculate actual work experience duration"""
        from datetime import datetime, timedelta
        import calendar
        
        # Month name mappings for different formats
        month_mappings = {
            # Full month names
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
            
            # Short month names (3 letters)
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            
            # Alternative short forms
            'sept': 9,
            
            # Numeric months
            '01': 1, '02': 2, '03': 3, '04': 4, '05': 5, '06': 6,
            '07': 7, '08': 8, '09': 9, '10': 10, '11': 11, '12': 12,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9
        }
        
        # Current date for "present" calculations
        current_date = datetime.now()
        
        # Date range patterns - comprehensive patterns for different formats
        date_patterns = [
            # Format: "March 2024 - October 2025" or "Mar 2024 - Oct 2025"
            r'(?P<start_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))\s+(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|Present|Current|Now)\s*(?P<end_year>20\d{2})?',
            
            # Format: "03/2024 - 10/2025" or "3/2024 - 10/2025"
            r'(?P<start_month>\d{1,2})/(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_month>\d{1,2})/(?P<end_year>20\d{2})|(?P<start_month2>\d{1,2})/(?P<start_year2>20\d{2})\s*[-–—]\s*(?P<end_present>Present|Current|Now)',
            
            # Format: "2024-03 - 2025-10"
            r'(?P<start_year>20\d{2})-(?P<start_month>\d{1,2})\s*[-–—]\s*(?P<end_year>20\d{2})-(?P<end_month>\d{1,2})|(?P<start_year2>20\d{2})-(?P<start_month2>\d{1,2})\s*[-–—]\s*(?P<end_present>Present|Current|Now)',
            
            # Format: "March 2024 - Present" or "Mar 2024 - Present"
            r'(?P<start_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))\s+(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_present>Present|Current|Now|Till\s+date|Ongoing)',
            
            # Format: "2024 - 2025" (year only)
            r'(?P<start_year>20\d{2})\s*[-–—]\s*(?P<end_year>20\d{2})|(?P<start_year2>20\d{2})\s*[-–—]\s*(?P<end_present>Present|Current|Now)',
            
            # Format: "Jan 2024 to Oct 2025"
            r'(?P<start_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))\s+(?P<start_year>20\d{2})\s+to\s+(?P<end_month>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|Present|Current|Now)\s*(?P<end_year>20\d{2})?'
        ]
        
        employment_periods = []
        total_experience_months = 0
        
        def parse_month(month_str):
            """Parse month string to number"""
            if not month_str:
                return 1  # Default to January if not specified
            
            month_str = month_str.lower().strip()
            return month_mappings.get(month_str, 1)
        
        def calculate_months_between(start_month, start_year, end_month, end_year):
            """Calculate months between two dates"""
            try:
                start_date = datetime(int(start_year), int(start_month), 1)
                end_date = datetime(int(end_year), int(end_month), 1)
                
                # Calculate difference in months
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                return max(1, months + 1)  # +1 to include both start and end months, minimum 1 month
            except:
                return 0
        
        # Search for date patterns in text
        text_lower = text.lower()
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    groups = match.groupdict()
                    
                    # Extract start date
                    start_month = None
                    start_year = None
                    end_month = None
                    end_year = None
                    is_current = False
                    
                    # Handle different group combinations
                    if groups.get('start_month') and groups.get('start_year'):
                        start_month = parse_month(groups['start_month'])
                        start_year = int(groups['start_year'])
                    elif groups.get('start_month2') and groups.get('start_year2'):
                        start_month = int(groups['start_month2'])
                        start_year = int(groups['start_year2'])
                    
                    # Handle end date or "present"
                    if groups.get('end_present') or groups.get('end_present'):
                        is_current = True
                        end_month = current_date.month
                        end_year = current_date.year
                    elif groups.get('end_month') and groups.get('end_year'):
                        if groups['end_month'].lower() not in ['present', 'current', 'now']:
                            end_month = parse_month(groups['end_month'])
                            end_year = int(groups['end_year'])
                        else:
                            is_current = True
                            end_month = current_date.month
                            end_year = current_date.year
                    elif groups.get('end_year') and not groups.get('end_month'):
                        end_month = 12  # Assume December if only year provided
                        end_year = int(groups['end_year'])
                    
                    # If we have valid start and end dates, calculate duration
                    if start_month and start_year and end_month and end_year:
                        months = calculate_months_between(start_month, start_year, end_month, end_year)
                        
                        if months > 0:
                            employment_periods.append({
                                "start_date": f"{calendar.month_name[start_month]} {start_year}",
                                "end_date": f"{calendar.month_name[end_month]} {end_year}" if not is_current else "Present",
                                "duration_months": months,
                                "duration_years": round(months / 12, 1),
                                "is_current": is_current,
                                "raw_text": match.group()
                            })
                            
                            total_experience_months += months
                
                except Exception as e:
                    # Skip invalid date patterns
                    continue
        
        # Remove overlapping periods and sort by start date
        employment_periods = self._remove_overlapping_periods(employment_periods)
        
        # Calculate total experience
        total_years = round(total_experience_months / 12, 1)
        
        return {
            "employment_periods": employment_periods,
            "total_experience_months": total_experience_months,
            "total_experience_years": total_years,
            "number_of_positions": len(employment_periods),
            "has_current_position": any(period["is_current"] for period in employment_periods),
            "longest_position_months": max([period["duration_months"] for period in employment_periods], default=0),
            "average_position_duration": round(total_experience_months / len(employment_periods), 1) if employment_periods else 0
        }
    
    def _remove_overlapping_periods(self, periods):
        """Remove overlapping employment periods to avoid double counting"""
        from datetime import datetime
        import calendar
        
        if not periods:
            return periods
        
        # Sort periods by start date (convert to datetime for sorting)
        def parse_date(date_str):
            try:
                if date_str == "Present":
                    return datetime.now()
                # Parse "Month Year" format
                month_year = date_str.split()
                month_num = list(calendar.month_name).index(month_year[0])
                year_num = int(month_year[1])
                return datetime(year_num, month_num, 1)
            except:
                return datetime.now()
        
        sorted_periods = sorted(periods, key=lambda x: parse_date(x["start_date"]))
        
        # Remove overlaps (keep longer periods)
        non_overlapping = []
        for period in sorted_periods:
            if not non_overlapping:
                non_overlapping.append(period)
                continue
            
            # Check for overlap with last period
            last_period = non_overlapping[-1]
            current_start = parse_date(period["start_date"])
            last_end = parse_date(last_period["end_date"])
            
            # If there's no overlap, add the period
            if current_start > last_end:
                non_overlapping.append(period)
            else:
                # If there's overlap, keep the longer period
                if period["duration_months"] > last_period["duration_months"]:
                    non_overlapping[-1] = period
        
        return non_overlapping
    
    def _analyze_content_quality(self, text: str) -> Dict[str, float]:
        """Analyze content quality using comprehensive metrics"""
        sentences = self._split_into_sentences(text)
        words = text.split()
        word_count = len(words)
        
        # 1. Sentence structure and complexity analysis
        if sentences:
            avg_sentence_length = np.mean([len(sentence.split()) for sentence in sentences])
            sentence_variety = len(set([len(s.split()) for s in sentences])) / len(sentences)
        else:
            avg_sentence_length = 0
            sentence_variety = 0
        
        # 2. Enhanced action verbs analysis
        strong_action_verbs = [
            "achieved", "accomplished", "improved", "increased", "developed", "created", 
            "implemented", "managed", "led", "designed", "built", "optimized", "reduced", 
            "delivered", "established", "founded", "launched", "initiated", "pioneered",
            "streamlined", "enhanced", "transformed", "spearheaded", "orchestrated"
        ]
        
        moderate_action_verbs = [
            "worked", "helped", "assisted", "supported", "participated", "contributed",
            "collaborated", "coordinated", "maintained", "updated", "monitored"
        ]
        
        text_lower = text.lower()
        strong_action_count = sum(1 for verb in strong_action_verbs if verb in text_lower)
        moderate_action_count = sum(1 for verb in moderate_action_verbs if verb in text_lower)
        
        action_verb_score = (strong_action_count * 2 + moderate_action_count) / max(len(sentences), 1)
        
        # 3. Quantifiable achievements analysis (enhanced patterns)
        quantification_patterns = [
            r'\d+%',  # Percentages
            r'\d+\+',  # Numbers with plus
            r'\$\d+(?:k|m|million|billion)?',  # Money amounts
            r'\d+(?:k|m|million|billion)?\s*(?:users|customers|clients)',  # User counts
            r'\d+(?:\.\d+)?\s*(?:years?|months?)',  # Time periods
            r'\d+\s*(?:projects?|teams?|people)',  # Count-based achievements
            r'(?:increased|improved|reduced|decreased)\s+(?:by\s+)?\d+',  # Improvement metrics
            r'\d+(?:\.\d+)?\s*(?:x|times)',  # Multipliers
            r'top\s+\d+',  # Rankings
        ]
        
        quantifiable_count = 0
        for pattern in quantification_patterns:
            quantifiable_count += len(re.findall(pattern, text_lower))
        
        quantifiable_score = min(100, quantifiable_count * 8)
        
        # 4. Professional terminology and language analysis
        technical_terms = [
            "architecture", "framework", "methodology", "optimization", "integration",
            "scalability", "performance", "security", "compliance", "automation"
        ]
        
        business_terms = [
            "strategy", "stakeholder", "roi", "kpi", "metrics", "budget", "revenue",
            "client", "customer", "market", "business", "growth", "profit"
        ]
        
        professional_terms = [
            "experience", "skills", "qualifications", "achievements", "responsibilities",
            "projects", "certification", "education", "training", "expertise"
        ]
        
        technical_density = sum(1 for term in technical_terms if term in text_lower) / len(technical_terms)
        business_density = sum(1 for term in business_terms if term in text_lower) / len(business_terms)
        professional_density = sum(1 for term in professional_terms if term in text_lower) / len(professional_terms)
        
        language_sophistication = (technical_density + business_density + professional_density) * 100 / 3
        
        # 5. Content length and readability
        readability_score = 50  # Base score
        if 200 <= word_count <= 800:
            readability_score = 100  # Optimal length
        elif 100 <= word_count < 200:
            readability_score = 75   # Acceptable but short
        elif 800 < word_count <= 1200:
            readability_score = 85   # Acceptable but long
        elif word_count < 100:
            readability_score = 30   # Too short
        else:
            readability_score = 60   # Too long
        
        # 6. Structure and formatting indicators
        structure_indicators = [
            r'•|\*|\-',  # Bullet points
            r'\n\s*\d+\.',  # Numbered lists
            r'[A-Z][^.!?]*:',  # Section headers
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',  # Dates
        ]
        
        structure_score = 0
        for pattern in structure_indicators:
            if re.search(pattern, text):
                structure_score += 25
        
        structure_score = min(100, structure_score)
        
        # Calculate component scores
        sentence_quality = min(100, (avg_sentence_length * 3) + (sentence_variety * 50))
        action_verb_quality = min(100, action_verb_score * 40)
        
        # Overall quality calculation (weighted average)
        overall_quality = (
            sentence_quality * 0.15 +
            action_verb_quality * 0.25 +
            quantifiable_score * 0.20 +
            language_sophistication * 0.20 +
            readability_score * 0.15 +
            structure_score * 0.05
        )
        
        return {
            "overall_quality": round(overall_quality, 2),
            "sentence_complexity": round(sentence_quality, 2),
            "action_verb_usage": round(action_verb_quality, 2),
            "quantifiable_achievements": round(quantifiable_score, 2),
            "professional_language": round(language_sophistication, 2),
            "readability": round(readability_score, 2),
            "structure_formatting": round(structure_score, 2),
            "word_count": word_count,
            "metrics_breakdown": {
                "strong_action_verbs": strong_action_count,
                "moderate_action_verbs": moderate_action_count,
                "quantifiable_items": quantifiable_count,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "sentence_variety": round(sentence_variety, 2)
            }
        }
    
    def _predict_job_roles(self, text: str, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Predict suitable job roles based on content"""
        job_role_keywords = {
            "Software Engineer": [
                "programming", "coding", "development", "software", "application",
                "algorithm", "debugging", "testing", "api", "database"
            ],
            "Data Scientist": [
                "data", "machine learning", "statistics", "analysis", "modeling",
                "python", "r", "visualization", "insights", "prediction"
            ],
            "Product Manager": [
                "product", "strategy", "roadmap", "stakeholder", "requirements",
                "management", "planning", "coordination", "analysis", "market"
            ],
            "DevOps Engineer": [
                "deployment", "infrastructure", "cloud", "automation", "ci/cd",
                "monitoring", "scaling", "docker", "kubernetes", "aws"
            ],
            "UI/UX Designer": [
                "design", "user experience", "interface", "prototype", "wireframe",
                "figma", "sketch", "photoshop", "user research", "usability"
            ]
        }
        
        text_lower = text.lower()
        role_scores = {}
        
        for role, keywords in job_role_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            role_scores[role] = score / len(keywords)  # Normalize score
        
        # Sort by score
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate match with target role if provided
        target_match = None
        if target_role and target_role in role_scores:
            target_match = {
                "role": target_role,
                "match_score": role_scores[target_role],
                "recommendation": "Good match" if role_scores[target_role] > 0.3 else "Consider skill development"
            }
        
        return {
            "predicted_roles": [
                {"role": role, "match_score": round(score, 3)}
                for role, score in sorted_roles[:5]
            ],
            "target_role_analysis": target_match,
            "confidence": max(role_scores.values()) if role_scores else 0
        }
    
    def _analyze_sections_semantically(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Analyze resume sections using semantic understanding"""
        # Define section patterns and their semantic indicators
        section_patterns = {
            "experience": {
                "keywords": ["experience", "work", "employment", "job", "position", "role"],
                "indicators": ["company", "responsibilities", "achievements", "dates"]
            },
            "education": {
                "keywords": ["education", "degree", "university", "college", "school"],
                "indicators": ["graduation", "gpa", "coursework", "academic"]
            },
            "skills": {
                "keywords": ["skills", "technical", "proficiency", "expertise"],
                "indicators": ["programming", "software", "tools", "technologies"]
            },
            "projects": {
                "keywords": ["projects", "portfolio", "github", "development"],
                "indicators": ["built", "created", "developed", "implemented"]
            }
        }
        
        section_analysis = {}
        text_lower = text.lower()
        
        for section, patterns in section_patterns.items():
            # Check for section presence
            keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in text_lower)
            indicator_matches = sum(1 for indicator in patterns["indicators"] if indicator in text_lower)
            
            presence_score = (keyword_matches + indicator_matches) / (len(patterns["keywords"]) + len(patterns["indicators"]))
            
            section_analysis[section] = {
                "present": presence_score > 0.2,
                "quality_score": min(100, presence_score * 100),
                "keyword_matches": keyword_matches,
                "indicator_matches": indicator_matches,
                "recommendations": self._get_section_recommendations(section, presence_score)
            }
        
        return section_analysis
    
    def _generate_semantic_suggestions(self, skills_analysis: Dict, content_quality: Dict, section_analysis: Dict) -> List[str]:
        """Generate intelligent suggestions based on semantic analysis"""
        suggestions = []
        
        # Skills-based suggestions
        if skills_analysis["total_skills_found"] < 10:
            suggestions.append("Consider adding more technical skills to increase your profile strength")
        
        if skills_analysis["skill_diversity_score"] < 40:
            suggestions.append("Diversify your skillset across different categories for better job market appeal")
        
        # Content quality suggestions
        if content_quality["action_verb_usage"] < 50:
            suggestions.append("Use more action verbs to describe your achievements and responsibilities")
        
        if content_quality["quantifiable_achievements"] < 30:
            suggestions.append("Add more quantifiable achievements with specific numbers and percentages")
        
        # Section-based suggestions
        for section, analysis in section_analysis.items():
            if not analysis["present"]:
                suggestions.append(f"Consider adding a dedicated {section.title()} section to your resume")
            elif analysis["quality_score"] < 60:
                suggestions.extend(analysis["recommendations"])
        
        return suggestions[:8]  # Limit to most important suggestions
    
    def _calculate_bert_score(self, skills_analysis: Dict, content_quality: Dict, section_analysis: Dict) -> int:
        """Calculate overall score based on enhanced BERT analysis with balanced weighting"""
        
        # 1. Skills Score (35% weight) - More balanced calculation
        skills_found = skills_analysis["total_skills_found"]
        skill_diversity = skills_analysis["skill_diversity_score"]
        
        # Normalize skills score with diminishing returns
        skills_base_score = min(80, skills_found * 4)  # Up to 80 points for 20+ skills
        diversity_bonus = min(20, skill_diversity * 0.4)  # Up to 20 points for diversity
        skills_score = skills_base_score + diversity_bonus
        
        # 2. Content Quality Score (30% weight)
        quality_score = content_quality["overall_quality"]
        
        # 3. Section Completeness Score (25% weight)
        section_scores = [analysis["quality_score"] for analysis in section_analysis.values()]
        section_avg = np.mean(section_scores) if section_scores else 40
        
        # 4. Experience Integration Score (10% weight) - New component
        # Bonus for well-integrated experience information
        experience_bonus = 0
        if skills_found > 5:  # Has meaningful skills
            experience_bonus += 20
        if len(section_analysis) >= 3:  # Has multiple sections
            experience_bonus += 30
        if quality_score > 60:  # Good content quality
            experience_bonus += 30
        
        experience_integration_score = min(100, experience_bonus)
        
        # Calculate weighted average with improved formula
        overall_score = int(
            (skills_score * 0.35) +           # Skills and expertise
            (quality_score * 0.30) +          # Content quality
            (section_avg * 0.25) +            # Section completeness
            (experience_integration_score * 0.10)  # Experience integration
        )
        
        # Apply bonus for exceptional profiles
        if skills_found >= 15 and quality_score >= 80 and section_avg >= 70:
            overall_score = min(100, overall_score + 5)  # Excellence bonus
        
        # Ensure minimum score for profiles with basic information
        if skills_found >= 3 and section_avg >= 30:
            overall_score = max(overall_score, 45)  # Minimum viable score
        
        return min(100, max(20, overall_score))  # Score range: 20-100
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in the analysis based on text quality and length"""
        word_count = len(text.split())
        
        if word_count < 100:
            return 0.3
        elif word_count < 300:
            return 0.6
        elif word_count < 600:
            return 0.8
        else:
            return 0.9
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for analysis"""
        # Improved sentence splitting with multiple delimiters
        sentences = re.split(r'[.!?]+|\n\s*[-•]\s*|\n\s*\d+\.\s*', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases for skill detection"""
        # Extract phrases between common delimiters
        phrase_patterns = [
            r'(?:Skills?|Technologies?|Tools?|Languages?|Frameworks?)[:\-]\s*([^.\n]+)',
            r'(?:Experience with|Proficient in|Knowledge of)[:\-]?\s*([^.\n]+)',
            r'(?:Used|Worked with|Developed using|Built with)[:\-]?\s*([^.\n]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+\d+(?:\.\d+)?)?)',  # Technology names
        ]
        
        phrases = []
        for pattern in phrase_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    phrases.extend([m.strip() for m in match if m.strip()])
                else:
                    phrases.append(match.strip())
        
        # Also extract comma-separated lists
        skill_sections = re.findall(r'(?:Skills?|Technologies?)[:\-]\s*([^.\n]*)', text, re.IGNORECASE)
        for section in skill_sections:
            items = [item.strip() for item in section.split(',') if item.strip()]
            phrases.extend(items)
        
        return [p for p in phrases if len(p) > 2 and len(p) < 50]
    
    def _extract_skills_directly(self, text: str) -> List[SkillMatch]:
        """Direct keyword matching with fuzzy matching for skill extraction"""
        direct_matches = []
        text_lower = text.lower()
        
        # Create a flat list of all skills for direct matching
        all_skills_flat = []
        for category, skills in self.skill_database.items():
            for skill in skills:
                all_skills_flat.append((skill.lower(), skill, category))
        
        for skill_lower, skill_original, category in all_skills_flat:
            # Direct exact match
            if skill_lower in text_lower:
                # Find the context where this skill appears
                context_start = max(0, text_lower.find(skill_lower) - 50)
                context_end = min(len(text), text_lower.find(skill_lower) + len(skill_lower) + 50)
                context = text[context_start:context_end].strip()
                
                direct_matches.append(SkillMatch(
                    skill=skill_original,
                    confidence=0.95,  # High confidence for direct matches
                    context=context,
                    category=category
                ))
            
            # Fuzzy matching for common variations
            skill_variations = self._generate_skill_variations(skill_original)
            for variation in skill_variations:
                if variation.lower() in text_lower and variation.lower() != skill_lower:
                    context_start = max(0, text_lower.find(variation.lower()) - 50)
                    context_end = min(len(text), text_lower.find(variation.lower()) + len(variation) + 50)
                    context = text[context_start:context_end].strip()
                    
                    direct_matches.append(SkillMatch(
                        skill=skill_original,
                        confidence=0.85,  # Slightly lower confidence for variations
                        context=context,
                        category=category
                    ))
        
        return direct_matches
    
    def _extract_skills_by_context(self, text: str) -> List[SkillMatch]:
        """Extract skills based on contextual indicators"""
        context_matches = []
        
        # Define context patterns that often contain skills
        context_patterns = [
            (r'(?:built|developed|created|implemented|used|worked with|experience with)\s+(?:using\s+)?([^.,\n]+)', 0.75),
            (r'(?:proficient|skilled|experienced)\s+(?:in|with)\s+([^.,\n]+)', 0.80),
            (r'(?:programming|coding)\s+(?:languages?|in)\s*[:\-]?\s*([^.,\n]+)', 0.85),
            (r'(?:frameworks?|libraries?|tools?)\s*[:\-]?\s*([^.,\n]+)', 0.80),
            (r'(?:database|DB)\s+(?:technologies?|systems?)?\s*[:\-]?\s*([^.,\n]+)', 0.85),
        ]
        
        for pattern, base_confidence in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split the match into potential individual skills
                potential_skills = [s.strip() for s in re.split(r'[,&/\|]', match) if s.strip()]
                
                for potential_skill in potential_skills:
                    # Check if this potential skill matches any in our database
                    potential_lower = potential_skill.lower()
                    for category, skills in self.skill_database.items():
                        for skill in skills:
                            if skill.lower() in potential_lower or potential_lower in skill.lower():
                                context_matches.append(SkillMatch(
                                    skill=skill,
                                    confidence=base_confidence,
                                    context=f"...{match}...",
                                    category=category
                                ))
        
        return context_matches
    
    def _generate_skill_variations(self, skill: str) -> List[str]:
        """Generate common variations of skill names"""
        variations = [skill]
        
        # Common abbreviations and variations
        variation_map = {
            "JavaScript": ["JS", "Javascript", "java script"],
            "TypeScript": ["TS", "Typescript", "type script"],
            "Python": ["Python3", "Python 3", "Py"],
            "React": ["ReactJS", "React.js"],
            "Angular": ["AngularJS", "Angular.js"],
            "Vue.js": ["Vue", "VueJS"],
            "Node.js": ["NodeJS", "Node"],
            "Express.js": ["Express", "ExpressJS"],
            "MongoDB": ["Mongo", "Mongo DB"],
            "PostgreSQL": ["Postgres", "PostgresQL"],
            "MySQL": ["My SQL"],
            "Machine Learning": ["ML", "MachineLearning"],
            "Deep Learning": ["DL", "DeepLearning"],
            "Artificial Intelligence": ["AI"],
            "Natural Language Processing": ["NLP"],
            "Amazon Web Services": ["AWS"],
            "Google Cloud Platform": ["GCP", "Google Cloud"],
            "Microsoft Azure": ["Azure"],
        }
        
        if skill in variation_map:
            variations.extend(variation_map[skill])
        
        # Generate generic variations
        variations.append(skill.replace(" ", ""))  # Remove spaces
        variations.append(skill.replace("-", " "))  # Replace hyphens with spaces
        variations.append(skill.replace(".", ""))   # Remove dots
        
        return list(set(variations))  # Remove duplicates
    
    def _cluster_and_deduplicate_skills(self, skill_matches: List[SkillMatch]) -> Dict[str, SkillMatch]:
        """Cluster similar skills and remove duplicates, keeping the best match"""
        unique_skills = {}
        
        for match in skill_matches:
            skill_key = match.skill.lower().strip()
            
            # Check if we already have this skill or a very similar one
            found_similar = False
            for existing_key in unique_skills.keys():
                # Check for exact match or very similar skills
                if (skill_key == existing_key or 
                    self._are_skills_similar(skill_key, existing_key)):
                    # Keep the match with higher confidence
                    if match.confidence > unique_skills[existing_key].confidence:
                        unique_skills[existing_key] = match
                    found_similar = True
                    break
            
            if not found_similar:
                unique_skills[skill_key] = match
        
        return unique_skills
    
    def _are_skills_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar enough to be considered the same"""
        # Remove common variations for comparison
        normalize = lambda s: s.lower().replace(" ", "").replace(".", "").replace("-", "")
        norm1, norm2 = normalize(skill1), normalize(skill2)
        
        # Check if one is contained in the other
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # Check for common abbreviations
        abbrev_pairs = [
            ("js", "javascript"), ("ts", "typescript"), ("py", "python"),
            ("ml", "machinelearning"), ("ai", "artificialintelligence"),
            ("aws", "amazonwebservices"), ("gcp", "googlecloud")
        ]
        
        for abbrev, full in abbrev_pairs:
            if (norm1 == abbrev and abbrev in norm2) or (norm2 == abbrev and abbrev in norm1):
                return True
        
        return False
    
    def _get_section_recommendations(self, section: str, score: float) -> List[str]:
        """Get specific recommendations for each section"""
        recommendations = {
            "experience": [
                "Include specific job titles and company names",
                "Add quantifiable achievements and metrics",
                "Use strong action verbs to describe responsibilities"
            ],
            "education": [
                "Include degree type, institution, and graduation year",
                "Add relevant coursework or academic achievements",
                "Consider including GPA if it's above 3.5"
            ],
            "skills": [
                "Organize skills by category (technical, soft skills, etc.)",
                "Include proficiency levels where relevant",
                "Focus on skills relevant to your target role"
            ],
            "projects": [
                "Describe the technologies used in each project",
                "Explain the impact or results of your projects",
                "Include links to portfolios or GitHub repositories"
            ]
        }
        
        if score < 0.5:
            return recommendations.get(section, [])
        else:
            return []

# Singleton instance
_bert_analyzer = None

def get_bert_analyzer() -> BertResumeAnalyzer:
    """Get singleton instance of BERT analyzer"""
    global _bert_analyzer
    if _bert_analyzer is None:
        _bert_analyzer = BertResumeAnalyzer()
    return _bert_analyzer

def analyze_with_bert(text: str, job_role: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze resume with BERT
    
    Args:
        text: Resume text content
        job_role: Optional target job role for analysis
        
    Returns:
        Dictionary containing BERT analysis results or error message
    """
    analyzer = get_bert_analyzer()
    return analyzer.analyze_resume(text, job_role)

# Test function to check if BERT is working
def test_bert_analyzer():
    """Test function to verify BERT analyzer functionality"""
    if not BERT_AVAILABLE:
        return {"status": "error", "message": "BERT dependencies not installed"}
    
    try:
        analyzer = get_bert_analyzer()
        test_text = """
        John Doe
        Software Engineer
        
        Experience:
        - Developed web applications using Python and React
        - Improved system performance by 40%
        - Led a team of 5 developers
        
        Skills:
        Python, JavaScript, React, AWS, Docker, Machine Learning
        
        Education:
        Bachelor of Computer Science, MIT, 2020
        """
        
        result = analyzer.analyze_resume(test_text, "Software Engineer")
        return {"status": "success", "sample_result": result}
        
    except Exception as e:
        return {"status": "error", "message": f"Test failed: {str(e)}"}

if __name__ == "__main__":
    # Run test when script is executed directly
    test_result = test_bert_analyzer()
    print(json.dumps(test_result, indent=2))