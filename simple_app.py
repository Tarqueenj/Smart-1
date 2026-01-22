from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os
import uuid
import json
import requests
import math
from functools import wraps

# Import AI service
try:
    from ai_service import AIServiceManager
    ai_service = AIServiceManager()
    AI_AVAILABLE = True
    print(" Hugging Face AI service loaded successfully")
except ImportError as e:
    AI_AVAILABLE = False
    ai_service = None
    print(f" AI service not available: {e}")

# Import configuration
try:
    from config import GOOGLE_PLACES_API_KEY
except ImportError:
    GOOGLE_PLACES_API_KEY = "AIzaSyAPJ762xmlsWpmF5N4U3oBasin1X2Gkj84"

app = Flask(__name__)
app.secret_key = 'smarttriage-secret-key-2024'

# In-memory storage for patients (for demo purposes)
patients_db = []

# User credentials for demo (in production, use proper database and password hashing)
USERS = {
    'nurse': {'password': 'nurse123', 'role': 'nurse', 'name': 'Sarah Johnson'},
    'clinician': {'password': 'clinician123', 'role': 'clinician', 'name': 'Dr. Michael Chen'},
    'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'}
}

# ArcGIS Configuration
ARCGIS_CONFIG = {
    'geocoder_url': 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer',
    'routing_url': 'https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World',
    'api_key': None,
    'default_search_radius': 50000
}

