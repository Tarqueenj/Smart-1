import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import re

class ValidationUtils:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (Kenyan format)"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Check for Kenyan phone number formats
        patterns = [
            r'^2547\d{8}$',  # +254 7XX XXX XXX
            r'^07\d{8}$',     # 07XX XXX XXX
            r'^\d{10}$'       # 10 digits
        ]
        
        return any(re.match(pattern, digits) for pattern in patterns)
    
    @staticmethod
    def validate_age(age):
        """Validate age (0-150 years)"""
        try:
            age_int = int(age)
            return 0 <= age_int <= 150
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_severity(severity):
        """Validate triage severity"""
        valid_severities = ['RED', 'YELLOW', 'GREEN']
        return severity.upper() in valid_severities
    
    @staticmethod
    def validate_patient_data(data):
        """Validate complete patient data"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'age', 'symptoms']
        for field in required_fields:
            if not data.get(field) or str(data[field]).strip() == '':
                errors.append(f'{field} is required')
        
        # Name validation
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                errors.append('Name must be at least 2 characters')
            elif len(name) > 100:
                errors.append('Name must be less than 100 characters')
        
        # Age validation
        if 'age' in data:
            if not ValidationUtils.validate_age(data['age']):
                errors.append('Invalid age (must be between 0-150)')
        
        # Symptoms validation
        if 'symptoms' in data:
            symptoms = data['symptoms'].strip()
            if len(symptoms) < 5:
                errors.append('Symptoms description must be at least 5 characters')
            elif len(symptoms) > 1000:
                errors.append('Symptoms description must be less than 1000 characters')
        
        return errors
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return ''
        
        # Remove potentially harmful characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()

class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_data(data):
        """Hash data using SHA-256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_data_hash(data, expected_hash):
        """Verify data against expected hash"""
        return SecurityUtils.hash_data(data) == expected_hash
    
    @staticmethod
    def mask_sensitive_data(data, mask_char='*'):
        """Mask sensitive data for logging"""
        if isinstance(data, str):
            if len(data) <= 4:
                return mask_char * len(data)
            return data[:2] + mask_char * (len(data) - 4) + data[-2:]
        return data
    
    @staticmethod
    def rate_limit_check(user_id, action, limit=10, window_minutes=60):
        """Mock rate limiting implementation"""
        # In production, this would use Redis or similar
        # For now, return True (no limit)
        return True

class DateTimeUtils:
    """Utility class for date and time operations"""
    
    @staticmethod
    def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
        """Format datetime to string"""
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
        """Parse string to datetime"""
        try:
            return datetime.strptime(dt_str, format_str)
        except ValueError:
            try:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except ValueError:
                return None
    
    @staticmethod
    def get_time_ago(dt):
        """Get human-readable time ago string"""
        if isinstance(dt, str):
            dt = DateTimeUtils.parse_datetime(dt)
        
        if not dt:
            return 'Unknown'
        
        now = datetime.now()
        diff = now - dt
        
        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            minutes = diff.seconds // 60
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = diff.seconds // 3600
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff < timedelta(weeks=1):
            days = diff.days
            return f'{days} day{"s" if days != 1 else ""} ago'
        else:
            return dt.strftime('%Y-%m-%d')
    
    @staticmethod
    def get_date_range(period):
        """Get start and end date for a period"""
        now = datetime.now()
        
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == 'week':
            start = now - timedelta(days=7)
            end = now
        elif period == 'month':
            start = now - timedelta(days=30)
            end = now
        elif period == 'year':
            start = now - timedelta(days=365)
            end = now
        else:
            start = now - timedelta(days=1)
            end = now
        
        return start, end

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def generate_filename(original_filename, prefix=''):
        """Generate unique filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(4)
        
        if prefix:
            return f"{prefix}_{timestamp}_{random_suffix}_{original_filename}"
        else:
            return f"{timestamp}_{random_suffix}_{original_filename}"
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"

class APIUtils:
    """Utility class for API operations"""
    
    @staticmethod
    def create_response(success=True, message=None, data=None, status_code=200):
        """Create standardized API response"""
        response = {
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if message:
            response['message'] = message
        
        if data:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def create_error_response(message, status_code=400, details=None):
        """Create standardized error response"""
        response = {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            response['details'] = details
        
        return jsonify(response), status_code
    
    @staticmethod
    def paginate_results(results, page=1, per_page=20):
        """Paginate results"""
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated = results[start:end]
        
        return {
            'results': paginated,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(results),
                'pages': (len(results) + per_page - 1) // per_page,
                'has_next': end < len(results),
                'has_prev': page > 1
            }
        }

class LoggingUtils:
    """Utility class for logging operations"""
    
    @staticmethod
    def log_action(user_id, action, resource_type, resource_id, details=None):
        """Log user action"""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # In production, this would be stored in database or log file
        print(f"ACTION_LOG: {json.dumps(log_entry, default=str)}")
        
        return log_entry
    
    @staticmethod
    def log_error(error, context=None):
        """Log error with context"""
        error_entry = {
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'request_info': {
                'method': request.method if request else None,
                'url': request.url if request else None,
                'ip': request.remote_addr if request else None
            }
        }
        
        # In production, this would be sent to error tracking service
        print(f"ERROR_LOG: {json.dumps(error_entry, default=str)}")
        
        return error_entry

class MetricsUtils:
    """Utility class for metrics and analytics"""
    
    @staticmethod
    def calculate_percentile(values, percentile):
        """Calculate percentile of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    @staticmethod
    def calculate_moving_average(values, window_size):
        """Calculate moving average"""
        if not values or window_size <= 0:
            return []
        
        moving_averages = []
        for i in range(len(values)):
            start = max(0, i - window_size + 1)
            window = values[start:i + 1]
            average = sum(window) / len(window)
            moving_averages.append(average)
        
        return moving_averages
    
    @staticmethod
    def smooth_data(data, alpha=0.3):
        """Apply exponential smoothing to data"""
        if not data:
            return []
        
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed_value = alpha * data[i] + (1 - alpha) * smoothed[i - 1]
            smoothed.append(smoothed_value)
        
        return smoothed

# Decorators
def validate_json(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return APIUtils.create_error_response('Request must be JSON', 400)
            
            data = request.get_json()
            if not data:
                return APIUtils.create_error_response('Invalid JSON data', 400)
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return APIUtils.create_error_response(
                        f'Missing required fields: {", ".join(missing_fields)}',
                        400
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_call(action):
    """Decorator to log API calls"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = f(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                LoggingUtils.log_action(
                    user_id=getattr(request, 'current_user', {}).get('user_id', 'anonymous'),
                    action=action,
                    resource_type='api_call',
                    resource_id=request.endpoint,
                    details={
                        'duration_seconds': duration,
                        'status_code': result[1] if isinstance(result, tuple) else 200
                    }
                )
                
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                LoggingUtils.log_error(e, {
                    'action': action,
                    'duration_seconds': duration
                })
                
                raise
        
        return decorated_function
    return decorator
