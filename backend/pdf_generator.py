from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
import json
from datetime import datetime
import io

class ResumeReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#34495e'),
            borderWidth=1,
            borderColor=HexColor('#bdc3c7'),
            borderPadding=8,
            backColor=HexColor('#ecf0f1')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=HexColor('#27ae60'),
            alignment=1,
            spaceAfter=20
        ))
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 80:
            return HexColor('#27ae60')  # Green
        elif score >= 60:
            return HexColor('#f39c12')  # Orange
        else:
            return HexColor('#e74c3c')  # Red
    
    def _create_score_chart(self, overall_score, industry_score=None):
        """Create a simple bar chart for scores"""
        drawing = Drawing(400, 200)
        
        # Create bar chart
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        
        # Data
        if industry_score is not None:
            chart.data = [[overall_score, industry_score]]
            chart.categoryAxis.categoryNames = ['Overall Score', 'Industry Score']
        else:
            chart.data = [[overall_score]]
            chart.categoryAxis.categoryNames = ['Overall Score']
        
        # Styling
        chart.bars[0].fillColor = self._get_score_color(overall_score)
        if industry_score is not None and len(chart.bars) > 1:
            chart.bars[1].fillColor = self._get_score_color(industry_score)
        
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueMin = 0
        
        drawing.add(chart)
        return drawing
    
    def _create_section_table(self, sections):
        """Create a table showing section scores"""
        if not sections:
            return None
        
        data = [['Section', 'Status', 'Score', 'Feedback']]
        
        for section_name, section_data in sections.items():
            status = "✓ Present" if section_data.get('exists', False) else "✗ Missing"
            score = f"{section_data.get('score', 0)}%" if section_data.get('exists', False) else "N/A"
            feedback = '; '.join(section_data.get('feedback', [])[:2])  # First 2 feedback items
            if len(feedback) > 80:
                feedback = feedback[:80] + "..."
            
            data.append([
                section_name.title(),
                status,
                score,
                feedback
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1*inch, 0.8*inch, 3.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        
        return table
    
    def _create_industry_analysis_table(self, industry_analysis):
        """Create table for industry analysis details"""
        if not industry_analysis:
            return None
        
        data = [['Analysis Type', 'Score', 'Details']]
        
        # Skills Analysis
        if 'skills_analysis' in industry_analysis:
            skills = industry_analysis['skills_analysis']
            found_count = len(skills.get('found_skills', []))
            missing_count = len(skills.get('missing_important_skills', []))
            details = f"Found: {found_count} skills, Missing: {missing_count} important skills"
            data.append(['Skills Match', f"{skills.get('score', 0)}%", details])
        
        # Sections Analysis
        if 'sections_analysis' in industry_analysis:
            sections = industry_analysis['sections_analysis']
            found_sections = len(sections.get('found_sections', []))
            missing_sections = len(sections.get('missing_sections', []))
            details = f"Present: {found_sections}, Missing: {missing_sections} sections"
            data.append(['Resume Sections', f"{sections.get('score', 0)}%", details])
        
        # Action Verbs
        if 'verbs_analysis' in industry_analysis:
            verbs = industry_analysis['verbs_analysis']
            found_verbs = len(verbs.get('found_verbs', []))
            details = f"Found {found_verbs} strong action verbs"
            data.append(['Action Verbs', f"{verbs.get('score', 0)}%", details])
        
        # Achievements
        if 'achievements_analysis' in industry_analysis:
            achievements = industry_analysis['achievements_analysis']
            found_achievements = len(achievements.get('achievement_phrases_found', []))
            details = f"Found {found_achievements} achievement keywords"
            data.append(['Achievements', f"{achievements.get('score', 0)}%", details])
        
        if len(data) == 1:  # Only header
            return None
        
        table = Table(data, colWidths=[2*inch, 1*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8e44ad')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        
        return table
    
    def generate_report(self, analysis_data, output_buffer):
        """Generate PDF report and write to buffer"""
        # Parse analysis results if it's a string
        if isinstance(analysis_data.get('analysis_results'), str):
            analysis_results = json.loads(analysis_data['analysis_results'])
        else:
            analysis_results = analysis_data.get('analysis_results', {})
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        story = []
        
        # Title
        title = Paragraph("Resume Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Basic Information
        info_data = [
            ['File Name:', analysis_data.get('filename', 'N/A')],
            ['Job Role:', analysis_data.get('job_role', 'General')],
            ['Analysis Date:', datetime.fromisoformat(analysis_data.get('created_at', datetime.now().isoformat())).strftime('%B %d, %Y at %I:%M %p')],
            ['Word Count:', str(analysis_data.get('word_count', 'N/A'))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#ecf0f1')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Overall Scores Section
        story.append(Paragraph("Overall Scores", self.styles['SectionHeader']))
        
        overall_score = analysis_data.get('overall_score', 0)
        industry_score = analysis_data.get('industry_score')
        
        # Score paragraph
        score_text = f"<font color='{self._get_score_color(overall_score).hexval()}' size='36'><b>{overall_score}</b></font>/100"
        if industry_score is not None:
            score_text += f"<br/><font size='14'>Industry Score: </font><font color='{self._get_score_color(industry_score).hexval()}' size='24'><b>{industry_score}</b></font>/100"
        
        story.append(Paragraph(score_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Section Analysis
        if analysis_results.get('sections'):
            story.append(Paragraph("Section Analysis", self.styles['SectionHeader']))
            section_table = self._create_section_table(analysis_results['sections'])
            if section_table:
                story.append(section_table)
                story.append(Spacer(1, 20))
        
        # Industry Analysis
        if analysis_results.get('industry_analysis'):
            story.append(Paragraph(f"Industry Analysis - {analysis_data.get('job_role', 'Unknown').title()}", self.styles['SectionHeader']))
            industry_table = self._create_industry_analysis_table(analysis_results['industry_analysis'])
            if industry_table:
                story.append(industry_table)
                story.append(Spacer(1, 20))
            
            # Industry Suggestions
            suggestions = analysis_results['industry_analysis'].get('suggestions', [])
            if suggestions:
                story.append(Paragraph("Industry-Specific Recommendations", self.styles['SectionHeader']))
                for i, suggestion in enumerate(suggestions[:5], 1):  # Limit to 5 suggestions
                    story.append(Paragraph(f"{i}. {suggestion}", self.styles['Normal']))
                story.append(Spacer(1, 15))
        
        # General Suggestions
        if analysis_results.get('suggestions'):
            story.append(Paragraph("General Suggestions", self.styles['SectionHeader']))
            for i, suggestion in enumerate(analysis_results['suggestions'][:5], 1):  # Limit to 5 suggestions
                story.append(Paragraph(f"{i}. {suggestion}", self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Strengths
        if analysis_results.get('strengths'):
            story.append(Paragraph("Identified Strengths", self.styles['SectionHeader']))
            for i, strength in enumerate(analysis_results['strengths'][:5], 1):  # Limit to 5 strengths
                story.append(Paragraph(f"• {strength}", self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} by IntelliResume</i>"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return output_buffer