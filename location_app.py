from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid
import math
import json

app = Flask(__name__)
app.secret_key = 'smarttriage-secret-key-2024'

# Hospital database with real coordinates and capabilities
HOSPITALS = [
    {
        'id': 'mtrh',
        'name': 'Moi Teaching and Referral Hospital',
        'address': 'Nairobi, Kenya',
        'coordinates': {'lat': -1.2921, 'lng': 36.8219},
        'phone': '+254-20-2717000',
        'emergency_services': True,
        'specialties': ['Emergency', 'Surgery', 'Pediatrics', 'Maternity', 'ICU'],
        'capacity': {'total': 650, 'available': 120},
        'wait_time_minutes': 45,
        'rating': 4.2
    },
    {
        'id': 'kenyatta',
        'name': 'Kenyatta National Hospital',
        'address': 'Hospital Road, Nairobi, Kenya',
        'coordinates': {'lat': -1.2717, 'lng': 36.8179},
        'phone': '+254-20-2726300',
        'emergency_services': True,
        'specialties': ['Emergency', 'Trauma', 'Cardiology', 'Neurology', 'ICU'],
        'capacity': {'total': 1800, 'available': 280},
        'wait_time_minutes': 60,
        'rating': 4.0
    },
    {
        'id': 'mbagathi',
        'name': 'Mbagathi County Hospital',
        'address': 'Nairobi, Kenya',
        'coordinates': {'lat': -1.3004, 'lng': 36.7654},
        'phone': '+254-20-2724251',
        'emergency_services': True,
        'specialties': ['Emergency', 'General Surgery', 'Pediatrics'],
        'capacity': {'total': 350, 'available': 80},
        'wait_time_minutes': 35,
        'rating': 3.8
    },
    {
        'id': 'nairobi',
        'name': 'Nairobi Hospital',
        'address': 'Argwings Kodhek Road, Nairobi, Kenya',
        'coordinates': {'lat': -1.2995, 'lng': 36.8167},
        'phone': '+254-20-2717151',
        'emergency_services': True,
        'specialties': ['Emergency', 'Cardiology', 'Oncology', 'Maternity'],
        'capacity': {'total': 450, 'available': 95},
        'wait_time_minutes': 40,
        'rating': 4.1
    },
    {
        'id': 'gertrude',
        'name': 'Gertrude\'s Children Hospital',
        'address': 'Muthaiga, Nairobi, Kenya',
        'coordinates': {'lat': -1.2655, 'lng': 36.8112},
        'phone': '+254-20-7110611',
        'emergency_services': True,
        'specialties': ['Pediatrics', 'Neonatal ICU', 'Emergency'],
        'capacity': {'total': 200, 'available': 45},
        'wait_time_minutes': 25,
        'rating': 4.5
    },
    {
        'id': 'karen',
        'name': 'Karen Hospital',
        'address': 'Karen, Nairobi, Kenya',
        'coordinates': {'lat': -1.3167, 'lng': 36.7333},
        'phone': '+254-20-7120000',
        'emergency_services': True,
        'specialties': ['Emergency', 'Maternity', 'General Surgery'],
        'capacity': {'total': 300, 'available': 70},
        'wait_time_minutes': 30,
        'rating': 4.3
    }
]

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates using Haversine formula"""
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def get_nearest_hospitals(user_lat, user_lng, max_distance=50, limit=10):
    """Get nearest hospitals to user location"""
    hospitals_with_distance = []
    
    for hospital in HOSPITALS:
        hospital_coords = hospital['coordinates']
        distance = calculate_distance(
            user_lat, user_lng,
            hospital_coords['lat'], hospital_coords['lng']
        )
        
        if distance <= max_distance:
            hospital_copy = hospital.copy()
            hospital_copy['distance_km'] = round(distance, 2)
            hospital_copy['travel_time_minutes'] = round(distance * 2)  # Assuming 30 km/h average speed
            hospital_copy['capacity_utilization'] = round(
                ((hospital['capacity']['total'] - hospital['capacity']['available']) / 
                 hospital['capacity']['total']) * 100, 1
            )
            hospitals_with_distance.append(hospital_copy)
    
    # Sort by distance, then by wait time
    hospitals_with_distance.sort(key=lambda x: (x['distance_km'], x['wait_time_minutes']))
    
    return hospitals_with_distance[:limit]

def get_hospital_recommendations(user_lat, user_lng, severity='YELLOW'):
    """Get hospital recommendations based on location and severity"""
    nearest_hospitals = get_nearest_hospitals(user_lat, user_lng)
    
    # Filter based on severity
    if severity == 'RED':
        # For critical cases, prioritize hospitals with emergency services and ICU
        recommended = [h for h in nearest_hospitals if h['emergency_services'] and 
                     ('ICU' in h['specialties'] or 'Trauma' in h['specialties'])]
    elif severity == 'YELLOW':
        # For urgent cases, prioritize hospitals with good capacity
        recommended = [h for h in nearest_hospitals if h['capacity']['available'] > 20]
    else:
        # For non-urgent cases, all hospitals are suitable
        recommended = nearest_hospitals
    
    return recommended[:5]  # Return top 5 recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/nurse')
def nurse():
    return render_template('nurse.html')

@app.route('/clinician')
def clinician():
    return render_template('clinician.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@app.route('/api/get_location_hospitals', methods=['POST'])
def get_location_hospitals():
    """Get hospitals based on user location"""
    try:
        data = request.get_json()
        
        # Get coordinates from request
        if 'latitude' in data and 'longitude' in data:
            user_lat = float(data['latitude'])
            user_lng = float(data['longitude'])
        elif 'lat' in data and 'lng' in data:
            user_lat = float(data['lat'])
            user_lng = float(data['lng'])
        else:
            return jsonify({
                'success': False,
                'error': 'Location coordinates required'
            }), 400
        
        # Get parameters
        max_distance = int(data.get('max_distance', 50))
        severity = data.get('severity', 'YELLOW')
        
        # Get nearest hospitals
        hospitals = get_nearest_hospitals(user_lat, user_lng, max_distance)
        
        # Get recommendations
        recommendations = get_hospital_recommendations(user_lat, user_lng, severity)
        
        return jsonify({
            'success': True,
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lng,
                'accuracy': data.get('accuracy', 'unknown')
            },
            'search_parameters': {
                'max_distance_km': max_distance,
                'severity': severity,
                'total_hospitals_found': len(hospitals)
            },
            'nearest_hospitals': hospitals,
            'recommended_hospitals': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Location processing error: {str(e)}'
        }), 500

@app.route('/api/get_hospitals_by_address', methods=['POST'])
def get_hospitals_by_address():
    """Get hospitals by address (geocoding simulation)"""
    try:
        data = request.get_json()
        address = data.get('address', '')
        
        # Simulate geocoding for common Nairobi locations
        location_coordinates = {
            'nairobi cbd': {'lat': -1.2921, 'lng': 36.8219},
            'westlands': {'lat': -1.2655, 'lng': 36.8112},
            'karen': {'lat': -1.3167, 'lng': 36.7333},
            'embakasi': {'lat': -1.2856, 'lng': 36.9251},
            'kileleshwa': {'lat': -1.2692, 'lng': 36.8036},
            'langata': {'lat': -1.2987, 'lng': 36.7469},
            'thika road': {'lat': -1.2611, 'lng': 36.8624},
            'mombasa road': {'lat': -1.3004, 'lng': 36.8167},
            'ngong road': {'lat': -1.2995, 'lng': 36.7833}
        }
        
        # Find matching location
        user_lat, user_lng = None, None
        for location, coords in location_coordinates.items():
            if location.lower() in address.lower():
                user_lat, user_lng = coords['lat'], coords['lng']
                break
        
        if user_lat is None:
            # Default to Nairobi CBD if no match found
            user_lat, user_lng = -1.2921, 36.8219
        
        # Get hospitals for the geocoded location
        hospitals = get_nearest_hospitals(user_lat, user_lng)
        
        return jsonify({
            'success': True,
            'address': address,
            'geocoded_location': {
                'latitude': user_lat,
                'longitude': user_lng
            },
            'nearest_hospitals': hospitals,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Address processing error: {str(e)}'
        }), 500

@app.route('/api/get_hospital_details/<hospital_id>')
def get_hospital_details(hospital_id):
    """Get detailed information about a specific hospital"""
    try:
        hospital = next((h for h in HOSPITALS if h['id'] == hospital_id), None)
        
        if not hospital:
            return jsonify({
                'success': False,
                'error': 'Hospital not found'
            }), 404
        
        # Add additional details
        hospital_details = hospital.copy()
        hospital_details.update({
            'services': {
                'emergency_24_7': hospital['emergency_services'],
                'ambulance_service': True,
                'pharmacy': True,
                'laboratory': True,
                'radiology': True,
                'blood_bank': hospital['id'] in ['mtrh', 'kenyatta']
            },
            'contact_info': {
                'phone': hospital['phone'],
                'email': f"info@{hospital['id']}.co.ke",
                'website': f"https://www.{hospital['id']}.co.ke"
            },
            'operating_hours': {
                'emergency': '24/7',
                'outpatient': '8:00 AM - 5:00 PM',
                'specialist': 'By Appointment'
            }
        })
        
        return jsonify({
            'success': True,
            'hospital': hospital_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Hospital details error: {str(e)}'
        }), 500

@app.route('/api/submit_symptoms', methods=['POST'])
def submit_symptoms():
    try:
        data = request.get_json()
        
        # Get user location if provided
        user_lat = data.get('latitude')
        user_lng = data.get('longitude')
        
        # Simple triage logic
        symptoms = data.get('symptoms', '').lower()
        age = int(data.get('age', 0))
        
        # Basic severity assessment
        if any(keyword in symptoms for keyword in ['chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding']):
            severity = 'RED'
            reason = 'Critical symptoms detected - immediate emergency care required'
        elif any(keyword in symptoms for keyword in ['moderate pain', 'headache', 'fever', 'nausea']):
            severity = 'YELLOW'
            reason = 'Urgent symptoms detected - timely medical evaluation needed'
        else:
            severity = 'GREEN'
            reason = 'Non-urgent symptoms - routine care acceptable'
        
        patient_id = str(uuid.uuid4())
        
        # Get hospital recommendations if location is provided
        recommendations = get_recommendations(severity)
        hospital_recommendations = []
        
        if user_lat and user_lng:
            hospital_recommendations = get_hospital_recommendations(user_lat, user_lng, severity)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'severity': severity,
            'reason': reason,
            'confidence': 0.85,
            'recommendations': recommendations,
            'hospital_recommendations': hospital_recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_recommendations(severity):
    recommendations = {
        'RED': [
            'Call emergency services (911) immediately',
            'Go to nearest emergency department',
            'Do not drive - call ambulance'
        ],
        'YELLOW': [
            'Seek medical evaluation within 1-2 hours',
            'Call primary care physician for appointment',
            'Monitor symptoms for changes'
        ],
        'GREEN': [
            'Schedule routine medical appointment',
            'Monitor symptoms at home',
            'Contact primary care physician for advice'
        ]
    }
    return recommendations.get(severity, ['Consult healthcare provider'])

if __name__ == '__main__':
    print("🚀 Starting SmartTriage AI with Enhanced Location Services...")
    print("🌐 Server: http://localhost:5000")
    print("🏥 Patient Portal: http://localhost:5000/patient")
    print("👩‍⚕️  Nurse Dashboard: http://localhost:5000/nurse")
    print("👨‍⚕️  Clinician View: http://localhost:5000/clinician")
    print("⚙️  Admin Panel: http://localhost:5000/admin")
    print("📊 Patient Monitoring: http://localhost:5000/monitoring")
    print("📍 Location API: /api/get_location_hospitals")
    print("🏥 Address API: /api/get_hospitals_by_address")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
