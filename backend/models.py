from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from timezone_utils import format_ist_datetime, get_ist_isoformat

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for regular users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with resume analyses
    resume_analyses = db.relationship('ResumeAnalysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'created_at': get_ist_isoformat(self.created_at),
            'last_login': get_ist_isoformat(self.last_login),
            'total_analyses': len(self.resume_analyses)
        }

class Admin(UserMixin, db.Model):
    """Admin model for administrative users"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return the full name of the admin"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert admin object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'is_super_admin': self.is_super_admin,
            'created_at': get_ist_isoformat(self.created_at),
            'last_login': get_ist_isoformat(self.last_login)
        }

class ResumeAnalysis(db.Model):
    """Model to store resume analysis results"""
    __tablename__ = 'resume_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # File size in bytes
    job_role = db.Column(db.String(100), nullable=False)
    overall_score = db.Column(db.Integer)
    industry_score = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Analysis results stored as JSON text
    analysis_results = db.Column(db.Text)  # JSON string of complete analysis
    suggestions = db.Column(db.Text)  # JSON string of suggestions
    strengths = db.Column(db.Text)  # JSON string of strengths
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert analysis object to dictionary"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'job_role': self.job_role,
            'overall_score': self.overall_score,
            'industry_score': self.industry_score,
            'word_count': self.word_count,
            'analysis_results': json.loads(self.analysis_results) if self.analysis_results else None,
            'suggestions': json.loads(self.suggestions) if self.suggestions else None,
            'strengths': json.loads(self.strengths) if self.strengths else None,
            'created_at': get_ist_isoformat(self.created_at),
            'user': {
                'username': self.user.username,
                'full_name': self.user.get_full_name()
            }
        }