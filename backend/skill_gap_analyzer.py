"""
Skill Gap Analysis & Learning Path Generation Module

This module identifies missing skills and provides personalized learning recommendations
with specific courses, certifications, and learning paths.
"""

import json
import re
from typing import List, Dict, Any

class SkillGapAnalyzer:
    def __init__(self):
        self.learning_resources = {
            # Technical Skills
            "python": {
                "difficulty": "beginner",
                "courses": [
                    {"name": "Python for Everybody Specialization", "provider": "Coursera", "duration": "8 months", "link": "https://coursera.org/specializations/python", "rating": 4.8, "type": "course"},
                    {"name": "Complete Python Bootcamp", "provider": "Udemy", "duration": "22 hours", "link": "https://udemy.com/course/complete-python-bootcamp/", "rating": 4.6, "type": "course"},
                    {"name": "Python Tutorial - Python Full Course for Beginners", "provider": "YouTube - Programming with Mosh", "duration": "6 hours", "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "rating": 4.9, "type": "video"},
                    {"name": "Python Crash Course for Beginners", "provider": "YouTube - Traversy Media", "duration": "1.5 hours", "link": "https://www.youtube.com/watch?v=JJmcL1N2KQs", "rating": 4.8, "type": "video"},
                    {"name": "Python Basics", "provider": "Codecademy", "duration": "25 hours", "link": "https://codecademy.com/learn/learn-python-3", "rating": 4.5, "type": "course"}
                ],
                "certifications": ["Python Institute PCAP", "Microsoft Python Certification"],
                "priority": "high"
            },
            "java": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "Java Programming and Software Engineering Fundamentals", "provider": "Coursera", "duration": "5 months", "link": "https://coursera.org/specializations/java-programming"},
                    {"name": "Java Tutorial for Complete Beginners", "provider": "Udemy", "duration": "16 hours", "link": "https://udemy.com/course/java-tutorial/"}
                ],
                "certifications": ["Oracle Java SE Certification", "Oracle Java EE Certification"],
                "priority": "high"
            },
            "javascript": {
                "difficulty": "beginner",
                "courses": [
                    {"name": "JavaScript Algorithms and Data Structures", "provider": "freeCodeCamp", "duration": "300 hours", "link": "https://freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "rating": 4.8, "type": "course"},
                    {"name": "The Complete JavaScript Course", "provider": "Udemy", "duration": "69 hours", "link": "https://udemy.com/course/the-complete-javascript-course/", "rating": 4.7, "type": "course"},
                    {"name": "JavaScript Crash Course For Beginners", "provider": "YouTube - Traversy Media", "duration": "1.5 hours", "link": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "rating": 4.8, "type": "video"},
                    {"name": "Learn JavaScript - Full Course for Beginners", "provider": "YouTube - freeCodeCamp", "duration": "3.5 hours", "link": "https://www.youtube.com/watch?v=PkZNo7MFNFg", "rating": 4.9, "type": "video"}
                ],
                "certifications": ["JavaScript Developer Certification"],
                "priority": "high"
            },
            "react": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "React - The Complete Guide", "provider": "Udemy", "duration": "48 hours", "link": "https://udemy.com/course/react-the-complete-guide-incl-redux/", "rating": 4.6, "type": "course"},
                    {"name": "React Specialization", "provider": "Coursera", "duration": "4 months", "link": "https://coursera.org/specializations/full-stack-react", "rating": 4.7, "type": "course"},
                    {"name": "React Tutorial for Beginners", "provider": "YouTube - Programming with Mosh", "duration": "2 hours", "link": "https://www.youtube.com/watch?v=Ke90Tje7VS0", "rating": 4.9, "type": "video"},
                    {"name": "React Course - Beginner's Tutorial for React JavaScript Library", "provider": "YouTube - freeCodeCamp", "duration": "12 hours", "link": "https://www.youtube.com/watch?v=bMknfKXIFA8", "rating": 4.8, "type": "video"}
                ],
                "certifications": ["React Developer Certification"],
                "priority": "medium"
            },
            "aws": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "AWS Cloud Practitioner Essentials", "provider": "AWS", "duration": "6 hours", "link": "https://aws.amazon.com/training/course-descriptions/cloud-practitioner-essentials/", "rating": 4.7, "type": "course"},
                    {"name": "AWS Certified Solutions Architect", "provider": "A Cloud Guru", "duration": "20 hours", "link": "https://acloudguru.com/course/aws-certified-solutions-architect-associate-saa-c03", "rating": 4.6, "type": "course"},
                    {"name": "AWS Tutorial for Beginners", "provider": "YouTube - Edureka", "duration": "4 hours", "link": "https://www.youtube.com/watch?v=k1RI5locZE4", "rating": 4.6, "type": "video"},
                    {"name": "AWS Certified Cloud Practitioner Training", "provider": "YouTube - freeCodeCamp", "duration": "4 hours", "link": "https://www.youtube.com/watch?v=3hLmDS179YE", "rating": 4.8, "type": "video"}
                ],
                "certifications": ["AWS Cloud Practitioner", "AWS Solutions Architect Associate", "AWS Developer Associate"],
                "priority": "high"
            },
            "docker": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "Docker and Kubernetes: Complete Guide", "provider": "Udemy", "duration": "21 hours", "link": "https://udemy.com/course/docker-and-kubernetes-the-complete-guide/"},
                    {"name": "Docker Essentials", "provider": "Linux Academy", "duration": "8 hours", "link": "https://linuxacademy.com/course/docker-essentials/"}
                ],
                "certifications": ["Docker Certified Associate"],
                "priority": "medium"
            },
            # Data Science Skills
            "machine learning": {
                "difficulty": "advanced",
                "courses": [
                    {"name": "Machine Learning Specialization", "provider": "Coursera - Stanford", "duration": "3 months", "link": "https://coursera.org/specializations/machine-learning-introduction", "rating": 4.9, "type": "course"},
                    {"name": "Machine Learning A-Z", "provider": "Udemy", "duration": "44 hours", "link": "https://udemy.com/course/machinelearning/", "rating": 4.5, "type": "course"},
                    {"name": "Machine Learning Course - CS229", "provider": "YouTube - Stanford", "duration": "20 hours", "link": "https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU", "rating": 4.9, "type": "video"},
                    {"name": "Machine Learning Explained", "provider": "YouTube - Zach Star", "duration": "1 hour", "link": "https://www.youtube.com/watch?v=ukzFI9rgwfU", "rating": 4.7, "type": "video"}
                ],
                "certifications": ["Google Cloud ML Engineer", "AWS Machine Learning Specialty"],
                "priority": "high"
            },
            "tensorflow": {
                "difficulty": "advanced",
                "courses": [
                    {"name": "TensorFlow Developer Certificate", "provider": "Coursera", "duration": "4 months", "link": "https://coursera.org/professional-certificates/tensorflow-in-practice"},
                    {"name": "Complete TensorFlow 2 and Keras Deep Learning Bootcamp", "provider": "Udemy", "duration": "18 hours", "link": "https://udemy.com/course/complete-tensorflow-2-and-keras-deep-learning-bootcamp/"}
                ],
                "certifications": ["TensorFlow Developer Certificate"],
                "priority": "medium"
            },
            "pandas": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "Data Analysis with Python", "provider": "freeCodeCamp", "duration": "300 hours", "link": "https://freecodecamp.org/learn/data-analysis-with-python/"},
                    {"name": "Pandas & Python for Data Analysis", "provider": "Udemy", "duration": "13 hours", "link": "https://udemy.com/course/data-analysis-with-pandas/"}
                ],
                "certifications": ["Python Data Analysis Certification"],
                "priority": "medium"
            },
            # Marketing Skills
            "google analytics": {
                "difficulty": "beginner",
                "courses": [
                    {"name": "Google Analytics for Beginners", "provider": "Google", "duration": "4 hours", "link": "https://analytics.google.com/analytics/academy/"},
                    {"name": "Google Analytics Masterclass", "provider": "Udemy", "duration": "6 hours", "link": "https://udemy.com/course/google-analytics-masterclass/"}
                ],
                "certifications": ["Google Analytics Individual Qualification", "Google Analytics 4 Certification"],
                "priority": "high"
            },
            "seo": {
                "difficulty": "beginner",
                "courses": [
                    {"name": "SEO Fundamentals Course", "provider": "SEMrush", "duration": "3 hours", "link": "https://semrush.com/academy/", "rating": 4.6, "type": "course"},
                    {"name": "Complete SEO Course", "provider": "Udemy", "duration": "23 hours", "link": "https://udemy.com/course/whiteboard-seo/", "rating": 4.4, "type": "course"},
                    {"name": "Complete SEO Course for Beginners", "provider": "YouTube - Ahrefs", "duration": "2 hours", "link": "https://www.youtube.com/watch?v=xsVTqzratPs", "rating": 4.7, "type": "video"},
                    {"name": "SEO Tutorial for Beginners", "provider": "YouTube - Moz", "duration": "1 hour", "link": "https://www.youtube.com/watch?v=hF515-0Tduk", "rating": 4.5, "type": "video"}
                ],
                "certifications": ["SEMrush SEO Toolkit Certification", "Google Search Console Certification"],
                "priority": "medium"
            },
            # Finance Skills
            "financial modeling": {
                "difficulty": "intermediate",
                "courses": [
                    {"name": "Financial Modeling Specialization", "provider": "Coursera", "duration": "5 months", "link": "https://coursera.org/specializations/financial-modeling"},
                    {"name": "Financial Modeling & Valuation Analyst", "provider": "CFI", "duration": "40 hours", "link": "https://corporatefinanceinstitute.com/certifications/financial-modeling-valuation-analyst-fmva/"}
                ],
                "certifications": ["FMVA - Financial Modeling & Valuation Analyst", "CFA Charter"],
                "priority": "high"
            },
            "excel": {
                "difficulty": "beginner",
                "courses": [
                    {"name": "Excel Skills for Business", "provider": "Coursera", "duration": "6 months", "link": "https://coursera.org/specializations/excel"},
                    {"name": "Microsoft Excel - Advanced Excel Formulas & Functions", "provider": "Udemy", "duration": "7 hours", "link": "https://udemy.com/course/excel-for-analysts/"}
                ],
                "certifications": ["Microsoft Excel Expert Certification", "Microsoft Office Specialist"],
                "priority": "medium"
            }
        }
        
        # Skill categories for better organization
        self.skill_categories = {
            "programming_languages": ["python", "java", "javascript", "c++", "ruby", "go", "rust"],
            "frameworks": ["react", "angular", "vue", "django", "flask", "spring", "node"],
            "databases": ["sql", "mongodb", "postgresql", "mysql", "nosql"],
            "cloud_platforms": ["aws", "azure", "gcp", "cloud"],
            "devops": ["docker", "kubernetes", "git", "ci/cd"],
            "data_science": ["machine learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"],
            "marketing": ["google analytics", "seo", "sem", "social media", "content marketing"],
            "finance": ["financial modeling", "excel", "financial analysis", "accounting"]
        }

    def analyze_skill_gaps(self, found_skills: List[str], required_skills: List[str], job_role: str) -> Dict[str, Any]:
        """
        Analyze skill gaps and generate learning recommendations
        """
        # Normalize skills to lowercase for comparison
        found_skills_lower = [skill.lower() for skill in found_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        # Identify missing skills
        missing_skills = [skill for skill in required_skills_lower if skill not in found_skills_lower]
        
        # Categorize missing skills
        categorized_gaps = self._categorize_missing_skills(missing_skills)
        
        # Generate learning path recommendations
        learning_path = self._generate_learning_path(missing_skills, job_role)
        
        # Calculate gap severity
        gap_severity = self._calculate_gap_severity(missing_skills, required_skills_lower)
        
        return {
            "total_required_skills": len(required_skills_lower),
            "skills_present": len(found_skills_lower),
            "skills_missing": len(missing_skills),
            "skill_match_percentage": round((len(found_skills_lower) / len(required_skills_lower)) * 100, 1),
            "gap_severity": gap_severity,
            "missing_skills_by_category": categorized_gaps,
            "priority_skills_to_learn": self._get_priority_skills(missing_skills),
            "learning_path": learning_path,
            "estimated_learning_time": self._estimate_learning_time(missing_skills),
            "quick_wins": self._identify_quick_wins(missing_skills),
            "career_impact": self._assess_career_impact(missing_skills, job_role)
        }

    def _categorize_missing_skills(self, missing_skills: List[str]) -> Dict[str, List[str]]:
        """Categorize missing skills by type"""
        categorized = {}
        
        for category, skills_in_category in self.skill_categories.items():
            missing_in_category = [skill for skill in missing_skills if skill in skills_in_category]
            if missing_in_category:
                categorized[category] = missing_in_category
        
        # Add uncategorized skills
        all_categorized = []
        for skills in categorized.values():
            all_categorized.extend(skills)
        
        uncategorized = [skill for skill in missing_skills if skill not in all_categorized]
        if uncategorized:
            categorized["other"] = uncategorized
        
        return categorized

    def _generate_learning_path(self, missing_skills: List[str], job_role: str) -> List[Dict[str, Any]]:
        """Generate a structured learning path"""
        learning_path = []
        
        # Sort skills by priority and difficulty
        prioritized_skills = self._prioritize_skills_for_learning(missing_skills)
        
        for i, skill in enumerate(prioritized_skills[:8]):  # Limit to top 8 skills
            if skill in self.learning_resources:
                resource = self.learning_resources[skill]
                
                # Recommend the best course for each skill
                best_course = resource["courses"][0] if resource["courses"] else None
                
                learning_step = {
                    "step": i + 1,
                    "skill": skill,
                    "difficulty": resource["difficulty"],
                    "priority": resource["priority"],
                    "recommended_course": best_course,
                    "recommended_courses": resource["courses"][:3],  # Show top 3 courses including videos
                    "alternative_courses": resource["courses"][1:3],  # Show 2 alternatives
                    "certifications": resource["certifications"],
                    "description": self._get_skill_description(skill, job_role)
                }
                
                learning_path.append(learning_step)
        
        return learning_path

    def _calculate_gap_severity(self, missing_skills: List[str], all_required_skills: List[str]) -> str:
        """Calculate the severity of skill gaps"""
        gap_percentage = (len(missing_skills) / len(all_required_skills)) * 100
        
        if gap_percentage <= 20:
            return "minimal"
        elif gap_percentage <= 40:
            return "moderate"
        elif gap_percentage <= 60:
            return "significant"
        else:
            return "critical"

    def _get_priority_skills(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Get high-priority skills that should be learned first"""
        priority_skills = []
        
        for skill in missing_skills:
            if skill in self.learning_resources:
                resource = self.learning_resources[skill]
                if resource["priority"] == "high":
                    priority_skills.append({
                        "skill": skill,
                        "reason": self._get_priority_reason(skill),
                        "estimated_time": self._extract_duration(resource["courses"][0]["duration"]) if resource["courses"] else "N/A"
                    })
        
        return priority_skills[:5]  # Return top 5 priority skills

    def _estimate_learning_time(self, missing_skills: List[str]) -> Dict[str, Any]:
        """Estimate total learning time for missing skills"""
        total_hours = 0
        skill_times = {}
        
        for skill in missing_skills[:10]:  # Limit to first 10 skills
            if skill in self.learning_resources:
                courses = self.learning_resources[skill]["courses"]
                if courses:
                    duration = self._extract_duration(courses[0]["duration"])
                    total_hours += duration
                    skill_times[skill] = duration
        
        return {
            "total_hours": total_hours,
            "estimated_months": round(total_hours / 40, 1),  # Assuming 10 hours per week
            "skill_breakdown": skill_times
        }

    def _identify_quick_wins(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Identify skills that can be learned quickly for immediate impact"""
        quick_wins = []
        
        for skill in missing_skills:
            if skill in self.learning_resources:
                resource = self.learning_resources[skill]
                if resource["difficulty"] == "beginner" and resource["courses"]:
                    duration = self._extract_duration(resource["courses"][0]["duration"])
                    if duration <= 20:  # Skills that can be learned in 20 hours or less
                        quick_wins.append({
                            "skill": skill,
                            "learning_time": f"{duration} hours",
                            "course": resource["courses"][0]["name"],
                            "provider": resource["courses"][0]["provider"],
                            "impact": "immediate"
                        })
        
        return quick_wins[:3]  # Return top 3 quick wins

    def _assess_career_impact(self, missing_skills: List[str], job_role: str) -> Dict[str, Any]:
        """Assess the career impact of learning missing skills"""
        high_impact_skills = []
        medium_impact_skills = []
        
        for skill in missing_skills:
            if skill in self.learning_resources:
                resource = self.learning_resources[skill]
                if resource["priority"] == "high":
                    high_impact_skills.append(skill)
                else:
                    medium_impact_skills.append(skill)
        
        return {
            "high_impact_skills": high_impact_skills,
            "medium_impact_skills": medium_impact_skills,
            "career_advancement_potential": "high" if len(high_impact_skills) >= 3 else "medium",
            "salary_increase_potential": self._estimate_salary_impact(high_impact_skills, job_role)
        }

    def _prioritize_skills_for_learning(self, missing_skills: List[str]) -> List[str]:
        """Prioritize skills based on difficulty and importance"""
        def skill_priority_score(skill):
            if skill not in self.learning_resources:
                return 0
            
            resource = self.learning_resources[skill]
            priority_score = {"high": 3, "medium": 2, "low": 1}[resource["priority"]]
            difficulty_score = {"beginner": 3, "intermediate": 2, "advanced": 1}[resource["difficulty"]]
            
            return priority_score + difficulty_score
        
        return sorted(missing_skills, key=skill_priority_score, reverse=True)

    def _extract_duration(self, duration_str: str) -> int:
        """Extract duration in hours from duration string"""
        if "hours" in duration_str:
            return int(re.findall(r'\d+', duration_str)[0])
        elif "months" in duration_str:
            months = int(re.findall(r'\d+', duration_str)[0])
            return months * 40  # Assuming 10 hours per week
        else:
            return 10  # Default estimate

    def _get_skill_description(self, skill: str, job_role: str) -> str:
        """Get description for why this skill is important for the job role"""
        descriptions = {
            "python": f"Essential programming language for {job_role}, widely used for automation, data analysis, and web development.",
            "java": f"Popular programming language for enterprise applications and backend development in {job_role} roles.",
            "javascript": f"Critical for frontend development and increasingly important for full-stack {job_role} positions.",
            "react": f"Leading frontend framework that significantly enhances {job_role} marketability.",
            "aws": f"Cloud computing skills are highly demanded in {job_role} positions across all industries.",
            "machine learning": f"Core skill for data-driven {job_role} roles with high salary potential.",
            "google analytics": f"Essential for data-driven decision making in {job_role} positions."
        }
        
        return descriptions.get(skill, f"Important skill for {job_role} professionals to enhance their capabilities.")

    def _get_priority_reason(self, skill: str) -> str:
        """Get reason why this skill is high priority"""
        reasons = {
            "python": "Most in-demand programming language with versatile applications",
            "java": "Enterprise-level programming language with strong job market",
            "aws": "Cloud computing is the future of infrastructure",
            "machine learning": "High-growth field with excellent salary prospects",
            "google analytics": "Data-driven marketing is essential for business success"
        }
        
        return reasons.get(skill, "High-demand skill in current job market")

    def _estimate_salary_impact(self, high_impact_skills: List[str], job_role: str) -> str:
        """Estimate potential salary increase from learning skills"""
        if len(high_impact_skills) >= 4:
            return "15-25% salary increase potential"
        elif len(high_impact_skills) >= 2:
            return "10-15% salary increase potential"
        else:
            return "5-10% salary increase potential"