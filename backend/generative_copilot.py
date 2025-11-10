"""
Generative Co-Pilot Module for AI Resume Enhancement

This module provides advanced generative AI capabilities for personalized resume improvement.
Features include bullet point rewriting, impact enhancement, and personalized recommendations.

Author: IntelliResume Team
Date: November 2025
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import random

# Optional imports - will gracefully degrade if not available
GENERATIVE_AI_AVAILABLE = False
transformers = None
torch = None

try:
    import torch
    from transformers import (
        T5ForConditionalGeneration, T5Tokenizer,
        GPT2LMHeadModel, GPT2Tokenizer,
        pipeline
    )
    
    GENERATIVE_AI_AVAILABLE = True
    print("Generative AI modules loaded successfully")
    
except (ImportError, ValueError, ModuleNotFoundError) as e:
    GENERATIVE_AI_AVAILABLE = False
    print(f"Generative AI modules not available: {e}")
    print("Install with: pip install transformers torch")

@dataclass
class BulletPointAnalysis:
    """Data class for bullet point analysis results"""
    original_text: str
    classification: str  # "responsibility-driven", "achievement-driven", "mixed"
    impact_score: float  # 0.0 to 1.0
    weakness_reasons: List[str]
    suggested_improvements: List[str]
    ai_rewrite: str
    confidence: float

class GenerativeCopilot:
    """
    Advanced AI-powered resume enhancement using generative models
    """
    
    def __init__(self):
        """Initialize the Generative Co-pilot with AI models"""
        self.is_available = GENERATIVE_AI_AVAILABLE
        
        if not GENERATIVE_AI_AVAILABLE:
            print("Warning: Generative Co-pilot initialized but transformers not available")
            return
        
        try:
            # Initialize models
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {self.device}")
            
            # T5 model for text-to-text generation (bullet point rewriting)
            self.t5_model_name = "t5-small"  # Using smaller model for faster inference
            self.t5_tokenizer = T5Tokenizer.from_pretrained(self.t5_model_name)
            self.t5_model = T5ForConditionalGeneration.from_pretrained(self.t5_model_name)
            self.t5_model.to(self.device)
            
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text2text-generation",
                model=self.t5_model,
                tokenizer=self.t5_tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                max_length=150,
                do_sample=True,
                temperature=0.7
            )
            
            # Load enhancement templates and patterns
            self._load_enhancement_patterns()
            
            print("Generative Co-pilot initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Generative AI models: {e}")
            self.is_available = False
    
    def _load_enhancement_patterns(self):
        """Load patterns and templates for bullet point enhancement"""
        
        # Weakness detection patterns
        self.weakness_patterns = {
            "responsibility_driven": [
                r"\b(responsible for|in charge of|tasked with|assigned to)\b",
                r"\b(duties included|job involved|work included)\b",
                r"\b(was|were)\s+\w+ing\b",  # passive voice
                r"\b(helped|assisted|supported)\b"  # vague helping verbs
            ],
            "vague_language": [
                r"\b(various|several|many|some|multiple)\b",
                r"\b(stuff|things|items|activities)\b",
                r"\b(good|nice|great|awesome)\b"  # subjective adjectives
            ],
            "missing_metrics": [
                r"^(?!.*\d+[%$]?)(?!.*\b\d+\s*(percent|million|thousand|hours|days|weeks|months|years)\b).*$"
            ]
        }
        
        # Impact enhancement templates
        self.enhancement_templates = {
            "software_engineer": [
                "Developed {technology} application that {impact_metric}",
                "Implemented {technical_solution} resulting in {performance_improvement}",
                "Architected {system_component} that reduced {problem} by {percentage}",
                "Optimized {technical_area} leading to {quantified_benefit}",
                "Built {product_feature} using {tech_stack}, improving {metric} by {amount}"
            ],
            "data_scientist": [
                "Analyzed {data_type} data to identify {insight} resulting in {business_impact}",
                "Developed {ml_model} that improved {metric} by {percentage}",
                "Created {visualization/dashboard} that enabled {decision_outcome}",
                "Processed {data_volume} of data using {tools} to {achievement}",
                "Implemented {algorithm} that reduced {problem} by {quantified_result}"
            ],
            "marketing": [
                "Launched {campaign_type} campaign that generated {result_metric}",
                "Increased {marketing_metric} by {percentage} through {strategy}",
                "Managed {channel/platform} resulting in {engagement_improvement}",
                "Created {content_type} that drove {quantified_outcome}",
                "Optimized {marketing_process} leading to {cost_saving} cost reduction"
            ],
            "finance": [
                "Analyzed {financial_area} data resulting in {cost_saving} savings",
                "Managed portfolio worth ${amount} with {performance_metric} returns",
                "Reduced {expense_category} by {percentage} through {method}",
                "Forecasted {financial_metric} with {accuracy_percentage} accuracy",
                "Streamlined {process} resulting in {time_saving} time reduction"
            ]
        }
        
        # Action verbs by industry
        self.strong_action_verbs = {
            "software_engineer": [
                "architected", "engineered", "developed", "implemented", "optimized",
                "deployed", "automated", "integrated", "refactored", "debugged",
                "scaled", "designed", "built", "launched", "maintained"
            ],
            "data_scientist": [
                "analyzed", "modeled", "predicted", "visualized", "discovered",
                "interpreted", "extracted", "processed", "identified", "forecasted",
                "segmented", "clustered", "classified", "validated", "optimized"
            ],
            "marketing": [
                "launched", "increased", "generated", "grew", "expanded",
                "acquired", "converted", "engaged", "promoted", "amplified",
                "optimized", "targeted", "influenced", "drove", "boosted"
            ],
            "finance": [
                "analyzed", "forecasted", "managed", "allocated", "optimized",
                "reduced", "saved", "improved", "streamlined", "evaluated",
                "assessed", "calculated", "projected", "monitored", "audited"
            ]
        }
    
    def analyze_bullet_points(self, resume_text: str, job_role: str = "software_engineer") -> List[BulletPointAnalysis]:
        """
        Analyze resume bullet points and identify areas for improvement
        """
        if not self.is_available:
            return self._fallback_bullet_analysis(resume_text, job_role)
        
        try:
            # Extract bullet points from resume text
            bullet_points = self._extract_bullet_points(resume_text)
            
            analyses = []
            for bullet in bullet_points:
                analysis = self._analyze_single_bullet_point(bullet, job_role)
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            print(f"Error in bullet point analysis: {e}")
            return self._fallback_bullet_analysis(resume_text, job_role)
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from resume text"""
        # Look for lines that start with bullet point indicators
        bullet_patterns = [
            r'^\s*[•▪▫‣⁃]\s*(.+)$',  # Unicode bullets
            r'^\s*[-*+]\s*(.+)$',     # ASCII bullets
            r'^\s*\d+\.\s*(.+)$',     # Numbered lists
            r'^\s*[►▸▶]\s*(.+)$'      # Arrow bullets
        ]
        
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 10 or len(line) > 200:  # Skip very short or very long lines
                continue
                
            for pattern in bullet_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    bullet_text = match.group(1).strip()
                    if len(bullet_text) > 15:  # Ensure meaningful content
                        bullet_points.append(bullet_text)
                    break
        
        # If no bullets found, try to extract sentences from experience sections
        if not bullet_points:
            bullet_points = self._extract_sentences_from_experience(text)
        
        return bullet_points[:10]  # Limit to first 10 bullets
    
    def _extract_sentences_from_experience(self, text: str) -> List[str]:
        """Extract sentences from experience sections when no bullets are found"""
        # Look for experience-related sections
        experience_patterns = [
            r'(?i)(experience|work history|employment|career|professional background)(.*?)(?=education|skills|projects|$)',
            r'(?i)(software engineer|developer|analyst|manager|specialist)(.*?)(?=education|skills|projects|$)'
        ]
        
        sentences = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                content = match[1] if len(match) > 1 else match[0]
                # Split into sentences
                content_sentences = re.split(r'[.!?]+', content)
                for sentence in content_sentences:
                    sentence = sentence.strip()
                    if 20 <= len(sentence) <= 150:  # Reasonable sentence length
                        sentences.append(sentence)
        
        return sentences[:8]  # Limit to 8 sentences
    
    def _analyze_single_bullet_point(self, bullet_text: str, job_role: str) -> BulletPointAnalysis:
        """Analyze a single bullet point for weaknesses and generate improvements"""
        
        # Classify the bullet point
        classification = self._classify_bullet_point(bullet_text)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(bullet_text)
        
        # Identify weaknesses
        weakness_reasons = self._identify_weaknesses(bullet_text)
        
        # Generate AI rewrite
        ai_rewrite = self._generate_ai_rewrite(bullet_text, job_role, weakness_reasons)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(bullet_text, job_role, weakness_reasons)
        
        # Calculate confidence
        confidence = self._calculate_confidence(bullet_text, weakness_reasons)
        
        return BulletPointAnalysis(
            original_text=bullet_text,
            classification=classification,
            impact_score=impact_score,
            weakness_reasons=weakness_reasons,
            suggested_improvements=suggestions,
            ai_rewrite=ai_rewrite,
            confidence=confidence
        )
    
    def _classify_bullet_point(self, text: str) -> str:
        """Classify bullet point as responsibility-driven, achievement-driven, or mixed"""
        text_lower = text.lower()
        
        responsibility_score = 0
        achievement_score = 0
        
        # Check for responsibility patterns
        for pattern in self.weakness_patterns["responsibility_driven"]:
            if re.search(pattern, text_lower):
                responsibility_score += 1
        
        # Check for achievement indicators
        achievement_indicators = [
            r'\b\d+%\b',  # percentages
            r'\b\$\d+\b',  # dollar amounts
            r'\b(increased|improved|reduced|grew|generated|saved|achieved)\b',
            r'\b\d+\s*(million|thousand|hours|days|weeks|months|years)\b'
        ]
        
        for pattern in achievement_indicators:
            if re.search(pattern, text_lower):
                achievement_score += 1
        
        if responsibility_score > achievement_score:
            return "responsibility-driven"
        elif achievement_score > responsibility_score:
            return "achievement-driven"
        else:
            return "mixed"
    
    def _calculate_impact_score(self, text: str) -> float:
        """Calculate the impact score of a bullet point (0.0 to 1.0)"""
        score = 0.5  # baseline
        text_lower = text.lower()
        
        # Positive indicators
        if re.search(r'\b\d+%\b', text):  # Has percentages
            score += 0.2
        if re.search(r'\b\$\d+\b', text):  # Has dollar amounts
            score += 0.2
        if re.search(r'\b(led|managed|developed|created|built|implemented)\b', text_lower):
            score += 0.1
        if re.search(r'\b\d+\s*(users|customers|projects|systems|applications)\b', text_lower):
            score += 0.15
        
        # Negative indicators
        if re.search(r'\b(responsible for|assisted|helped)\b', text_lower):
            score -= 0.2
        if re.search(r'\b(various|several|many|some)\b', text_lower):
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _identify_weaknesses(self, text: str) -> List[str]:
        """Identify specific weaknesses in the bullet point"""
        weaknesses = []
        text_lower = text.lower()
        
        # Check for responsibility-driven language
        for pattern in self.weakness_patterns["responsibility_driven"]:
            if re.search(pattern, text_lower):
                weaknesses.append("Uses passive, responsibility-focused language")
                break
        
        # Check for vague language
        for pattern in self.weakness_patterns["vague_language"]:
            if re.search(pattern, text_lower):
                weaknesses.append("Contains vague, non-specific terms")
                break
        
        # Check for missing metrics
        if not re.search(r'\d+[%$]?', text) and not re.search(r'\b\d+\s*(percent|million|thousand|hours|days|weeks|months|years)\b', text_lower):
            weaknesses.append("Lacks quantifiable metrics or results")
        
        # Check for weak action verbs
        weak_verbs = ["was", "were", "did", "had", "got", "made", "worked", "helped", "assisted"]
        if any(verb in text_lower.split()[:3] for verb in weak_verbs):
            weaknesses.append("Starts with weak or passive action verbs")
        
        return weaknesses
    
    def _generate_ai_rewrite(self, text: str, job_role: str, weaknesses: List[str]) -> str:
        """Generate AI-powered rewrite of the bullet point"""
        if not self.is_available:
            return self._fallback_rewrite(text, job_role, weaknesses)
        
        try:
            # Create a prompt for T5 model
            prompt = f"rewrite this resume bullet point to be more impactful and achievement-focused: {text}"
            
            # Generate rewrite using T5 model
            result = self.text_generator(
                prompt,
                max_length=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            ai_rewrite = result[0]['generated_text'].strip()
            
            # Post-process the rewrite
            ai_rewrite = self._post_process_rewrite(ai_rewrite, job_role)
            
            return ai_rewrite
            
        except Exception as e:
            print(f"Error in AI rewrite generation: {e}")
            return self._fallback_rewrite(text, job_role, weaknesses)
    
    def _post_process_rewrite(self, rewrite: str, job_role: str) -> str:
        """Post-process the AI-generated rewrite"""
        # Ensure it starts with a strong action verb
        strong_verbs = self.strong_action_verbs.get(job_role, self.strong_action_verbs["software_engineer"])
        
        words = rewrite.split()
        if words and words[0].lower() not in [verb.lower() for verb in strong_verbs]:
            # Replace first word with a strong verb if it's weak
            suggested_verb = random.choice(strong_verbs)
            rewrite = f"{suggested_verb.title()} " + " ".join(words[1:])
        
        # Ensure proper capitalization
        rewrite = rewrite[0].upper() + rewrite[1:] if rewrite else rewrite
        
        # Remove redundant periods
        rewrite = rewrite.rstrip('.')
        
        return rewrite
    
    def _generate_improvement_suggestions(self, text: str, job_role: str, weaknesses: List[str]) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        for weakness in weaknesses:
            if "passive, responsibility-focused" in weakness:
                suggestions.append("Start with a strong action verb like 'Led', 'Developed', or 'Implemented'")
            elif "vague, non-specific" in weakness:
                suggestions.append("Replace vague terms with specific technologies, quantities, or outcomes")
            elif "lacks quantifiable metrics" in weakness:
                suggestions.append("Add numbers, percentages, or timeframes to show measurable impact")
            elif "weak or passive action verbs" in weakness:
                strong_verbs = self.strong_action_verbs.get(job_role, self.strong_action_verbs["software_engineer"])
                suggestions.append(f"Use stronger action verbs like: {', '.join(strong_verbs[:5])}")
        
        # Add role-specific suggestions
        if job_role == "software_engineer":
            suggestions.append("Include specific technologies, frameworks, or programming languages used")
            suggestions.append("Mention performance improvements, user impact, or system scalability")
        elif job_role == "data_scientist":
            suggestions.append("Specify data size, model accuracy, or business impact of insights")
            suggestions.append("Mention tools used (Python, R, SQL) and analysis methods")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _calculate_confidence(self, text: str, weaknesses: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = 0.8
        
        # Reduce confidence based on number of weaknesses
        confidence = base_confidence - (len(weaknesses) * 0.1)
        
        # Adjust based on text length and quality
        if len(text) < 20:
            confidence -= 0.2
        elif len(text) > 100:
            confidence += 0.1
        
        return max(0.3, min(1.0, confidence))
    
    def _fallback_bullet_analysis(self, resume_text: str, job_role: str) -> List[BulletPointAnalysis]:
        """Fallback analysis when AI models are not available"""
        bullet_points = self._extract_bullet_points(resume_text)
        
        analyses = []
        for bullet in bullet_points:
            # Simple rule-based analysis
            classification = self._classify_bullet_point(bullet)
            impact_score = self._calculate_impact_score(bullet)
            weaknesses = self._identify_weaknesses(bullet)
            suggestions = self._generate_improvement_suggestions(bullet, job_role, weaknesses)
            ai_rewrite = self._fallback_rewrite(bullet, job_role, weaknesses)
            confidence = 0.7  # Lower confidence for fallback
            
            analyses.append(BulletPointAnalysis(
                original_text=bullet,
                classification=classification,
                impact_score=impact_score,
                weakness_reasons=weaknesses,
                suggested_improvements=suggestions,
                ai_rewrite=ai_rewrite,
                confidence=confidence
            ))
        
        return analyses
    
    def _fallback_rewrite(self, text: str, job_role: str, weaknesses: List[str]) -> str:
        """Fallback rewrite using templates when AI is not available"""
        # Use templates to create a better version
        strong_verbs = self.strong_action_verbs.get(job_role, self.strong_action_verbs["software_engineer"])
        
        # Simple template-based rewrite
        words = text.split()
        if words:
            # Replace first word with strong action verb
            suggested_verb = random.choice(strong_verbs)
            template_rewrite = f"{suggested_verb.title()} {' '.join(words[1:])}"
            
            # Add placeholder for metrics if missing
            if "lacks quantifiable metrics" in str(weaknesses):
                template_rewrite += " [Add specific metrics like percentages, dollar amounts, or timeframes]"
            
            return template_rewrite
        
        return text

# Global function for external access
def analyze_bullet_points_with_ai(resume_text: str, job_role: str = "software_engineer") -> Dict[str, Any]:
    """
    Main function to analyze bullet points and provide AI-powered improvements
    """
    copilot = GenerativeCopilot()
    
    if not copilot.is_available:
        return {
            "available": False,
            "message": "Generative AI features not available. Install transformers and torch.",
            "bullet_analyses": []
        }
    
    analyses = copilot.analyze_bullet_points(resume_text, job_role)
    
    # Convert to serializable format
    result = {
        "available": True,
        "total_bullets_analyzed": len(analyses),
        "responsibility_driven_count": len([a for a in analyses if a.classification == "responsibility-driven"]),
        "bullet_analyses": [
            {
                "original_text": analysis.original_text,
                "classification": analysis.classification,
                "impact_score": round(analysis.impact_score, 2),
                "weakness_reasons": analysis.weakness_reasons,
                "suggested_improvements": analysis.suggested_improvements,
                "ai_rewrite": analysis.ai_rewrite,
                "confidence": round(analysis.confidence, 2)
            }
            for analysis in analyses
        ]
    }
    
    return result

# Test function
def test_generative_copilot():
    """Test the generative copilot functionality"""
    sample_resume = """
    Experience:
    • Was responsible for developing the company website
    • Helped with various database tasks and stuff
    • Worked on several projects using different technologies
    • Managed team meetings and coordination activities
    • Assisted in testing and debugging applications
    """
    
    result = analyze_bullet_points_with_ai(sample_resume, "software_engineer")
    
    print("=== Generative Co-pilot Test Results ===")
    print(f"Available: {result['available']}")
    if result['available']:
        print(f"Bullets analyzed: {result['total_bullets_analyzed']}")
        print(f"Responsibility-driven bullets: {result['responsibility_driven_count']}")
        
        for i, analysis in enumerate(result['bullet_analyses'][:3], 1):
            print(f"\n--- Bullet Point {i} ---")
            print(f"Original: {analysis['original_text']}")
            print(f"Classification: {analysis['classification']}")
            print(f"Impact Score: {analysis['impact_score']}")
            print(f"Weaknesses: {', '.join(analysis['weakness_reasons'])}")
            print(f"AI Rewrite: {analysis['ai_rewrite']}")
    
    return result

if __name__ == "__main__":
    test_generative_copilot()