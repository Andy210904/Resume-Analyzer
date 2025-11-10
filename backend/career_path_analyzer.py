"""
Career Path Analyzer Module
Provides career path recommendations based on extracted skills and experience
"""

import re
from typing import Dict, List, Any, Optional
from collections import Counter

class CareerPathAnalyzer:
    def __init__(self):
        # Define career paths with required skills and progression levels
        self.career_paths = {
            # Software Development Paths
            "Frontend Developer": {
                "required_skills": ["html", "css", "javascript", "react", "vue", "angular", "typescript", "sass", "bootstrap"],
                "nice_to_have": ["webpack", "npm", "git", "figma", "adobe"],
                "industries": ["Technology", "E-commerce", "Media", "Finance"],
                "levels": {
                    "Junior Frontend Developer": {"experience": (0, 2), "skills_needed": 3},
                    "Frontend Developer": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Frontend Developer": {"experience": (4, 7), "skills_needed": 7},
                    "Lead Frontend Developer": {"experience": (7, 10), "skills_needed": 8},
                    "Frontend Architect": {"experience": (10, 15), "skills_needed": 9}
                }
            },
            "Backend Developer": {
                "required_skills": ["python", "java", "node.js", "sql", "mongodb", "postgresql", "api", "rest", "django", "flask", "spring"],
                "nice_to_have": ["docker", "kubernetes", "aws", "microservices", "redis"],
                "industries": ["Technology", "Finance", "Healthcare", "E-commerce"],
                "levels": {
                    "Junior Backend Developer": {"experience": (0, 2), "skills_needed": 3},
                    "Backend Developer": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Backend Developer": {"experience": (4, 7), "skills_needed": 7},
                    "Lead Backend Developer": {"experience": (7, 10), "skills_needed": 8},
                    "Backend Architect": {"experience": (10, 15), "skills_needed": 9}
                }
            },
            "Full Stack Developer": {
                "required_skills": ["html", "css", "javascript", "python", "java", "react", "node.js", "sql", "api", "git"],
                "nice_to_have": ["docker", "aws", "mongodb", "typescript", "redux"],
                "industries": ["Technology", "Startups", "E-commerce", "Finance"],
                "levels": {
                    "Junior Full Stack Developer": {"experience": (0, 2), "skills_needed": 5},
                    "Full Stack Developer": {"experience": (2, 4), "skills_needed": 7},
                    "Senior Full Stack Developer": {"experience": (4, 7), "skills_needed": 9},
                    "Full Stack Team Lead": {"experience": (7, 10), "skills_needed": 10},
                    "Full Stack Architect": {"experience": (10, 15), "skills_needed": 12}
                }
            },
            # Data Science Paths
            "Data Scientist": {
                "required_skills": ["python", "r", "sql", "machine learning", "statistics", "pandas", "numpy", "scikit-learn"],
                "nice_to_have": ["tensorflow", "pytorch", "tableau", "power bi", "aws", "spark"],
                "industries": ["Technology", "Finance", "Healthcare", "Retail", "Consulting"],
                "levels": {
                    "Junior Data Scientist": {"experience": (0, 2), "skills_needed": 4},
                    "Data Scientist": {"experience": (2, 4), "skills_needed": 6},
                    "Senior Data Scientist": {"experience": (4, 7), "skills_needed": 8},
                    "Principal Data Scientist": {"experience": (7, 10), "skills_needed": 9},
                    "Chief Data Scientist": {"experience": (10, 15), "skills_needed": 10}
                }
            },
            "Data Analyst": {
                "required_skills": ["sql", "excel", "python", "tableau", "power bi", "statistics", "data visualization"],
                "nice_to_have": ["r", "sas", "looker", "google analytics", "spark"],
                "industries": ["Finance", "Retail", "Healthcare", "Marketing", "Consulting"],
                "levels": {
                    "Junior Data Analyst": {"experience": (0, 2), "skills_needed": 3},
                    "Data Analyst": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Data Analyst": {"experience": (4, 7), "skills_needed": 6},
                    "Lead Data Analyst": {"experience": (7, 10), "skills_needed": 7},
                    "Analytics Manager": {"experience": (10, 15), "skills_needed": 8}
                }
            },
            # DevOps/Cloud Paths
            "DevOps Engineer": {
                "required_skills": ["docker", "kubernetes", "aws", "jenkins", "git", "linux", "bash", "terraform"],
                "nice_to_have": ["ansible", "prometheus", "grafana", "helm", "istio"],
                "industries": ["Technology", "Finance", "Healthcare", "E-commerce"],
                "levels": {
                    "Junior DevOps Engineer": {"experience": (0, 2), "skills_needed": 4},
                    "DevOps Engineer": {"experience": (2, 4), "skills_needed": 6},
                    "Senior DevOps Engineer": {"experience": (4, 7), "skills_needed": 8},
                    "DevOps Team Lead": {"experience": (7, 10), "skills_needed": 9},
                    "DevOps Architect": {"experience": (10, 15), "skills_needed": 10}
                }
            },
            "Cloud Engineer": {
                "required_skills": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker", "networking"],
                "nice_to_have": ["serverless", "lambda", "cloudformation", "iam", "vpc"],
                "industries": ["Technology", "Finance", "Healthcare", "Government"],
                "levels": {
                    "Junior Cloud Engineer": {"experience": (0, 2), "skills_needed": 3},
                    "Cloud Engineer": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Cloud Engineer": {"experience": (4, 7), "skills_needed": 7},
                    "Cloud Architect": {"experience": (7, 10), "skills_needed": 8},
                    "Principal Cloud Architect": {"experience": (10, 15), "skills_needed": 9}
                }
            },
            # Product/Management Paths
            "Product Manager": {
                "required_skills": ["product management", "analytics", "user research", "agile", "scrum", "roadmapping"],
                "nice_to_have": ["sql", "tableau", "figma", "jira", "a/b testing"],
                "industries": ["Technology", "E-commerce", "Finance", "Healthcare", "Media"],
                "levels": {
                    "Associate Product Manager": {"experience": (0, 2), "skills_needed": 3},
                    "Product Manager": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Product Manager": {"experience": (4, 7), "skills_needed": 6},
                    "Principal Product Manager": {"experience": (7, 10), "skills_needed": 7},
                    "VP of Product": {"experience": (10, 15), "skills_needed": 8}
                }
            },
            # Cybersecurity Paths
            "Cybersecurity Analyst": {
                "required_skills": ["cybersecurity", "networking", "firewalls", "incident response", "vulnerability assessment"],
                "nice_to_have": ["splunk", "wireshark", "metasploit", "nessus", "cissp"],
                "industries": ["Technology", "Finance", "Government", "Healthcare"],
                "levels": {
                    "Junior Security Analyst": {"experience": (0, 2), "skills_needed": 3},
                    "Security Analyst": {"experience": (2, 4), "skills_needed": 5},
                    "Senior Security Analyst": {"experience": (4, 7), "skills_needed": 7},
                    "Security Team Lead": {"experience": (7, 10), "skills_needed": 8},
                    "CISO": {"experience": (10, 15), "skills_needed": 9}
                }
            }
        }

    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text"""
        try:
            # Look for patterns like "3 years", "5+ years", "2-3 years"
            patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)',
                r'(\d+)\+?\s*yrs?\s*(?:of\s+)?(?:experience|exp)',
                r'experience.*?(\d+)\+?\s*years?',
                r'(\d+)\+?\s*years?\s*in',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    return max([int(match) for match in matches])
            
            return 0
        except:
            return 0

    def normalize_skill(self, skill: str) -> str:
        """Normalize skill names for better matching"""
        skill = skill.lower().strip()
        
        # Handle common variations
        skill_mappings = {
            'js': 'javascript',
            'ts': 'typescript',
            'reactjs': 'react',
            'nodejs': 'node.js',
            'postgresql': 'postgres',
            'mysql': 'sql',
            'mongodb': 'mongo',
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform',
            'k8s': 'kubernetes',
            'tf': 'tensorflow'
        }
        
        return skill_mappings.get(skill, skill)

    def calculate_skill_match(self, resume_skills: List[str], career_skills: List[str]) -> Dict[str, Any]:
        """Calculate how well resume skills match career requirements"""
        normalized_resume_skills = [self.normalize_skill(skill) for skill in resume_skills]
        normalized_career_skills = [self.normalize_skill(skill) for skill in career_skills]
        
        matched_skills = []
        for career_skill in normalized_career_skills:
            for resume_skill in normalized_resume_skills:
                if career_skill in resume_skill or resume_skill in career_skill:
                    matched_skills.append(career_skill)
                    break
        
        match_percentage = (len(matched_skills) / len(normalized_career_skills)) * 100 if normalized_career_skills else 0
        
        return {
            "matched_skills": matched_skills,
            "total_required": len(normalized_career_skills),
            "match_percentage": round(match_percentage, 1),
            "missing_skills": [skill for skill in normalized_career_skills if skill not in matched_skills]
        }

    def determine_career_level(self, career_path: str, experience_years: int, matched_skills_count: int) -> Dict[str, Any]:
        """Determine appropriate career level based on experience and skills"""
        if career_path not in self.career_paths:
            return None
        
        levels = self.career_paths[career_path]["levels"]
        suitable_levels = []
        
        for level_name, requirements in levels.items():
            exp_min, exp_max = requirements["experience"]
            skills_needed = requirements["skills_needed"]
            
            # Check if experience and skills match
            exp_match = exp_min <= experience_years <= exp_max
            skills_match = matched_skills_count >= skills_needed
            
            # Calculate suitability score
            exp_score = min(100, max(0, 100 - abs(experience_years - (exp_min + exp_max) / 2) * 10))
            skills_score = min(100, (matched_skills_count / skills_needed) * 100) if skills_needed > 0 else 100
            
            overall_score = (exp_score + skills_score) / 2
            
            suitable_levels.append({
                "level": level_name,
                "experience_match": exp_match,
                "skills_match": skills_match,
                "overall_score": round(overall_score, 1),
                "requirements": requirements
            })
        
        # Sort by overall score
        suitable_levels.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return {
            "recommended_level": suitable_levels[0] if suitable_levels else None,
            "all_levels": suitable_levels
        }

    def analyze_career_paths(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to analyze career paths based on resume data"""
        try:
            # Extract data from resume
            all_text = ""
            if 'text' in resume_data:
                all_text = resume_data['text']
            elif 'sections' in resume_data:
                for section in resume_data['sections'].values():
                    if isinstance(section, str):
                        all_text += " " + section
                    elif isinstance(section, list):
                        all_text += " " + " ".join(section)
            
            # Get skills from previous analysis
            skills = []
            if 'skills' in resume_data:
                if isinstance(resume_data['skills'], list):
                    skills = resume_data['skills']
                elif isinstance(resume_data['skills'], dict):
                    for skill_list in resume_data['skills'].values():
                        if isinstance(skill_list, list):
                            skills.extend(skill_list)
            
            # Extract experience years
            experience_years = self.extract_experience_years(all_text)
            
            # Analyze each career path
            career_recommendations = []
            
            for career_name, career_info in self.career_paths.items():
                # Calculate skill match
                skill_match = self.calculate_skill_match(skills, career_info["required_skills"])
                nice_to_have_match = self.calculate_skill_match(skills, career_info["nice_to_have"])
                
                # Determine career level
                level_info = self.determine_career_level(
                    career_name, 
                    experience_years, 
                    len(skill_match["matched_skills"])
                )
                
                # Calculate overall suitability score
                skill_score = skill_match["match_percentage"]
                bonus_score = nice_to_have_match["match_percentage"] * 0.3  # 30% weight for nice-to-have
                overall_score = min(100, skill_score + bonus_score)
                
                if overall_score >= 20:  # Only include if at least 20% match
                    career_recommendations.append({
                        "career_path": career_name,
                        "overall_score": round(overall_score, 1),
                        "skill_match": skill_match,
                        "nice_to_have_match": nice_to_have_match,
                        "level_recommendations": level_info,
                        "industries": career_info["industries"],
                        "current_experience": experience_years
                    })
            
            # Sort by overall score
            career_recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
            
            # Take top 5 recommendations
            top_recommendations = career_recommendations[:5]
            
            return {
                "career_recommendations": top_recommendations,
                "total_experience_years": experience_years,
                "total_skills_analyzed": len(skills),
                "analysis_summary": {
                    "top_career_match": top_recommendations[0]["career_path"] if top_recommendations else "No suitable match found",
                    "recommended_level": top_recommendations[0]["level_recommendations"]["recommended_level"]["level"] if top_recommendations and top_recommendations[0]["level_recommendations"]["recommended_level"] else "Entry Level",
                    "skill_development_priority": self._get_skill_development_priority(top_recommendations[:3]) if top_recommendations else []
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing career paths: {str(e)}",
                "career_recommendations": [],
                "total_experience_years": 0,
                "total_skills_analyzed": 0
            }

    def _get_skill_development_priority(self, top_careers: List[Dict]) -> List[str]:
        """Get prioritized list of skills to develop based on top career matches"""
        missing_skills = []
        for career in top_careers:
            missing_skills.extend(career["skill_match"]["missing_skills"])
        
        # Count frequency and return top 5 most commonly missing skills
        skill_counts = Counter(missing_skills)
        return [skill for skill, count in skill_counts.most_common(5)]