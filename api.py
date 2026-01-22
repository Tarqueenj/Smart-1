from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import init_models
from ai_engine import triage_engine
from auth import token_required, role_required, log_user_activity
import json

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize models (will be passed from app)
models = None

def init_api(mongo):
    """Initialize API with database models"""
    global models
    models = init_models(mongo)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email') or data.get('username')  # Accept both email and username
        password = data.get('password')
        role = data.get('role')  # Get role for demo purposes
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Get user from database
        user = models['user'].get_by_email(email)
        
        # Create demo user if not exists (for development)
        if not user:
            demo_user = {
                'user_id': f"user_{email.replace('@', '_').replace('.', '_')}",
                'name': email.split('@')[0].title(),
                'email': email,
                'role': role or 'nurse',  # Default to nurse if no role specified
                'department': 'Emergency',
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            user = models['user'].create(demo_user)
        
        # In production, verify password hash
        # if not auth_manager.verify_password(password, user.get('password_hash', '')):
        #     return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        from auth import auth_manager
        token = auth_manager.generate_token(user['user_id'], user['role'])
        
        # Update last login
        models['user'].update_last_login(user['user_id'])
        
        # Log activity
        log_user_activity(user['user_id'], 'login')
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'user': {
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'email': user['email'],
                    'role': user['role'],
                    'department': user.get('department')
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@api_bp.route('/submit_symptoms', methods=['POST'])
def submit_symptoms():
    """Submit patient symptoms for AI triage"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'age', 'symptoms']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Analyze symptoms with AI engine
        assessment = triage_engine.analyze_symptoms(
            data['symptoms'],
            data['age'],
            data.get('pregnancy_status', False)
        )
        
        # Create patient record
        patient_data = {
            'name': data['name'],
            'age': data['age'],
            'symptoms': data['symptoms'],
            'severity': assessment['severity'],
            'triage_reason': assessment['reason'],
            'pregnancy_status': data.get('pregnancy_status', False),
            'facility': data.get('facility', 'MTRH')
        }
        
        patient = models['patient'].create(patient_data)
        
        # Record analytics
        models['analytics'].record_patient_flow(
            datetime.now(),
            assessment['severity'],
            'arrival'
        )
        
        return jsonify({
            'success': True,
            'patient_id': patient['patient_id'],
            'assessment': assessment,
            'patient_info': {
                'name': patient['name'],
                'age': patient['age'],
                'severity': patient['severity'],
                'timestamp': patient['timestamp'].isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Symptom submission failed', 'details': str(e)}), 500

@api_bp.route('/patients', methods=['GET'])
@token_required
@role_required('nurse', 'clinician', 'admin')
def get_patients():
    """Get all patients with optional filters"""
    try:
        # Get query parameters
        filters = {}
        
        severity = request.args.get('severity')
        if severity and severity != 'all':
            filters['severity'] = severity
        
        status = request.args.get('status')
        if status and status != 'all':
            filters['status'] = status
        
        facility = request.args.get('facility')
        if facility:
            filters['facility'] = facility
        
        # Get patients
        patients = models['patient'].get_all(filters)
        
        return jsonify({
            'success': True,
            'patients': patients,
            'total_count': len(patients)
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve patients', 'details': str(e)}), 500

@api_bp.route('/patients/<patient_id>', methods=['GET'])
@token_required
@role_required('nurse', 'clinician', 'admin')
def get_patient(patient_id):
    """Get specific patient details"""
    try:
        patient = models['patient'].get_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        return jsonify({
            'success': True,
            'patient': patient
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve patient', 'details': str(e)}), 500

@api_bp.route('/patients/<patient_id>/status', methods=['PUT'])
@token_required
@role_required('nurse', 'clinician')
def update_patient_status(patient_id):
    """Update patient status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['waiting', 'in-progress', 'completed', 'transferred']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # Update patient status
        success = models['patient'].update_status(
            patient_id,
            new_status,
            request.current_user['user_id']
        )
        
        if not success:
            return jsonify({'error': 'Patient not found or update failed'}), 404
        
        # Record analytics if completed
        if new_status == 'completed':
            models['analytics'].record_patient_flow(
                datetime.now(),
                None,  # Will be determined from patient record
                'discharge'
            )
        
        # Log activity
        log_user_activity(
            request.current_user['user_id'],
            'update_patient_status',
            {'patient_id': patient_id, 'new_status': new_status}
        )
        
        return jsonify({
            'success': True,
            'message': 'Patient status updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to update patient status', 'details': str(e)}), 500

@api_bp.route('/patients/<patient_id>/notes', methods=['PUT'])
@token_required
@role_required('clinician')
def add_clinician_notes(patient_id):
    """Add clinician notes to patient record"""
    try:
        data = request.get_json()
        notes = data.get('notes')
        diagnosis = data.get('diagnosis')
        treatment = data.get('treatment')
        
        if not notes:
            return jsonify({'error': 'Notes are required'}), 400
        
        # Add notes to patient record
        success = models['patient'].add_clinician_notes(
            patient_id,
            notes,
            diagnosis,
            treatment,
            request.current_user['user_id']
        )
        
        if not success:
            return jsonify({'error': 'Patient not found or update failed'}), 404
        
        # Log activity
        log_user_activity(
            request.current_user['user_id'],
            'add_clinician_notes',
            {'patient_id': patient_id, 'notes_length': len(notes)}
        )
        
        return jsonify({
            'success': True,
            'message': 'Clinician notes added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to add clinician notes', 'details': str(e)}), 500

@api_bp.route('/analytics', methods=['GET'])
@token_required
@role_required('admin')
def get_analytics():
    """Get comprehensive analytics data"""
    try:
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        else:
            end_date = datetime.now()
        
        # Get patient statistics
        patient_stats = models['patient'].get_statistics(start_date, end_date)
        
        # Get hourly flow data
        hourly_flow = models['analytics'].get_hourly_flow(start_date, end_date)
        
        # Get severity distribution
        severity_dist = models['analytics'].get_severity_distribution(start_date, end_date)
        
        # Mock additional analytics data
        analytics_data = {
            'patient_statistics': patient_stats,
            'hourly_flow': hourly_flow,
            'severity_distribution': severity_dist,
            'resource_utilization': {
                'bed_occupancy': 78,
                'doctor_to_patient_ratio': 1.8,
                'nurse_to_patient_ratio': 4.2,
                'average_length_of_stay': 4.5  # hours
            },
            'performance_metrics': {
                'triage_accuracy': 94.2,
                'average_processing_time': 2.3,  # seconds
                'system_uptime': 99.7,
                'user_satisfaction': 4.6  # out of 5
            },
            'peak_hours': {
                'morning_peak': '10:00-12:00',
                'afternoon_peak': '14:00-16:00',
                'busiest_day': 'Wednesday'
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics_data,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve analytics', 'details': str(e)}), 500

@api_bp.route('/facilities', methods=['GET'])
def get_facilities():
    """Get nearby facilities with wait times"""
    try:
        # Get coordinates from query parameters (default to Eldoret)
        lat = float(request.args.get('lat', 0.5175))
        lng = float(request.args.get('lng', 35.2693))
        max_distance = int(request.args.get('max_distance', 50))
        
        # Get nearby facilities
        facilities = models['facility'].get_nearby(lat, lng, max_distance)
        
        # Add mock wait time predictions
        for facility in facilities:
            # Simulate AI-based wait time prediction
            base_wait = facility.get('base_wait_time', 30)
            current_load = hash(facility['name'] + str(datetime.now().hour)) % 50
            facility['estimated_wait_time'] = base_wait + current_load
            facility['confidence_score'] = 0.85  # Mock confidence
            facility['recommended'] = facility['estimated_wait_time'] < 45
        
        return jsonify({
            'success': True,
            'facilities': facilities,
            'search_location': {'lat': lat, 'lng': lng}
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve facilities', 'details': str(e)}), 500

@api_bp.route('/search', methods=['GET'])
@token_required
def search():
    """Quick search functionality"""
    try:
        query = request.args.get('q', '').lower()
        search_type = request.args.get('type', 'all')
        
        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        results = []
        
        # Search patients
        if search_type in ['all', 'patients']:
            patients = models['patient'].get_all()
            patient_results = [
                {
                    'type': 'patient',
                    'id': p['patient_id'],
                    'title': p['name'],
                    'description': f"Age {p['age']}, {p['severity']} priority",
                    'severity': p['severity'],
                    'timestamp': p['timestamp']
                }
                for p in patients
                if query in p['name'].lower() or query in p['symptoms'].lower()
            ]
            results.extend(patient_results)
        
        # Mock search for other types
        if search_type in ['all', 'symptoms']:
            # Mock symptom search results
            symptom_results = [
                {
                    'type': 'symptom',
                    'id': 'chest_pain',
                    'title': 'Chest Pain',
                    'description': 'Emergency symptom requiring immediate evaluation'
                },
                {
                    'type': 'symptom',
                    'id': 'difficulty_breathing',
                    'title': 'Difficulty Breathing',
                    'description': 'Respiratory distress - immediate attention needed'
                }
            ]
            results.extend([r for r in symptom_results if query in r['title'].lower()])
        
        if search_type in ['all', 'actions']:
            # Mock action search results
            action_results = [
                {
                    'type': 'action',
                    'id': 'order_labs',
                    'title': 'Order Laboratory Tests',
                    'description': 'Request blood work and other lab tests'
                },
                {
                    'type': 'action',
                    'id': 'request_imaging',
                    'title': 'Request Imaging Studies',
                    'description': 'Order X-rays, CT scans, or other imaging'
                }
            ]
            results.extend([r for r in action_results if query in r['title'].lower()])
        
        return jsonify({
            'success': True,
            'results': results[:20],  # Limit to 20 results
            'total_count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@api_bp.route('/updates', methods=['GET'])
@token_required
def get_updates():
    """Get real-time updates for dashboard"""
    try:
        # Get last update timestamp
        since = request.args.get('since')
        if since:
            since = datetime.fromisoformat(since)
        else:
            since = datetime.now() - timedelta(minutes=5)
        
        updates = []
        
        # Get recent patient arrivals
        recent_patients = models['patient'].get_all(
            filters={'timestamp': {'$gte': since}}
        )
        
        for patient in recent_patients:
            updates.append({
                'type': 'patient_arrival',
                'message': f"New patient: {patient['name']} ({patient['severity']} priority)",
                'severity': patient['severity'],
                'timestamp': patient['timestamp'],
                'data': patient
            })
        
        # Mock system updates
        if datetime.now().hour % 4 == 0:  # Every 4 hours
            updates.append({
                'type': 'system_update',
                'message': 'System performance optimized',
                'severity': 'info',
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'updates': updates,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to get updates', 'details': str(e)}), 500

@api_bp.route('/audit_logs', methods=['GET'])
@token_required
@role_required('admin')
def get_audit_logs():
    """Get audit logs for compliance"""
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        else:
            start_date = datetime.now() - timedelta(days=7)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        else:
            end_date = datetime.now()
        
        if user_id:
            logs = models['audit_log'].get_user_actions(user_id, start_date, end_date)
        else:
            # Mock comprehensive audit logs
            logs = [
                {
                    'user_id': 'user_001',
                    'action': 'login',
                    'timestamp': datetime.now().isoformat(),
                    'ip_address': '192.168.1.100'
                },
                {
                    'user_id': 'user_002',
                    'action': 'update_patient_status',
                    'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'details': {'patient_id': 'patient_123', 'new_status': 'completed'}
                }
            ]
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total_count': len(logs)
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve audit logs', 'details': str(e)}), 500
