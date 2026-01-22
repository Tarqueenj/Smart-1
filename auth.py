from functools import wraps
from flask import request, jsonify, session
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class AuthManager:
    """Authentication and authorization manager for SmartTriage AI"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.config.setdefault('SECRET_KEY', 'smarttriage-secret-key-2024')
        app.config.setdefault('JWT_EXPIRATION_HOURS', 24)
        self.app = app
    
    def generate_token(self, user_id: str, role: str) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.app.config['JWT_EXPIRATION_HOURS']),
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            self.app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return generate_password_hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(hashed, password)

# Initialize auth manager
auth_manager = AuthManager()

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Bearer token malformed'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Verify token
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'message': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'message': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'current_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def log_user_activity(user_id: str, action: str, details: dict = None):
    """Log user activity for audit trail"""
    # This would integrate with the audit log model
    activity = {
        'user_id': user_id,
        'action': action,
        'details': details or {},
        'timestamp': datetime.datetime.utcnow(),
        'ip_address': request.remote_addr if request else None
    }
    
    # In production, this would be stored in the database
    print(f"User Activity: {activity}")  # Debug logging
