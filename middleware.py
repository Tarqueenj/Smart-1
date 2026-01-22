from functools import wraps
from flask import request, jsonify, g
import time
from collections import defaultdict
import re

class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key, limit, period):
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < period]
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit=100, period=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as rate limit key
            key = request.remote_addr or 'unknown'
            
            if not rate_limiter.is_allowed(key, limit, period):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {limit} per {period} seconds.',
                    'retry_after': int(period)
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_patient_data(data):
    """Validate patient symptom submission data"""
    errors = []
    
    # Name validation
    if not data.get('name') or len(data.get('name', '').strip()) < 2:
        errors.append('Name is required and must be at least 2 characters')
    elif len(data.get('name', '')) > 100:
        errors.append('Name must be less than 100 characters')
    
    # Age validation
    try:
        age = int(data.get('age', 0))
        if age < 0 or age > 150:
            errors.append('Age must be between 0 and 150')
    except (ValueError, TypeError):
        errors.append('Valid age is required')
    
    # Symptoms validation
    symptoms = data.get('symptoms', '').strip()
    if not symptoms or len(symptoms) < 10:
        errors.append('Symptoms description is required and must be at least 10 characters')
    elif len(symptoms) > 2000:
        errors.append('Symptoms description must be less than 2000 characters')
    
    # Pregnancy status validation
    pregnancy_status = data.get('pregnancy_status', False)
    if pregnancy_status not in [True, False, 'true', 'false', 1, 0, '1', '0']:
        errors.append('Pregnancy status must be true or false')
    
    # Facility validation
    facility = data.get('facility', '').strip()
    if facility and len(facility) > 100:
        errors.append('Facility name must be less than 100 characters')
    
    return errors

def validate_user_login(data):
    """Validate user login data"""
    errors = []
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors.append('Email is required')
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append('Invalid email format')
    elif len(email) > 255:
        errors.append('Email must be less than 255 characters')
    
    # Password validation
    password = data.get('password', '')
    if not password:
        errors.append('Password is required')
    elif len(password) < 8:
        errors.append('Password must be at least 8 characters')
    elif len(password) > 128:
        errors.append('Password must be less than 128 characters')
    
    # Role validation
    role = data.get('role', '').strip()
    valid_roles = ['nurse', 'clinician', 'admin']
    if not role:
        errors.append('Role is required')
    elif role not in valid_roles:
        errors.append(f'Role must be one of: {", ".join(valid_roles)}')
    
    return errors

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ''
    
    # Basic XSS prevention
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>'
    ]
    
    sanitized = text
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_coordinates(lat, lng):
    """Validate GPS coordinates"""
    errors = []
    
    try:
        lat_float = float(lat)
        lng_float = float(lng)
        
        if not (-90 <= lat_float <= 90):
            errors.append('Latitude must be between -90 and 90 degrees')
        
        if not (-180 <= lng_float <= 180):
            errors.append('Longitude must be between -180 and 180 degrees')
            
    except (ValueError, TypeError):
        errors.append('Valid latitude and longitude coordinates are required')
    
    return errors
