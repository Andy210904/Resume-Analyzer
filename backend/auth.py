from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import re
from timezone_utils import get_ist_isoformat, get_ist_now

auth_bp = Blueprint('auth', __name__)

def get_models():
    """Lazy import models to avoid circular import"""
    from models import db, User, Admin, ResumeAnalysis
    return db, User, Admin, ResumeAnalysis

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Split full_name into first_name and last_name
        full_name_parts = data['full_name'].strip().split()
        if len(full_name_parts) < 2:
            return jsonify({'error': 'Please provide both first and last name'}), 400
        first_name = full_name_parts[0]
        last_name = ' '.join(full_name_parts[1:])  # Handle middle names
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(data['password'])  # Hash the password using the model method
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) |
            (User.email == data['username'])
        ).first()
        
        if user and user.check_password(data['password']):
            from flask import session
            login_user(user, remember=True)  # Always remember users for convenience
            session.permanent = True  # Make session permanent (uses PERMANENT_SESSION_LIFETIME)
            user.last_login = datetime.utcnow()  # Keep UTC in database
            db.session.commit()
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'is_admin': False
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find admin by username or email
        admin = Admin.query.filter(
            (Admin.username == data['username']) |
            (Admin.email == data['username'])
        ).first()
        
        if admin and admin.check_password(data['password']):
            from flask import session
            login_user(admin, remember=True)  # Always remember admins for convenience
            session.permanent = True  # Make session permanent (uses PERMANENT_SESSION_LIFETIME)
            admin.last_login = datetime.utcnow()  # Keep UTC in database
            db.session.commit()
            
            return jsonify({
                'message': 'Admin login successful',
                'user': {
                    'id': admin.id,
                    'username': admin.username,
                    'email': admin.email,
                    'full_name': admin.get_full_name(),
                    'is_admin': True
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.get_full_name(),
            'phone': getattr(current_user, 'phone', ''),
            'bio': getattr(current_user, 'bio', ''),
            'created_at': get_ist_isoformat(current_user.created_at),
            'last_login': get_ist_isoformat(current_user.last_login),
            'is_admin': isinstance(current_user, Admin)
        }
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already exists'}), 400
            current_user.email = data['email']
        if 'phone' in data and hasattr(current_user, 'phone'):
            current_user.phone = data['phone']
        if 'bio' in data and hasattr(current_user, 'bio'):
            current_user.bio = data['bio']
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if not current_user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin routes
@auth_bp.route('/admin/users', methods=['GET'])
@login_required
def get_users():
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        if not isinstance(current_user, Admin):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'created_at': get_ist_isoformat(user.created_at),
                'last_login': get_ist_isoformat(user.last_login),
                'is_active': user.is_active
            } for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated and refresh session"""
    try:
        db, User, Admin, ResumeAnalysis = get_models()
        
        if current_user.is_authenticated:
            # Refresh the session to extend its lifetime
            from flask import session
            session.permanent = True
            
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'email': current_user.email,
                    'full_name': current_user.get_full_name(),
                    'is_admin': isinstance(current_user, Admin)
                }
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500