# Kenya Hospitals Data
KENYA_HOSPITALS = [
    {
        'name': 'Moi Teaching and Referral Hospital',
        'address': 'Eldoret, Kenya',
        'coordinates': {'lat': 0.5143, 'lng': 35.2698},
        'phone': '+254-53-30001',
        'specialties': ['Emergency', 'Surgery', 'Maternity', 'Pediatrics'],
        'capacity': {'total': 800, 'available': 245},
        'wait_time_minutes': 45,
        'level': 'Referral'
    },
    {
        'name': 'Eldoret Hospital',
        'address': 'Eldoret, Kenya',
        'coordinates': {'lat': 0.5277, 'lng': 35.2698},
        'phone': '+254-53-20333',
        'specialties': ['Emergency', 'General Medicine', 'Surgery'],
        'capacity': {'total': 200, 'available': 67},
        'wait_time_minutes': 30,
        'level': 'County'
    },
    {
        'name': 'Kenyatta National Hospital',
        'address': 'Nairobi, Kenya',
        'coordinates': {'lat': -1.2921, 'lng': 36.8219},
        'phone': '+254-20-2726300',
        'specialties': ['Emergency', 'Surgery', 'Maternity', 'Pediatrics', 'Oncology'],
        'capacity': {'total': 1800, 'available': 450},
        'wait_time_minutes': 60,
        'level': 'National Referral'
    },
    {
        'name': 'Nairobi Hospital',
        'address': 'Nairobi, Kenya',
        'coordinates': {'lat': -1.2864, 'lng': 36.8172},
        'phone': '+254-20-2715400',
        'specialties': ['Emergency', 'General Medicine', 'Surgery', 'Cardiology'],
        'capacity': {'total': 650, 'available': 180},
        'wait_time_minutes': 35,
        'level': 'Private'
    },
    {
        'name': 'Mombasa County Hospital',
        'address': 'Mombasa, Kenya',
        'coordinates': {'lat': -4.0435, 'lng': 39.6682},
        'phone': '+254-41-2315444',
        'specialties': ['Emergency', 'General Medicine', 'Maternity'],
        'capacity': {'total': 400, 'available': 120},
        'wait_time_minutes': 40,
        'level': 'County'
    },
    {
        'name': 'Kisumu County Hospital',
        'address': 'Kisumu, Kenya',
        'coordinates': {'lat': -0.0917, 'lng': 34.7680},
        'phone': '+254-57-2022000',
        'specialties': ['Emergency', 'General Medicine', 'Pediatrics'],
        'capacity': {'total': 350, 'available': 95},
        'wait_time_minutes': 25,
        'level': 'County'
    },
    {
        'name': 'Nakuru Level 5 Hospital',
        'address': 'Nakuru, Kenya',
        'coordinates': {'lat': -0.3031, 'lng': 36.0695},
        'phone': '+254-51-2210000',
        'specialties': ['Emergency', 'General Medicine', 'Surgery', 'Maternity'],
        'capacity': {'total': 500, 'available': 150},
        'wait_time_minutes': 30,
        'level': 'County'
    },
    {
        'name': 'Thika Level 5 Hospital',
        'address': 'Thika, Kenya',
        'coordinates': {'lat': -1.0333, 'lng': 37.0717},
        'phone': '+254-67-2220000',
        'specialties': ['Emergency', 'General Medicine', 'Surgery'],
        'capacity': {'total': 300, 'available': 80},
        'wait_time_minutes': 28,
        'level': 'County'
    },
    {
        'name': 'Kericho County Hospital',
        'address': 'Kericho, Kenya',
        'coordinates': {'lat': -0.3667, 'lng': 35.2833},
        'phone': '+254-52-2020000',
        'specialties': ['Emergency', 'General Medicine', 'Maternity'],
        'capacity': {'total': 250, 'available': 70},
        'wait_time_minutes': 20,
        'level': 'County'
    },
    {
        'name': 'Kakamega County Hospital',
        'address': 'Kakamega, Kenya',
        'coordinates': {'lat': 0.2833, 'lng': 34.7500},
        'phone': '+254-56-300000',
        'specialties': ['Emergency', 'General Medicine', 'Pediatrics'],
        'capacity': {'total': 280, 'available': 85},
        'wait_time_minutes': 22,
        'level': 'County'
    }
]

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def geocode_address(address):
    try:
        params = {'address': address, 'f': 'json'}
        response = requests.get(f"{ARCGIS_CONFIG['geocoder_url']}/findAddressCandidates", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('candidates'):
                candidate = data['candidates'][0]
                return {
                    'success': True,
                    'address': candidate.get('address'),
                    'coordinates': {
                        'lat': candidate.get('location', {}).get('y'),
                        'lng': candidate.get('location', {}).get('x')
                    }
                }
        return {'success': False, 'error': 'Address not found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def find_nearby_hospitals(lat, lng, radius_km=50, severity='YELLOW'):
    nearby = []
    for hospital in KENYA_HOSPITALS:
        distance = haversine_distance(lat, lng, hospital['coordinates']['lat'], hospital['coordinates']['lng'])
        if distance <= radius_km:
            h = hospital.copy()
            h.update({
                'distance_km': round(distance, 2),
                'travel_time_minutes': max(5, int(distance * 2)),
                'capacity_utilization': ((h['capacity']['total'] - h['capacity']['available']) / h['capacity']['total']) * 100
            })
            nearby.append(h)
    nearby.sort(key=lambda x: x['distance_km'])
    return {'success': True, 'nearest_hospitals': nearby, 'recommended_hospitals': nearby[:2]}

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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/nurse')
@role_required('nurse', 'admin')
def nurse():
    return render_template('nurse.html')

@app.route('/clinician')
@role_required('clinician', 'admin')
def clinician():
    return render_template('clinician.html')

@app.route('/admin')
@role_required('admin')
def admin():
    return render_template('admin.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Authenticate user login with role tracking"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # Check user credentials
        if username in USERS and USERS[username]['password'] == password:
            user_role = USERS[username]['role']
            user_name = USERS[username]['name']
            
            # Create session
            session['user_id'] = username
            session['role'] = user_role
            session['name'] = user_name
            
            # Log successful login with role
            print(f"🔐 LOGIN SUCCESS: {username} ({user_role}) - {user_name}")
            
            # Redirect based on role
            if user_role == 'nurse':
                return redirect(url_for('nurse'))
            elif user_role == 'clinician':
                return redirect(url_for('clinician'))
            elif user_role == 'admin':
                return redirect(url_for('admin'))
        else:
            print(f"❌ LOGIN FAILED: {username} - Invalid credentials")
            return render_template('login.html', error='Invalid username or password')
            
    except Exception as e:
        print(f"🚨 LOGIN ERROR: {str(e)}")
        return render_template('login.html', error='Login failed. Please try again.')

@app.route('/auth/custom_login', methods=['POST'])
def auth_custom_login():
    """Handle custom login with role-based access"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        # For custom login, we need to determine role from username or separate field
        # Since user wants custom role, we'll create a dynamic user based on role
        # In production, this would validate against a real database
        
        # For demo, we'll create a simple role-based user
        # Extract role from username if it contains role keywords, or use a default
        username_lower = username.lower()
        if 'nurse' in username_lower:
            user_role = 'nurse'
            user_name = f"{username} (Nurse)"
        elif 'clinician' in username_lower or 'doctor' in username_lower:
            user_role = 'clinician'
            user_name = f"Dr. {username}"
        elif 'admin' in username_lower:
            user_role = 'admin'
            user_name = f"{username} (Admin)"
        else:
            # Default to nurse if no role detected
            user_role = 'nurse'
            user_name = f"{username} (Staff)"
        
        # Create session
        session['user_id'] = username
        session['role'] = user_role
        session['name'] = user_name
        session['custom_user'] = True  # Flag as custom user
        
        # Log successful custom login
        print(f"🔐 CUSTOM LOGIN SUCCESS: {username} ({user_role}) - {user_name}")
        
        # Redirect based on role
        if user_role == 'nurse':
            return redirect(url_for('nurse'))
        elif user_role == 'clinician':
            return redirect(url_for('clinician'))
        elif user_role == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('nurse'))  # Default to nurse
            
    except Exception as e:
        print(f"🚨 CUSTOM LOGIN ERROR: {str(e)}")
        return render_template('login.html', error='Custom login failed. Please try again.')

@app.route('/api/get_location_hospitals', methods=['POST'])
def get_location_hospitals():
    """Get hospitals based on user location"""
    try:
        data = request.get_json()
        lat = data.get('latitude')
        lng = data.get('longitude')
        severity = data.get('severity', 'YELLOW')
        
        if not lat or not lng:
            return jsonify({'success': False, 'error': 'Coordinates required'})
        
        result = find_nearby_hospitals(lat, lng, severity=severity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_hospitals_by_address', methods=['POST'])
def get_hospitals_by_address():
    """Get hospitals by address (geocoding simulation)"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        severity = data.get('severity', 'YELLOW')
        
        # Simulate geocoding for common locations
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
        
        hospital_result = find_nearby_hospitals(user_lat, user_lng, severity=severity)
        hospital_result['geocoded_location'] = {'latitude': user_lat, 'longitude': user_lng}
        
        return jsonify(hospital_result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/google_places_search', methods=['POST'])
def google_places_search():
    """Search hospitals using Google Places API"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        location = data.get('location')  # Optional: lat,lng for nearby search
        
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'})
        
        # Google Places API key (imported from config)
        if not GOOGLE_PLACES_API_KEY or GOOGLE_PLACES_API_KEY == "YOUR_GOOGLE_PLACES_API_KEY":
            return jsonify({'success': False, 'error': 'Google Places API key not configured'})
        
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
            return jsonify({'success': False, 'error': f'Google Places API error: {data.get("error_message", "Unknown error")}'})
        
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
                hospital['distance_km'] = haversine_distance(
                    lat, lng, 
                    hospital['coordinates']['lat'], 
                    hospital['coordinates']['lng']
                )
            
            hospitals.append(hospital)
        
        return jsonify({
            'success': True,
            'hospitals': hospitals,
            'total_found': len(hospitals),
            'search_type': 'nearby' if location else 'text_search'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Google Places search failed'})

# Enhanced AI Triage Analysis System
def analyze_symptoms_with_ai(symptoms, age, pregnancy_status):
    """
    Sophisticated AI-powered symptom analysis using medical heuristics
    Returns: (severity, reason, confidence)
    """
    symptoms_lower = symptoms.lower()
    confidence = 0.85
    
    # RED FLAG - Critical Emergency Conditions
    red_criteria = {
        'cardiac': ['chest pain', 'chest pressure', 'chest tightness', 'heart attack', 'palpitations', 'rapid heartbeat'],
        'respiratory': ['difficulty breathing', 'shortness of breath', 'can\'t breathe', 'wheezing', 'choking'],
        'neurological': ['unconscious', 'fainting', 'loss of consciousness', 'confusion', 'seizure', 'stroke'],
        'trauma': ['severe bleeding', 'major injury', 'broken bone', 'head injury', 'spinal injury'],
        'abdominal_critical': ['severe abdominal pain', 'rupture', 'perforation', 'obstruction']
    }
    
    # YELLOW FLAG - Urgent but Non-Life-Threatening
    yellow_criteria = {
        'pain': ['moderate pain', 'mild pain', 'headache', 'migraine', 'back pain', 'joint pain'],
        'infection': ['fever', 'chills', 'sweats', 'infection', 'abscess'],
        'gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'stomach pain', 'constipation'],
        'respiratory_moderate': ['cough', 'sore throat', 'runny nose', 'congestion'],
        'other_urgent': ['dizziness', 'lightheaded', 'fatigue', 'weakness', 'rash']
    }
    
    # Check for RED conditions first (highest priority)
    for category, keywords in red_criteria.items():
        if any(keyword in symptoms_lower for keyword in keywords):
            # Specific reasoning based on category
            reasons = {
                'cardiac': 'Cardiac emergency detected - immediate medical intervention required',
                'respiratory': 'Respiratory distress detected - airway compromise possible',
                'neurological': 'Neurological emergency detected - potential brain injury',
                'trauma': 'Major trauma detected - uncontrolled bleeding or injury',
                'abdominal_critical': 'Acute abdominal emergency detected - possible organ rupture'
            }
            
            # Boost confidence for multiple symptoms
            symptom_count = sum(1 for keyword in keywords if keyword in symptoms_lower)
            if symptom_count > 1:
                confidence = min(0.95, confidence + 0.1)
            
            return 'RED', reasons.get(category, 'Critical symptoms detected - immediate emergency care required'), confidence
    
    # Check for YELLOW conditions
    for category, keywords in yellow_criteria.items():
        if any(keyword in symptoms_lower for keyword in keywords):
            # Specific reasoning based on category
            reasons = {
                'pain': 'Pain symptoms detected - medical evaluation needed for pain management',
                'infection': 'Infection symptoms detected - may require antibiotics or treatment',
                'gastrointestinal': 'GI symptoms detected - dehydration risk possible',
                'respiratory_moderate': 'Respiratory infection detected - may need medication',
                'other_urgent': 'Urgent symptoms detected - timely medical evaluation needed'
            }
            
            # Boost confidence for multiple symptoms
            symptom_count = sum(1 for keyword in keywords if keyword in symptoms_lower)
            if symptom_count > 1:
                confidence = min(0.90, confidence + 0.05)
            
            return 'YELLOW', reasons.get(category, 'Urgent symptoms detected - timely medical evaluation needed'), confidence
    
    # Pregnancy-specific considerations
    if pregnancy_status:
        pregnancy_keywords = ['pregnancy', 'pregnant', 'baby', 'fetal']
        if any(keyword in symptoms_lower for keyword in pregnancy_keywords):
            return 'YELLOW', 'Pregnancy-related symptoms require medical evaluation', confidence
        
        # Any symptoms in pregnant patients are automatically higher priority
        if symptoms_lower.strip():  # If there are any symptoms at all
            return 'YELLOW', 'Pregnant patient with symptoms - medical evaluation recommended', confidence
    
    # Age-specific considerations
    if age > 65:
        elderly_keywords = ['confusion', 'weakness', 'fall', 'dizziness', 'pain']
        if any(keyword in symptoms_lower for keyword in elderly_keywords):
            return 'YELLOW', 'Elderly patient with concerning symptoms - medical evaluation needed', confidence
    
    elif age < 12:
        pediatric_keywords = ['fever', 'difficulty breathing', 'lethargic', 'not eating', 'crying']
        if any(keyword in symptoms_lower for keyword in pediatric_keywords):
            return 'YELLOW', 'Pediatric patient with concerning symptoms - medical evaluation needed', confidence
    
    # GREEN - Non-urgent conditions
    if symptoms_lower.strip():
        green_reasons = [
            'Mild symptoms detected - routine care acceptable',
            'Non-urgent condition - can wait for regular appointment',
            'Minor symptoms - self-care may be appropriate'
        ]
        return 'GREEN', green_reasons[min(len(green_reasons)-1, len(symptoms_lower.split()) % len(green_reasons))], confidence
    
    # No symptoms provided
    return 'GREEN', 'No specific symptoms reported - routine care if needed', 0.70

def get_recommendations(severity):
    """Get medical recommendations based on severity"""
    recommendations = {
        'RED': [
            '🚑 Call emergency services immediately (999/911)',
            '🏥 Go to nearest emergency department',
            '⏰ Do not wait - time is critical',
            '📞 Have someone drive you if possible'
        ],
        'YELLOW': [
            '🏥 Visit urgent care or emergency department within 2-4 hours',
            '📞 Call your doctor for immediate appointment',
            '🚗 Have someone available to drive you',
            '💊 Bring current medications list'
        ],
        'GREEN': [
            '📅 Schedule regular doctor appointment',
            '🏠 Monitor symptoms at home',
            '💧 Stay hydrated and rest',
            '📞 Call doctor if symptoms worsen'
        ]
    }
    return recommendations.get(severity, [])

@app.route('/api/submit_symptoms', methods=['POST'])
def submit_symptoms():
    try:
        data = request.get_json()
        name = data.get('name', 'Anonymous')
        age = int(data.get('age', 0))
        symptoms = data.get('symptoms', '').lower()
        pregnancy_status = data.get('pregnancy_status', False)
        facility = data.get('facility', 'Moi Teaching and Referral Hospital')
        
        # Get additional context for AI analysis
        additional_context = {
            'facility': facility,
            'timestamp': datetime.now().isoformat(),
            'patient_name': name
        }
        
        # Use AI service if available, otherwise fallback to keyword analysis
        if AI_AVAILABLE and ai_service:
            ai_result = ai_service.get_ai_analysis(symptoms, age, pregnancy_status, additional_context)
            severity = ai_result.get('severity', 'GREEN')
            reason = ai_result.get('reason', 'Analysis completed')
            confidence = ai_result.get('confidence', 0.70)
            recommendations = ai_result.get('recommendations', [])
            ai_insights = ai_result.get('ai_insights', [])
            analysis_method = ai_result.get('analysis_method', 'unknown')
        else:
            # Fallback to original keyword analysis
            severity, reason, confidence = analyze_symptoms_with_ai(symptoms, age, pregnancy_status)
            recommendations = get_recommendations(severity)
            ai_insights = ['AI service not available - using keyword analysis']
            analysis_method = 'keyword_fallback'
        
        # Create patient record
        patient = {
            'patient_id': str(uuid.uuid4()),
            'name': name,
            'age': age,
            'symptoms': symptoms,
            'severity': severity,
            'triage_reason': reason,
            'status': 'waiting',
            'pregnancy_status': pregnancy_status,
            'facility': facility,
            'timestamp': datetime.now().isoformat(),
            'wait_time': 0,
            'ai_confidence': confidence,
            'analysis_method': analysis_method,
            'ai_insights': ai_insights
        }
        
        # Store patient in memory
        patients_db.append(patient)
        
        return jsonify({
            'success': True,
            'patient_id': patient['patient_id'],
            'severity': severity,
            'reason': reason,
            'confidence': confidence,
            'recommendations': recommendations,
            'ai_insights': ai_insights,
            'analysis_method': analysis_method,
            'model_used': ai_result.get('model_used', 'keyword_fallback') if AI_AVAILABLE and ai_service else 'keyword_fallback',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/arcgis_geocode', methods=['POST'])
def arcgis_geocode():
    data = request.get_json()
    address = data.get('address')
    if not address:
        return jsonify({'success': False, 'error': 'Address required'})
    
    result = geocode_address(address)
    return jsonify(result)

@app.route('/api/get_patients')
def get_patients():
    """Get all patients from memory"""
    try:
        # Calculate wait times for patients
        current_time = datetime.now()
        
        for patient in patients_db:
            # Calculate wait time in minutes
            patient_time = datetime.fromisoformat(patient['timestamp'].replace('Z', '+00:00') if patient['timestamp'].endswith('Z') else patient['timestamp'])
            wait_minutes = (current_time - patient_time).total_seconds() / 60
            patient['wait_time'] = max(0, round(wait_minutes))
        
        return jsonify(patients_db)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai_models', methods=['GET'])
def get_ai_models():
    """Get available AI models"""
    try:
        if AI_AVAILABLE and ai_service:
            models = ai_service.get_available_models()
            return jsonify({
                'success': True,
                'ai_available': True,
                'models': models,
                'current_model': ai_service.huggingface_service.model_name if ai_service.huggingface_service else None
            })
        else:
            return jsonify({
                'success': True,
                'ai_available': False,
                'models': [],
                'current_model': None,
                'message': 'AI service not available - using keyword analysis'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_analytics')
def get_analytics():
    """Get analytics data from real patient data"""
    try:
        if not patients_db:
            # Return default values if no patients
            return jsonify({
                'total_patients': 0,
                'red_patients': 0,
                'yellow_patients': 0,
                'green_patients': 0,
                'average_wait_time': 0,
                'bed_occupancy': 0,
                'doctor_to_patient_ratio': 0,
                'patient_flow_by_hour': {},
                'severity_distribution': {'RED': 0, 'YELLOW': 0, 'GREEN': 0},
                'facility_distribution': {},
                'peak_hours': [],
                'ai_analysis_stats': {
                    'total_analyzed': 0,
                    'huggingface_used': 0,
                    'keyword_fallback_used': 0,
                    'average_confidence': 0
                }
            })
        
        # Calculate real analytics from patient data
        total_patients = len(patients_db)
        red_patients = len([p for p in patients_db if p['severity'] == 'RED'])
        yellow_patients = len([p for p in patients_db if p['severity'] == 'YELLOW'])
        green_patients = len([p for p in patients_db if p['severity'] == 'GREEN'])
        
        # Calculate average wait time
        current_time = datetime.now()
        wait_times = []
        for patient in patients_db:
            patient_time = datetime.fromisoformat(patient['timestamp'].replace('Z', '+00:00') if patient['timestamp'].endswith('Z') else patient['timestamp'])
            wait_minutes = (current_time - patient_time).total_seconds() / 60
            wait_times.append(max(0, wait_minutes))
        
        average_wait_time = round(sum(wait_times) / len(wait_times), 1) if wait_times else 0
        
        # Calculate bed occupancy (mock calculation based on severity)
        bed_occupancy = min(95, (total_patients * 15) + (red_patients * 10))
        
        # Calculate doctor:patient ratio (mock calculation)
        doctor_to_patient_ratio = max(1.0, total_patients / 20) if total_patients > 0 else 0
        
        # Analyze patient flow by hour
        patient_flow_by_hour = {}
        for patient in patients_db:
            hour = datetime.fromisoformat(patient['timestamp'].replace('Z', '+00:00') if patient['timestamp'].endswith('Z') else patient['timestamp']).hour
            hour_key = f"{hour:02d}:00"
            patient_flow_by_hour[hour_key] = patient_flow_by_hour.get(hour_key, 0) + 1
        
        # Facility distribution
        facility_distribution = {}
        for patient in patients_db:
            facility = patient.get('facility', 'Unknown')
            facility_distribution[facility] = facility_distribution.get(facility, 0) + 1
        
        # Find peak hours
        if patient_flow_by_hour:
            peak_hours = sorted(patient_flow_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
        else:
            peak_hours = []
        
        # AI Analysis Statistics
        ai_stats = {
            'total_analyzed': total_patients,
            'huggingface_used': len([p for p in patients_db if p.get('analysis_method') == 'huggingface']),
            'keyword_fallback_used': len([p for p in patients_db if p.get('analysis_method') == 'keyword_fallback']),
            'average_confidence': round(sum([p.get('ai_confidence', 0) for p in patients_db]) / total_patients, 2) if total_patients > 0 else 0,
            'models_used': list(set([p.get('model_used', 'unknown') for p in patients_db]))
        }
        
        return jsonify({
            'total_patients': total_patients,
            'red_patients': red_patients,
            'yellow_patients': yellow_patients,
            'green_patients': green_patients,
            'average_wait_time': average_wait_time,
            'bed_occupancy': bed_occupancy,
            'doctor_to_patient_ratio': doctor_to_patient_ratio,
            'patient_flow_by_hour': patient_flow_by_hour,
            'severity_distribution': {'RED': red_patients, 'YELLOW': yellow_patients, 'GREEN': green_patients},
            'facility_distribution': facility_distribution,
            'peak_hours': [{'hour': hour, 'count': count} for hour, count in peak_hours],
            'ai_analysis_stats': ai_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update_patient_status', methods=['POST'])
def update_patient_status():
    """Update patient status"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        new_status = data.get('status')
        
        # Find and update patient in memory
        for patient in patients_db:
            if patient['patient_id'] == patient_id:
                patient['status'] = new_status
                return jsonify({
                    'success': True,
                    'message': 'Patient status updated successfully'
                })
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting SmartTriage AI with ArcGIS Integration...")
    print("🌐 Server: http://localhost:5000")
    print("🏥 Patient Portal: http://localhost:5000/patient")
    print("👩‍⚕️  Nurse Dashboard: http://localhost:5000/nurse")
    print("⚙️  Admin Panel: http://localhost:5000/admin")
    
    app.run(debug=True, host='0.0.0.0', port=5000)