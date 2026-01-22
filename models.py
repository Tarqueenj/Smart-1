from datetime import datetime
import uuid

class PatientModel:
    def __init__(self, mongo):
        self.collection = mongo.db.patients
    
    def create(self, patient_data):
        patient_data['patient_id'] = str(uuid.uuid4())
        patient_data['created_at'] = datetime.now()
        patient_data['status'] = 'waiting'
        result = self.collection.insert_one(patient_data)
        return dict(result) if result else None
    
    def get_all(self):
        patients = list(self.collection.find({}))
        # Convert ObjectId to string for JSON serialization
        for patient in patients:
            patient['_id'] = str(patient['_id'])
        return patients
    
    def update_status(self, patient_id, new_status):
        result = self.collection.update_one(
            {'patient_id': patient_id},
            {'$set': {'status': new_status, 'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    def get_statistics(self, date_filter=None):
        match_stage = {}
        if date_filter:
            match_stage['$match'] = {
                'created_at': {'$gte': date_filter}
            }
        
        pipeline = [
            match_stage,
            {
                '$group': {
                    '_id': None,
                    'total_patients': {'$sum': 1},
                    'red_patients': {
                        '$sum': {
                            '$cond': [{'$eq': ['$severity', 'RED']}, 1, 0]
                        }
                    },
                    'yellow_patients': {
                        '$sum': {
                            '$cond': [{'$eq': ['$severity', 'YELLOW']}, 1, 0]
                        }
                    },
                    'green_patients': {
                        '$sum': {
                            '$cond': [{'$eq': ['$severity', 'GREEN']}, 1, 0]
                        }
                    },
                    'avg_wait_time': {'$avg': '$wait_time'}
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {
            'total_patients': 0,
            'red_patients': 0,
            'yellow_patients': 0,
            'green_patients': 0,
            'avg_wait_time': 0
        }

class FacilityModel:
    def __init__(self, mongo):
        self.collection = mongo.db.facilities
    
    def get_all_active(self):
        facilities = list(self.collection.find({'is_active': True}))
        # Convert ObjectId to string for JSON serialization
        for facility in facilities:
            facility['_id'] = str(facility['_id'])
        return facilities

class UserModel:
    def __init__(self, mongo):
        self.collection = mongo.db.users
    
    def authenticate(self, username, password):
        user = self.collection.find_one({'user_id': username})
        if user and user.get('password') == password:
            return user
        return None

class AnalyticsModel:
    def __init__(self, mongo):
        self.collection = mongo.db.analytics
    
    def record_patient_flow(self, timestamp, severity=None, event_type=None):
        event = {
            'timestamp': timestamp,
            'event_type': event_type or 'patient_flow',
            'severity': severity,
            'data': {
                'action': 'triage_completed'
            }
        }
        self.collection.insert_one(event)
    
    def get_analytics(self, date_filter=None):
        match_stage = {}
        if date_filter:
            match_stage['$match'] = {
                'timestamp': {'$gte': date_filter}
            }
        
        pipeline = [
            match_stage,
            {
                '$group': {
                    '_id': None,
                    'total_events': {'$sum': 1}
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return {
            'total_events': result[0]['total_events'] if result else 0,
            'date_filter': date_filter.isoformat() if date_filter else None
        }

def init_models(mongo):
    return {
        'patient': PatientModel(mongo),
        'facility': FacilityModel(mongo),
        'user': UserModel(mongo),
        'analytics': AnalyticsModel(mongo)
    }
