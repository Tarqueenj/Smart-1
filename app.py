from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import os
import uuid
import json
import requests
from functools import wraps
import logging
import math

# Import configuration
try:
    from config import GOOGLE_PLACES_API_KEY
except ImportError:
    GOOGLE_PLACES_API_KEY = "AIzaSyAPJ762xmlsWpmF5N4U3oBasin1X2Gkj84"

from bson.objectid import ObjectId
from functools import wraps

# Import custom modules
from database import db_manager
from models import init_models
from ai_engine import triage_engine
from auth import auth_manager
from api import init_api
from utils import APIUtils, LoggingUtils
from middleware import rate_limit, validate_patient_data, validate_user_login, sanitize_input, validate_coordinates
from realtime import initialize_realtime

# Import Hugging Face AI service
try:
    from ai_service import AIServiceManager
    AI_AVAILABLE = True
    ai_service = AIServiceManager()
    print("✅ Hugging Face AI service loaded successfully")
except ImportError as e:
    AI_AVAILABLE = False
    ai_service = None
    print(f"⚠️ AI service not available: {e}")
except Exception as e:
    AI_AVAILABLE = False
    ai_service = None
    print(f"⚠️ AI service initialization failed: {e}")

app = Flask(__name__)
app.secret_key = 'smarttriage-secret-key-2024'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/smarttriage_db'
mongo = PyMongo(app)
CORS(app)

