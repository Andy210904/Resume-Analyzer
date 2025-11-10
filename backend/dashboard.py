from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json
from timezone_utils import format_ist_datetime, get_ist_isoformat, get_ist_now

dashboard_bp = Blueprint('dashboard', __name__)

def get_models():
    """Lazy import models to avoid circular import"""
    from models import db, User, Admin, ResumeAnalysis
    return db, User, Admin, ResumeAnalysis

def _check_bert_status():
    """Check if BERT analyzer is available"""
    try:
        from bert_analyzer import get_bert_analyzer
        analyzer = get_bert_analyzer()
        return analyzer.is_available
    except (ImportError, AttributeError):
        return False

@dashboard_bp.route('/user/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get dashboard statistics for regular users"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        # Ensure it's a regular user, not admin
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access not allowed on user dashboard'}), 403
        
        # Get user's resume analyses
        analyses = ResumeAnalysis.query.filter_by(user_id=current_user.id).all()
        
        # Calculate stats
        total_resumes = len(analyses)
        last_analyzed = None
        overall_score = 0
        score_progression = []
        skill_matches = {}
        top_skills = []
        
        if analyses:
            # Sort by creation date
            analyses_sorted = sorted(analyses, key=lambda x: x.created_at)
            last_analyzed = get_ist_isoformat(analyses_sorted[-1].created_at)
            
            # Calculate average score
            scores = [a.overall_score for a in analyses if a.overall_score]
            overall_score = round(sum(scores) / len(scores)) if scores else 0
            
            # Score progression over time
            for analysis in analyses_sorted:
                if analysis.overall_score:
                    score_progression.append({
                        'date': analysis.created_at.strftime('%Y-%m-%d'),
                        'score': analysis.overall_score,
                        'job_role': analysis.job_role
                    })
            
            # Extract skill information from analyses
            for analysis in analyses:
                if analysis.analysis_results:
                    try:
                        results = json.loads(analysis.analysis_results)
                        # Extract skills from sections
                        if 'sections' in results and 'skills' in results['sections']:
                            skills_section = results['sections']['skills']
                            if skills_section.get('exists'):
                                # This is a simplified skill extraction
                                # In a real scenario, you'd parse the skills more thoroughly
                                skill_matches[analysis.job_role] = skills_section.get('score', 0)
                    except:
                        continue
        
        # Mock some additional data for demo purposes
        recommended_skills = [
            {'skill': 'Python', 'relevance': 95},
            {'skill': 'React', 'relevance': 88},
            {'skill': 'Machine Learning', 'relevance': 82},
            {'skill': 'SQL', 'relevance': 78},
            {'skill': 'AWS', 'relevance': 75}
        ]
        
        stats = {
            'total_resumes': total_resumes,
            'last_analyzed': last_analyzed,
            'overall_score': overall_score,
            'resumes_improved': max(0, total_resumes - 1) if total_resumes > 1 else 0,
            'score_progression': score_progression,
            'skill_matches': skill_matches,
            'recommended_skills': recommended_skills,
            'ats_compatibility': min(95, overall_score + 10) if overall_score else 75,
            'bert_available': _check_bert_status()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/user/insights', methods=['GET'])
@login_required
def get_user_insights():
    """Get AI-generated insights for the user"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access not allowed on user dashboard'}), 403
        
        # Get latest analysis
        latest_analysis = ResumeAnalysis.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(ResumeAnalysis.created_at)).first()
        
        insights = {
            'summary': 'Your resume shows strong technical skills and relevant experience.',
            'strengths': [
                'Well-structured format',
                'Strong technical skills section',
                'Relevant work experience'
            ],
            'improvements': [
                'Add more quantifiable achievements',
                'Include industry-specific keywords',
                'Consider adding a professional summary'
            ],
            'recommended_jobs': [
                'Software Developer',
                'Full Stack Engineer',
                'Data Analyst',
                'Machine Learning Engineer'
            ]
        }
        
        if latest_analysis and latest_analysis.analysis_results:
            try:
                results = json.loads(latest_analysis.analysis_results)
                if 'suggestions' in results:
                    insights['improvements'] = results['suggestions'][:5]
                if 'strengths' in results:
                    insights['strengths'] = results['strengths'][:5]
            except:
                pass
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/admin/stats', methods=['GET'])
@login_required
def get_admin_stats():
    """Get dashboard statistics for admins"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        # Ensure it's an admin user
        if not isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get system-wide statistics
        total_users = User.query.count()
        total_analyses = ResumeAnalysis.query.count()
        
        # Calculate average score
        avg_score_result = db.session.query(func.avg(ResumeAnalysis.overall_score)).filter(
            ResumeAnalysis.overall_score.isnot(None)
        ).scalar()
        avg_score = round(avg_score_result) if avg_score_result else 0
        
        # Active users today (users who logged in today)
        today = get_ist_now().date()
        active_today = User.query.filter(
            func.date(User.last_login) == today
        ).count()
        
        # Score distribution
        score_ranges = [
            {'range': '0-20', 'count': 0},
            {'range': '21-40', 'count': 0},
            {'range': '41-60', 'count': 0},
            {'range': '61-80', 'count': 0},
            {'range': '81-100', 'count': 0}
        ]
        
        analyses_with_scores = ResumeAnalysis.query.filter(
            ResumeAnalysis.overall_score.isnot(None)
        ).all()
        
        for analysis in analyses_with_scores:
            score = analysis.overall_score
            if score <= 20:
                score_ranges[0]['count'] += 1
            elif score <= 40:
                score_ranges[1]['count'] += 1
            elif score <= 60:
                score_ranges[2]['count'] += 1
            elif score <= 80:
                score_ranges[3]['count'] += 1
            else:
                score_ranges[4]['count'] += 1
        
        # Upload trend (last 7 days)
        upload_trend = []
        for i in range(7):
            date = get_ist_now().date() - timedelta(days=i)
            count = ResumeAnalysis.query.filter(
                func.date(ResumeAnalysis.created_at) == date
            ).count()
            upload_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        upload_trend.reverse()
        
        # Top skills (mock data for now)
        top_skills = [
            {'skill': 'Python', 'count': 45},
            {'skill': 'JavaScript', 'count': 38},
            {'skill': 'React', 'count': 32},
            {'skill': 'SQL', 'count': 28},
            {'skill': 'Java', 'count': 25},
            {'skill': 'AWS', 'count': 22},
            {'skill': 'Machine Learning', 'count': 20},
            {'skill': 'Docker', 'count': 18},
            {'skill': 'Git', 'count': 16},
            {'skill': 'Node.js', 'count': 14}
        ]
        
        # Domain distribution (mock data)
        domain_distribution = [
            {'domain': 'Software Development', 'count': 25},
            {'domain': 'Data Science', 'count': 18},
            {'domain': 'DevOps', 'count': 12},
            {'domain': 'UI/UX Design', 'count': 8},
            {'domain': 'Product Management', 'count': 5}
        ]
        
        stats = {
            'total_users': total_users,
            'total_analyses': total_analyses,
            'avg_score': avg_score,
            'active_today': active_today,
            'score_distribution': score_ranges,
            'upload_trend': upload_trend,
            'top_skills': top_skills,
            'domain_distribution': domain_distribution
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/admin/users', methods=['GET'])
@login_required
def get_all_users():
    """Get all users with their statistics for admin dashboard"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        if not isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get users with pagination
        users_query = User.query.order_by(desc(User.created_at))
        users_paginated = users_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users_data = []
        for user in users_paginated.items:
            # Get user's resume analyses
            analyses = ResumeAnalysis.query.filter_by(user_id=user.id).all()
            
            # Calculate average score
            scores = [a.overall_score for a in analyses if a.overall_score]
            avg_score = round(sum(scores) / len(scores)) if scores else 0
            
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name(),
                'created_at': get_ist_isoformat(user.created_at),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'resume_count': len(analyses),
                'avg_score': avg_score,
                'last_analysis': get_ist_isoformat(analyses[-1].created_at) if analyses else None
            }
            users_data.append(user_data)
        
        return jsonify({
            'users': users_data,
            'total': users_paginated.total,
            'pages': users_paginated.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/user/analyses', methods=['GET'])
@login_required
def get_user_analyses():
    """Return a paginated list of the current user's past analyses"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()

        # Ensure regular user
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access not allowed on user analyses'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = ResumeAnalysis.query.filter_by(user_id=current_user.id).order_by(ResumeAnalysis.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        analyses = [a.to_dict() for a in paginated.items]

        return jsonify({
            'analyses': analyses,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/user/analyses/<int:analysis_id>', methods=['GET'])
@login_required
def get_user_analysis(analysis_id):
    """Get a single analysis details for the current user"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()

        # Ensure regular user
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access not allowed on user analyses'}), 403

        analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found or access denied'}), 404

        return jsonify({'analysis': analysis.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/user/analyses/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_user_analysis(analysis_id):
    """Delete a specific analysis for the current user"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()

        # Ensure regular user
        if isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access not allowed on user analyses'}), 403

        # Find the analysis
        analysis = ResumeAnalysis.query.filter_by(
            id=analysis_id, 
            user_id=current_user.id
        ).first()

        if not analysis:
            return jsonify({'error': 'Analysis not found or access denied'}), 404

        # Store filename for response
        filename = analysis.filename

        # Delete the analysis
        db.session.delete(analysis)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Analysis for "{filename}" deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500