# User credentials for demo (in production, use proper database and password hashing)
USERS = {
    'nurse': {'password': 'nurse123', 'role': 'nurse', 'name': 'Sarah Johnson'},
    'clinician': {'password': 'clinician123', 'role': 'clinician', 'name': 'Dr. Michael Chen'},
    'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'}
}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            user_role = session.get('role')
            if user_role not in allowed_roles:
                return render_template('unauthorized.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize Socket.IO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize auth manager
auth_manager.init_app(app)

# Initialize database models
models = init_models(mongo)

# Initialize API routes
init_api(mongo)

# Initialize real-time WebSocket manager
realtime_manager = initialize_realtime(socketio)

# Connect to database (commented out for testing AI service)
# if not db_manager.connect():
#     print("❌ Failed to connect to database. Exiting...")
#     exit(1)

# Initialize database with collections and seed data
db_manager.initialize_collections()

# Legacy triage function for backward compatibility
def calculate_triage_score(symptoms, age, pregnancy_status=None):
    """Legacy triage function - use AI engine instead"""
    assessment = triage_engine.analyze_symptoms(symptoms, age, pregnancy_status)
    return assessment['severity'], assessment['reason']

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/patient')
def patient():
    """Patient portal"""
    return render_template('patient.html')

@app.route('/login')
def login():
    """Login page for staff"""
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Authenticate user login"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # Check user credentials
        if username in USERS and USERS[username]['password'] == password:
            session['user_id'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            
            # Redirect based on role
            if USERS[username]['role'] == 'nurse':
                return redirect(url_for('nurse_dashboard'))
            elif USERS[username]['role'] == 'clinician':
                return redirect(url_for('clinician_dashboard'))
            elif USERS[username]['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
            
    except Exception as e:
        return render_template('login.html', error='Login failed. Please try again.')

@app.route('/nurse')
@role_required('nurse', 'admin')
def nurse_dashboard():
    """Nurse triage dashboard"""
    return render_template('nurse.html')

@app.route('/clinician')
@role_required('clinician', 'admin')
def clinician_dashboard():
    """Clinician dashboard"""
    return render_template('clinician.html')

@app.route('/admin')
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin.html')

# Legacy API Routes (for backward compatibility)
@app.route('/api/submit_symptoms', methods=['POST'])
@rate_limit(limit=10, period=60)  # 10 submissions per minute
def submit_symptoms():
    """Submit patient symptoms for triage (legacy endpoint)"""
    try:
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_patient_data(data)
        if validation_errors:
            return APIUtils.create_error_response(f'Validation failed: {", ".join(validation_errors)}', 400)
        
        # Sanitize inputs
        sanitized_data = {
            'name': sanitize_input(data['name']),
            'age': int(data['age']),
            'symptoms': sanitize_input(data['symptoms']),
            'pregnancy_status': data.get('pregnancy_status', False),
            'facility': sanitize_input(data.get('facility', 'MTRH'))
        }
        
        # Get additional context for AI analysis
        additional_context = {
            'facility': sanitized_data['facility'],
            'timestamp': datetime.now().isoformat(),
            'patient_name': sanitized_data['name']
        }
        
        # Use Hugging Face AI service if available, otherwise fallback to original AI engine
        if AI_AVAILABLE and ai_service:
            ai_result = ai_service.get_ai_analysis(
                sanitized_data['symptoms'],
                sanitized_data['age'],
                sanitized_data['pregnancy_status'],
                additional_context
            )
            assessment = {
                'severity': ai_result.get('severity', 'GREEN'),
                'reason': ai_result.get('reason', 'Analysis completed'),
                'confidence': ai_result.get('confidence', 0.70),
                'ai_insights': ai_result.get('ai_insights', []),
                'analysis_method': ai_result.get('analysis_method', 'huggingface'),
                'model_used': ai_result.get('model_used', 'unknown')
            }
        else:
            # Fallback to original AI engine
            assessment = triage_engine.analyze_symptoms(
                sanitized_data['symptoms'],
                sanitized_data['age'],
                sanitized_data['pregnancy_status']
            )
            assessment.update({
                'ai_insights': ['AI service not available - using standard analysis'],
                'analysis_method': 'keyword_fallback',
                'model_used': 'ai_engine',
                'confidence': 0.70
            })
        
        # Create patient record
        patient_data = {
            'name': sanitized_data['name'],
            'age': sanitized_data['age'],
            'symptoms': sanitized_data['symptoms'],
            'severity': assessment['severity'],
            'triage_reason': assessment['reason'],
            'pregnancy_status': sanitized_data['pregnancy_status'],
            'facility': sanitized_data['facility'],
            'ai_confidence': assessment.get('confidence', 0.70),
            'analysis_method': assessment.get('analysis_method', 'unknown'),
            'ai_insights': assessment.get('ai_insights', []),
            'model_used': assessment.get('model_used', 'unknown')
        }
        
        patient_id = None
        
        try:
            # Try to save to database
            patient = models['patient'].create(patient_data)
            patient_id = str(patient.inserted_id) if hasattr(patient, 'inserted_id') else 'unknown'
        except Exception as db_error:
            print(f"⚠️ Database save failed: {db_error}")
            patient_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        finally:
            # Ensure patient_id is always set
            if not patient_id:
                patient_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Record analytics
            models['analytics'].record_patient_flow(
                datetime.now(),
                assessment['severity'],
                'arrival'
            )
        except Exception as analytics_error:
            print(f"⚠️ Analytics recording failed: {analytics_error}")
        finally:
            # Ensure analytics attempt completes
            pass
        
        try:
            # Log the action
            LoggingUtils.log_action(
                'anonymous',
                'submit_symptoms',
                'patient',
                patient_id,
                {
                    'severity': assessment['severity'],
                    'analysis_method': assessment.get('analysis_method', 'unknown'),
                    'confidence': assessment.get('confidence', 0.70)
                }
            )
        except Exception as log_error:
            print(f"⚠️ Logging failed: {log_error}")
        finally:
            # Ensure logging completes
            pass
        
        return APIUtils.create_response(
            success=True,
            message='Triage assessment completed',
            data={
                'patient_id': patient_id,
                'severity': assessment['severity'],
                'reason': assessment['reason'],
                'confidence': assessment.get('confidence', 0.70),
                'ai_insights': assessment.get('ai_insights', []),
                'analysis_method': assessment.get('analysis_method', 'unknown'),
                'model_used': assessment.get('model_used', 'unknown'),
                'assessment': assessment
            }
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'submit_symptoms'})
        return APIUtils.create_error_response('Triage analysis failed', 500)
    
    finally:
        # Cleanup if needed
        pass

@app.route('/api/get_patients')
def get_patients():
    """Get all patients (legacy endpoint)"""
    try:
        patients = models['patient'].get_all()
        
        return APIUtils.create_response(
            success=True,
            data=patients
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_patients'})
        return APIUtils.create_error_response('Failed to retrieve patients', 500)

@app.route('/api/update_patient_status', methods=['POST'])
def update_patient_status():
    """Update patient status (legacy endpoint)"""
    try:
        data = request.get_json()
        patient_id = data['patient_id']
        new_status = data['status']
        
        # Validate status
        valid_statuses = ['waiting', 'in-progress', 'completed']
        if new_status not in valid_statuses:
            return APIUtils.create_error_response(f'Invalid status. Must be one of: {valid_statuses}')
        
        # Update patient status
        success = models['patient'].update_status(patient_id, new_status)
        
        if not success:
            return APIUtils.create_error_response('Patient not found', 404)
        
        # Record analytics if completed
        if new_status == 'completed':
            models['analytics'].record_patient_flow(
                datetime.now(),
                None,
                'discharge'
            )
        
        # Log the action
        LoggingUtils.log_action(
            'anonymous',
            'update_patient_status',
            'patient',
            patient_id,
            {'new_status': new_status}
        )
        
        return APIUtils.create_response(
            success=True,
            message='Patient status updated successfully'
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'update_patient_status'})
        return APIUtils.create_error_response('Failed to update patient status', 500)

@app.route('/api/ai_models', methods=['GET'])
def get_ai_models():
    """Get available AI models"""
    try:
        if AI_AVAILABLE and ai_service:
            models = ai_service.get_available_models()
            return APIUtils.create_response(
                success=True,
                message='AI models retrieved successfully',
                data={
                    'ai_available': True,
                    'models': models,
                    'current_model': ai_service.huggingface_service.model_name if ai_service.huggingface_service else None
                }
            )
        else:
            return APIUtils.create_response(
                success=True,
                message='AI service not available',
                data={
                    'ai_available': False,
                    'models': [],
                    'current_model': None,
                    'message': 'AI service not available - using keyword analysis'
                }
            )
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_ai_models'})
        return APIUtils.create_error_response('Failed to get AI models', 500)

@app.route('/api/get_analytics')
def get_analytics():
    """Get analytics data (legacy endpoint)"""
    try:
        # Get today's statistics
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        patient_stats = models['patient'].get_statistics(today)
        
        # Get all patients for AI analysis statistics
        all_patients = models['patient'].get_all()
        
        # Calculate AI analysis statistics
        ai_stats = {
            'total_analyzed': len(all_patients),
            'huggingface_used': len([p for p in all_patients if p.get('analysis_method') == 'huggingface']),
            'keyword_fallback_used': len([p for p in all_patients if p.get('analysis_method') == 'keyword_fallback']),
            'average_confidence': round(sum([p.get('ai_confidence', 0) for p in all_patients]) / len(all_patients), 2) if all_patients else 0,
            'models_used': list(set([p.get('model_used', 'unknown') for p in all_patients]))
        }
        
        # Mock additional analytics
        analytics_data = {
            'total_patients': patient_stats['total_patients'],
            'red_patients': patient_stats['red_patients'],
            'yellow_patients': patient_stats['yellow_patients'],
            'green_patients': patient_stats['green_patients'],
            'average_wait_time': round(patient_stats['avg_wait_time'] or 0, 1),
            'peak_hour': 14,
            'bed_occupancy': 78,
            'doctor_to_patient_ratio': 1.8,
            'ai_analysis_stats': ai_stats
        }
        
        return APIUtils.create_response(
            success=True,
            data=analytics_data
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_analytics'})
        return APIUtils.create_error_response('Failed to retrieve analytics', 500)

@app.route('/api/get_location_hospitals', methods=['POST'])
@rate_limit(limit=30, period=60)
def get_location_hospitals():
    """Get hospitals based on user location"""
    try:
        data = request.get_json()
        lat = data.get('latitude')
        lng = data.get('longitude')
        severity = data.get('severity', 'YELLOW')
        
        if not lat or not lng:
            return APIUtils.create_error_response('Coordinates required', 400)
        
        # Get all facilities from database
        all_facilities = list(models['facility'].collection.find({'is_active': True}))
        
        # Calculate real distances for all facilities
        facilities_with_distance = []
        for facility in all_facilities:
            facility_coords = facility.get('coordinates', {})
            facility_lat = facility_coords.get('lat')
            facility_lng = facility_coords.get('lng')
            
            if facility_lat and facility_lng:
                # Calculate real distance using Haversine formula
                distance = calculate_distance(float(lat), float(lng), facility_lat, facility_lng)
                
                # Only include facilities within specified radius
                if distance <= 50:  # 50km radius
                    facility['distance_km'] = distance
                    
                    # Calculate realistic wait time based on current time and facility capacity
                    current_hour = datetime.now().hour
                    base_wait = facility.get('base_wait_time', 30)
                    
                    # Adjust wait time based on time of day (busier during certain hours)
                    if 8 <= current_hour <= 12:  # Morning rush
                        time_multiplier = 1.5
                    elif 13 <= current_hour <= 17:  # Afternoon
                        time_multiplier = 1.2
                    elif 18 <= current_hour <= 22:  # Evening
                        time_multiplier = 1.3
                    else:  # Night
                        time_multiplier = 0.8
                    
                    # Add some variation based on facility size
                    capacity_factor = facility.get('capacity', {}).get('emergency_beds', 20)
                    size_multiplier = max(0.7, min(1.5, 20 / capacity_factor))
                    
                    facility['estimated_wait'] = int(base_wait * time_multiplier * size_multiplier)
                    
                    # Smart recommendation based on distance and wait time
                    facility['recommended'] = distance < 30 and facility['estimated_wait'] < 45
                    
                    # Convert ObjectId to string for JSON serialization
                    facility['_id'] = str(facility['_id'])
                    facilities_with_distance.append(facility)
        
        # Sort by distance (closest first)
        facilities_with_distance.sort(key=lambda f: f['distance_km'])
        
        return APIUtils.create_response(
            success=True,
            data={
                'nearest_hospitals': facilities_with_distance[:10],
                'recommended_hospitals': facilities_with_distance[:2],
                'user_location': {
                    'latitude': float(lat),
                    'longitude': float(lng)
                }
            }
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_location_hospitals'})
        return APIUtils.create_error_response('Failed to retrieve hospitals', 500)

@app.route('/api/google_places_search', methods=['POST'])
@rate_limit(limit=20, period=60)
def google_places_search():
    """Search hospitals using Google Places API"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location')  # Optional: lat,lng for nearby search
        
        if not query:
            return APIUtils.create_error_response('Search query required', 400)
        
        # Google Places API key (imported from config)
        if not GOOGLE_PLACES_API_KEY or GOOGLE_PLACES_API_KEY == "YOUR_GOOGLE_PLACES_API_KEY":
            return APIUtils.create_error_response('Google Places API key not configured', 500)
        
        if location:
            # Nearby search
            lat, lng = location.get('lat'), location.get('lng')
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=10000&type=hospital&key={GOOGLE_PLACES_API_KEY}"
        else:
            # Text search
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}+hospital+Kenya&key={GOOGLE_PLACES_API_KEY}"
        
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') != 'OK':
            return APIUtils.create_error_response(f'Google Places API error: {data.get("error_message", "Unknown error")}', 400)
        
        # Process results
        hospitals = []
        for place in data.get('results', []):
            hospital = {
                'name': place.get('name', ''),
                'address': place.get('vicinity', place.get('formatted_address', '')),
                'coordinates': {
                    'lat': place['geometry']['location']['lat'],
                    'lng': place['geometry']['location']['lng']
                },
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'types': place.get('types', []),
                'place_id': place.get('place_id', ''),
                'opening_hours': place.get('opening_hours'),
                'photos': place.get('photos', []),
                'source': 'google_places'
            }
            
            # Calculate distance if user location provided
            if location:
                from utils import calculate_distance  # Import the distance function
                hospital['distance_km'] = calculate_distance(
                    lat, lng, 
                    hospital['coordinates']['lat'], 
                    hospital['coordinates']['lng']
                )
            
            hospitals.append(hospital)
        
        return APIUtils.create_response(
            success=True,
            data={
                'hospitals': hospitals,
                'total_found': len(hospitals),
                'search_type': 'nearby' if location else 'text_search'
            }
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'google_places_search'})
        return APIUtils.create_error_response('Google Places search failed', 500)

@app.route('/api/get_hospitals_by_address', methods=['POST'])
@rate_limit(limit=20, period=60)
def get_hospitals_by_address():
    """Get hospitals by address with geocoding"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        severity = data.get('severity', 'YELLOW')
        
        if not address:
            return APIUtils.create_error_response('Address required', 400)
        
        # Simulate geocoding for common Kenyan locations
        location_coordinates = {
            'nairobi': {'lat': -1.2921, 'lng': 36.8219},
            'eldoret': {'lat': 0.5143, 'lng': 35.2698},
            'mombasa': {'lat': -4.0435, 'lng': 39.6682},
            'kisumu': {'lat': -0.0917, 'lng': 34.7680},
            'nakuru': {'lat': -0.3031, 'lng': 36.0695}
        }
        
        # Find matching location
        user_lat, user_lng = None, None
        for location, coords in location_coordinates.items():
            if location.lower() in address.lower():
                user_lat, user_lng = coords['lat'], coords['lng']
                break
        
        if user_lat is None:
            # Default to Nairobi if no match found
            user_lat, user_lng = -1.2921, 36.8219
        
        # Get hospitals for geocoded location
        all_facilities = list(models['facility'].collection.find({'is_active': True}))
        facilities_with_distance = []
        
        for facility in all_facilities:
            facility_coords = facility.get('coordinates', {})
            facility_lat = facility_coords.get('lat')
            facility_lng = facility_coords.get('lng')
            
            if facility_lat and facility_lng:
                distance = calculate_distance(user_lat, user_lng, facility_lat, facility_lng)
                if distance <= 50:
                    facility['distance_km'] = distance
                    facility['_id'] = str(facility['_id'])
                    facilities_with_distance.append(facility)
        
        facilities_with_distance.sort(key=lambda f: f['distance_km'])
        
        return APIUtils.create_response(
            success=True,
            data={
                'nearest_hospitals': facilities_with_distance[:10],
                'geocoded_location': {'latitude': user_lat, 'longitude': user_lng},
                'address': address
            }
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_hospitals_by_address'})
        return APIUtils.create_error_response('Failed to process address', 500)

@app.route('/api/get_facilities')
@rate_limit(limit=30, period=60)  # 30 requests per minute
def get_facilities():
    """Get facilities with real distance calculation based on user's location"""
    try:
        # Get user's location from query parameters
        user_lat = request.args.get('lat')
        user_lng = request.args.get('lng')
        max_distance = int(request.args.get('max_distance', 100))  # 100km default radius
        
        # Validate coordinates
        validation_errors = validate_coordinates(user_lat, user_lng)
        if validation_errors:
            return APIUtils.create_error_response(f'Invalid coordinates: {", ".join(validation_errors)}', 400)
        
        # Require user location - no fallbacks
        if not user_lat or not user_lng:
            return APIUtils.create_error_response('Location coordinates required. Please enable location services.', 400)
        
        user_lat = float(user_lat)
        user_lng = float(user_lng)
        
        # Get all facilities from database
        all_facilities = list(models['facility'].collection.find({'is_active': True}))
        
        # Calculate real distances for all facilities
        facilities_with_distance = []
        for facility in all_facilities:
            facility_coords = facility.get('coordinates', {})
            facility_lat = facility_coords.get('lat')
            facility_lng = facility_coords.get('lng')
            
            if facility_lat and facility_lng:
                # Calculate real distance using Haversine formula
                distance = calculate_distance(user_lat, user_lng, facility_lat, facility_lng)
                
                # Only include facilities within specified radius
                if distance <= max_distance:
                    facility['distance'] = distance
                    
                    # Calculate realistic wait time based on current time and facility capacity
                    current_hour = datetime.now().hour
                    base_wait = facility.get('base_wait_time', 30)
                    
                    # Adjust wait time based on time of day (busier during certain hours)
                    if 8 <= current_hour <= 12:  # Morning rush
                        time_multiplier = 1.5
                    elif 13 <= current_hour <= 17:  # Afternoon
                        time_multiplier = 1.2
                    elif 18 <= current_hour <= 22:  # Evening
                        time_multiplier = 1.3
                    else:  # Night
                        time_multiplier = 0.8
                    
                    # Add some variation based on facility size
                    capacity_factor = facility.get('capacity', {}).get('emergency_beds', 20)
                    size_multiplier = max(0.7, min(1.5, 20 / capacity_factor))
                    
                    facility['estimated_wait'] = int(base_wait * time_multiplier * size_multiplier)
                    
                    # Smart recommendation based on distance and wait time
                    facility['recommended'] = distance < 30 and facility['estimated_wait'] < 45
                    
                    # Convert ObjectId to string for JSON serialization
                    facility['_id'] = str(facility['_id'])
                    facilities_with_distance.append(facility)
        
        # Sort by distance (closest first)
        facilities_with_distance.sort(key=lambda f: f['distance'])
        
        # Limit to top 10 nearest facilities
        facilities_with_distance = facilities_with_distance[:10]
        
        return APIUtils.create_response(
            success=True,
            data=facilities_with_distance
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'get_facilities'})
        return APIUtils.create_error_response('Failed to retrieve facilities', 500)

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates using Vincenty's formula for maximum accuracy"""
    import math
    
    # Vincenty's formula for accurate distance calculation on ellipsoid
    # WGS84 ellipsoid parameters
    a = 6378137.0  # Semi-major axis
    f = 1 / 298.257223563  # Flattening
    b = (1 - f) * a  # Semi-minor axis
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lng1_rad = math.radians(lng1)
    lng2_rad = math.radians(lng2)
    
    # Difference in longitude
    L = lng2_rad - lng1_rad
    
    # Reduced latitude
    U1 = math.atan((1 - f) * math.tan(lat1_rad))
    U2 = math.atan((1 - f) * math.tan(lat2_rad))
    
    # Iterative calculation
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    
    # Initial approximation
    lambda_val = L
    max_iterations = 100
    tolerance = 1e-12
    
    for _ in range(max_iterations):
        sin_lambda = math.sin(lambda_val)
        cos_lambda = math.cos(lambda_val)
        
        sin_sigma = math.sqrt((cosU2 * sin_lambda) ** 2 + 
                           (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda) ** 2)
        
        if sin_sigma == 0:
            return 0  # Co-incident points
        
        cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        
        sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        if cos2_alpha == 0:
            cos2_sigma_m = 0
        else:
            cos2_sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos2_alpha
        
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        
        lambda_prev = lambda_val
        lambda_val = L + (1 - C) * f * sin_alpha * (
            sigma + C * sin_sigma * (cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2))
        )
        
        if abs(lambda_val - lambda_prev) < tolerance:
            break
    
    # Final calculations
    u2 = cos2_alpha * (a ** 2 - b ** 2) / b ** 2
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    delta_sigma = B * sin_sigma * (
        cos2_sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) -
            B / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)
        )
    )
    
    # Distance on the ellipsoid
    s = b * A * (sigma - delta_sigma)
    
    # Convert to kilometers
    distance_km = s / 1000.0
    
    return distance_km

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = db_manager.client.admin.command('ping') if db_manager.client else None
        
        return APIUtils.create_response(
            success=True,
            message='System healthy',
            data={
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'database': 'connected' if db_status else 'disconnected'
            }
        )
        
    except Exception as e:
        LoggingUtils.log_error(e, {'action': 'health_check'})
        return APIUtils.create_error_response('System unhealthy', 500)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return APIUtils.create_error_response('Resource not found', 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    LoggingUtils.log_error(error, {'type': 'internal_server_error'})
    return APIUtils.create_error_response('Internal server error', 500)

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return APIUtils.create_error_response('Bad request', 400)

# Application shutdown
@app.teardown_appcontext
def shutdown_db(exception=None):
    """Cleanup on app shutdown"""
    pass

if __name__ == '__main__':
    try:
        print("🚀 Starting SmartTriage AI with Real-time Updates...")
        print(f"📊 Database: {db_manager.db.name if db_manager.db is not None else 'Not connected'}")
        print("🌐 Server: http://localhost:5000")
        print("🌐 WebSocket: ws://localhost:5000")
        print("🏥 Patient Portal: http://localhost:5000/patient")
        print("👩‍⚕️  Nurse Dashboard: http://localhost:5000/nurse")
        print("👨‍⚕️  Clinician View: http://localhost:5000/clinician")
        print("⚙️  Admin Panel: http://localhost:5000/admin")
        
        # Run Flask with Socket.IO
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5000
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down SmartTriage AI...")
        db_manager.disconnect()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        db_manager.disconnect()
