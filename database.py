from pymongo import MongoClient
from datetime import datetime, timedelta
import json

class DatabaseManager:
    """Database connection and initialization manager"""
    
    def __init__(self, uri='mongodb://localhost:27017/smarttriage_db'):
        self.uri = uri
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client.get_default_database()
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    def initialize_collections(self):
        """Initialize database collections and indexes"""
        if self.db is None:
            print("❌ Database not connected")
            return False
        
        try:
            # Create collections if they don't exist
            collections = [
                'patients',
                'users', 
                'facilities',
                'analytics',
                'audit_logs',
                'system_config'
            ]
            
            for collection_name in collections:
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(collection_name)
                    print(f"📁 Created collection: {collection_name}")
            
            # Create indexes for performance
            self._create_indexes()
            
            # Seed initial data
            self._seed_initial_data()
            
            print("✅ Database initialization complete")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            return False
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            print("🔧 Creating database indexes...")
            
            # Patients collection indexes
            self.db.patients.create_index([("patient_id", 1)], unique=True)
            self.db.patients.create_index([("timestamp", -1)])  # For recent patients
            self.db.patients.create_index([("severity", 1)])  # For triage priority
            self.db.patients.create_index([("status", 1)])  # For queue management
            self.db.patients.create_index([("facility", 1)])  # For facility-based queries
            self.db.patients.create_index([("severity", 1), ("timestamp", -1)])  # Compound index
            
            # Users collection indexes
            self.db.users.create_index([("user_id", 1)], unique=True)
            self.db.users.create_index([("email", 1)], unique=True)
            self.db.users.create_index([("role", 1)])  # For role-based queries
            self.db.users.create_index([("last_login", -1)])  # For activity tracking
            
            # Facilities collection indexes
            self.db.facilities.create_index([("facility_id", 1)], unique=True)
            self.db.facilities.create_index([("coordinates", "2dsphere")])  # For geospatial queries
            self.db.facilities.create_index([("is_active", 1)])  # For active facility filtering
            
            # Analytics collection indexes
            self.db.analytics.create_index([("timestamp", -1)])  # For time-based queries
            self.db.analytics.create_index([("event_type", 1)])  # For event filtering
            self.db.analytics.create_index([("user_id", 1), ("timestamp", -1)])  # Compound index
            
            # Audit logs collection indexes
            self.db.audit_logs.create_index([("timestamp", -1)])  # For log queries
            self.db.audit_logs.create_index([("user_id", 1)])  # For user activity
            self.db.audit_logs.create_index([("action", 1)])  # For action filtering
            
            print("📊 Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to create some indexes: {e}")
    
    def _seed_initial_data(self):
        """Seed initial data for demonstration"""
        try:
            # Check if data already exists
            if self.db.users.count_documents({}) > 0:
                print("📋 Database already contains data, skipping seed")
                return
            
            # Seed users
            users = [
                {
                    'user_id': 'user_001',
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@mtrh.ke',
                    'role': 'clinician',
                    'department': 'Emergency Medicine',
                    'license_number': 'MD12345',
                    'phone': '+254-712-345-678',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'last_login': None
                },
                {
                    'user_id': 'user_002',
                    'name': 'Grace Wanjiru',
                    'email': 'grace.wanjiru@mtrh.ke',
                    'role': 'nurse',
                    'department': 'Emergency',
                    'license_number': 'RN67890',
                    'phone': '+254-723-456-789',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'last_login': None
                },
                {
                    'user_id': 'user_003',
                    'name': 'David Kimani',
                    'email': 'david.kimani@mtrh.ke',
                    'role': 'admin',
                    'department': 'Administration',
                    'phone': '+254-734-567-890',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'last_login': None
                }
            ]
            
            self.db.users.insert_many(users)
            print(f"👥 Seeded {len(users)} users")
            
            # Seed facilities with real hospital coordinates
            facilities = [
                {
                    'facility_id': 'fac_001',
                    'name': 'Moi Teaching and Referral Hospital (MTRH)',
                    'type': 'Teaching Hospital',
                    'address': 'Eldoret, Kenya',
                    'coordinates': {'lat': 0.5175, 'lng': 35.2693},
                    'phone': '+254-53-30000',
                    'capacity': {
                        'emergency_beds': 50,
                        'inpatient_beds': 800,
                        'icu_beds': 20
                    },
                    'services': [
                        'Emergency Medicine',
                        'Surgery',
                        'Pediatrics',
                        'Maternity',
                        'ICU',
                        'Radiology',
                        'Laboratory'
                    ],
                    'base_wait_time': 45,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_002',
                    'name': 'Kenya Medical Research Institute (KEMRI)',
                    'type': 'Research Hospital',
                    'address': 'Nairobi, Kenya',
                    'coordinates': {'lat': -1.2921, 'lng': 36.8219},
                    'phone': '+254-20-2720000',
                    'capacity': {
                        'emergency_beds': 30,
                        'inpatient_beds': 200,
                        'icu_beds': 15
                    },
                    'services': [
                        'Emergency Medicine',
                        'Research',
                        'Laboratory',
                        'Radiology'
                    ],
                    'base_wait_time': 35,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_003',
                    'name': 'Nairobi Hospital',
                    'type': 'Private Hospital',
                    'address': 'Nairobi, Kenya',
                    'coordinates': {'lat': -1.2864, 'lng': 36.8172},
                    'phone': '+254-20-2845000',
                    'capacity': {
                        'emergency_beds': 25,
                        'inpatient_beds': 300,
                        'icu_beds': 12
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Surgery',
                        'Cardiology',
                        'Maternity',
                        'ICU'
                    ],
                    'base_wait_time': 25,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_004',
                    'name': 'Mombasa Hospital',
                    'type': 'Regional Hospital',
                    'address': 'Mombasa, Kenya',
                    'coordinates': {'lat': -4.0435, 'lng': 39.6682},
                    'phone': '+254-41-2311111',
                    'capacity': {
                        'emergency_beds': 20,
                        'inpatient_beds': 250,
                        'icu_beds': 8
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Medicine',
                        'Pediatrics',
                        'Maternity'
                    ],
                    'base_wait_time': 30,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_005',
                    'name': 'Kisumu County Hospital',
                    'type': 'County Referral Hospital',
                    'address': 'Kisumu, Kenya',
                    'coordinates': {'lat': -0.0917, 'lng': 34.7680},
                    'phone': '+254-57-2021000',
                    'capacity': {
                        'emergency_beds': 35,
                        'inpatient_beds': 400,
                        'icu_beds': 10
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Surgery',
                        'Pediatrics',
                        'Maternity',
                        'Laboratory'
                    ],
                    'base_wait_time': 40,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_006',
                    'name': 'Nakuru Level 5 Hospital',
                    'type': 'Level 5 Hospital',
                    'address': 'Nakuru, Kenya',
                    'coordinates': {'lat': -0.3031, 'lng': 36.0695},
                    'phone': '+254-51-2214000',
                    'capacity': {
                        'emergency_beds': 30,
                        'inpatient_beds': 350,
                        'icu_beds': 12
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Medicine',
                        'Surgery',
                        'Pediatrics'
                    ],
                    'base_wait_time': 35,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_007',
                    'name': 'Thika Level 5 Hospital',
                    'type': 'Level 5 Hospital',
                    'address': 'Thika, Kenya',
                    'coordinates': {'lat': -1.0339, 'lng': 37.0745},
                    'phone': '+254-67-2220000',
                    'capacity': {
                        'emergency_beds': 25,
                        'inpatient_beds': 300,
                        'icu_beds': 10
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Surgery',
                        'Maternity',
                        'Laboratory'
                    ],
                    'base_wait_time': 30,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_008',
                    'name': 'Garissa County Referral Hospital',
                    'type': 'County Referral Hospital',
                    'address': 'Garissa, Kenya',
                    'coordinates': {'lat': -0.4529, 'lng': 39.6460},
                    'phone': '+254-46-2210000',
                    'capacity': {
                        'emergency_beds': 20,
                        'inpatient_beds': 200,
                        'icu_beds': 6
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Medicine',
                        'Pediatrics',
                        'Maternity'
                    ],
                    'base_wait_time': 45,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_009',
                    'name': 'Kakamega County Referral Hospital',
                    'type': 'County Referral Hospital',
                    'address': 'Kakamega, Kenya',
                    'coordinates': {'lat': 0.2842, 'lng': 34.7519},
                    'phone': '+254-56-30000',
                    'capacity': {
                        'emergency_beds': 25,
                        'inpatient_beds': 280,
                        'icu_beds': 8
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Medicine',
                        'Surgery',
                        'Pediatrics',
                        'Maternity'
                    ],
                    'base_wait_time': 35,
                    'is_active': True,
                    'created_at': datetime.now()
                },
                {
                    'facility_id': 'fac_010',
                    'name': 'Meru Level 5 Hospital',
                    'type': 'Level 5 Hospital',
                    'address': 'Meru, Kenya',
                    'coordinates': {'lat': 0.0470, 'lng': 37.6553},
                    'phone': '+254-64-30000',
                    'capacity': {
                        'emergency_beds': 22,
                        'inpatient_beds': 250,
                        'icu_beds': 8
                    },
                    'services': [
                        'Emergency Medicine',
                        'General Medicine',
                        'Surgery',
                        'Pediatrics'
                    ],
                    'base_wait_time': 30,
                    'is_active': True,
                    'created_at': datetime.now()
                }
            ]
            
            self.db.facilities.insert_many(facilities)
            print(f"🏥 Seeded {len(facilities)} facilities")
            
            # Seed sample patients
            sample_patients = [
                {
                    'patient_id': 'patient_001',
                    'name': 'John Kamau',
                    'age': 45,
                    'symptoms': 'Severe chest pain radiating to left arm, shortness of breath, sweating',
                    'severity': 'RED',
                    'triage_reason': 'Possible cardiac emergency - immediate evaluation required',
                    'pregnancy_status': False,
                    'facility': 'MTRH',
                    'status': 'in-progress',
                    'timestamp': datetime.now() - timedelta(minutes=30),
                    'updated_at': datetime.now() - timedelta(minutes=15),
                    'clinician_notes': 'Patient presenting with classic cardiac symptoms. ECG ordered.',
                    'vitals': {
                        'blood_pressure': '160/95',
                        'heart_rate': 110,
                        'oxygen_saturation': 92,
                        'temperature': 37.2
                    },
                    'diagnosis': 'Suspected Acute Coronary Syndrome',
                    'treatment': 'Aspirin, Nitroglycerin, Cardiac enzymes ordered',
                    'discharge_time': None,
                    'wait_time_minutes': 15.0
                },
                {
                    'patient_id': 'patient_002',
                    'name': 'Mary Chebet',
                    'age': 28,
                    'symptoms': 'Fever, fast breathing, confusion, decreased urine output',
                    'severity': 'RED',
                    'triage_reason': 'Possible sepsis detected - requires immediate evaluation',
                    'pregnancy_status': False,
                    'facility': 'MTRH',
                    'status': 'waiting',
                    'timestamp': datetime.now() - timedelta(minutes=45),
                    'updated_at': datetime.now() - timedelta(minutes=45),
                    'clinician_notes': '',
                    'vitals': {
                        'blood_pressure': '90/60',
                        'heart_rate': 125,
                        'oxygen_saturation': 88,
                        'temperature': 39.5
                    },
                    'diagnosis': '',
                    'treatment': '',
                    'discharge_time': None,
                    'wait_time_minutes': 45.0
                },
                {
                    'patient_id': 'patient_003',
                    'name': 'Grace Njeri',
                    'age': 32,
                    'symptoms': 'Moderate headache, nausea, sensitivity to light',
                    'severity': 'YELLOW',
                    'triage_reason': 'Urgent symptom detected - timely evaluation recommended',
                    'pregnancy_status': True,
                    'facility': 'MTRH',
                    'status': 'waiting',
                    'timestamp': datetime.now() - timedelta(minutes=20),
                    'updated_at': datetime.now() - timedelta(minutes=20),
                    'clinician_notes': '',
                    'vitals': {
                        'blood_pressure': '120/80',
                        'heart_rate': 85,
                        'oxygen_saturation': 98,
                        'temperature': 37.0
                    },
                    'diagnosis': '',
                    'treatment': '',
                    'discharge_time': None,
                    'wait_time_minutes': 20.0
                },
                {
                    'patient_id': 'patient_004',
                    'name': 'Samuel Kiprop',
                    'age': 65,
                    'symptoms': 'Mild back pain, difficulty sleeping',
                    'severity': 'GREEN',
                    'triage_reason': 'Non-emergency symptoms - routine evaluation appropriate',
                    'pregnancy_status': False,
                    'facility': 'MTRH',
                    'status': 'waiting',
                    'timestamp': datetime.now() - timedelta(minutes=60),
                    'updated_at': datetime.now() - timedelta(minutes=60),
                    'clinician_notes': '',
                    'vitals': {
                        'blood_pressure': '135/85',
                        'heart_rate': 72,
                        'oxygen_saturation': 97,
                        'temperature': 36.8
                    },
                    'diagnosis': '',
                    'treatment': '',
                    'discharge_time': None,
                    'wait_time_minutes': 60.0
                }
            ]
            
            self.db.patients.insert_many(sample_patients)
            print(f"👤 Seeded {len(sample_patients)} sample patients")
            
            # Seed system configuration
            system_config = {
                'config_id': 'system_001',
                'version': '1.0.0',
                'ai_model_version': '2.4.1',
                'settings': {
                    'auto_refresh_interval': 30,  # seconds
                    'max_patients_per_page': 50,
                    'enable_voice_input': True,
                    'supported_languages': ['en', 'sw'],  # English, Swahili
                    'emergency_threshold': 5,  # patients
                    'backup_enabled': True,
                    'maintenance_mode': False
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            self.db.system_config.insert_one(system_config)
            print("⚙️  Seeded system configuration")
            
            print("✅ Initial data seeding complete")
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to seed initial data: {e}")
    
    def get_database_info(self):
        """Get database information and statistics"""
        if self.db is None:
            return None
        
        try:
            stats = {
                'database_name': self.db.name,
                'collections': {},
                'server_info': self.client.server_info()
            }
            
            # Get collection statistics
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                stats['collections'][collection_name] = {
                    'document_count': collection.count_documents({}),
                    'indexes': list(collection.list_indexes())
                }
            
            return stats
            
        except Exception as e:
            print(f"❌ Failed to get database info: {e}")
            return None
    
    def backup_database(self, backup_path=None):
        """Create database backup (mock implementation)"""
        try:
            if not backup_path:
                backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'database': self.db.name,
                'collections': {}
            }
            
            # Export all collections
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                documents = list(collection.find({}))
                
                # Convert ObjectId to string for JSON serialization
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    if 'timestamp' in doc and hasattr(doc['timestamp'], 'isoformat'):
                        doc['timestamp'] = doc['timestamp'].isoformat()
                    if 'created_at' in doc and hasattr(doc['created_at'], 'isoformat'):
                        doc['created_at'] = doc['created_at'].isoformat()
                    if 'updated_at' in doc and hasattr(doc['updated_at'], 'isoformat'):
                        doc['updated_at'] = doc['updated_at'].isoformat()
                
                backup_data['collections'][collection_name] = documents
            
            # Write backup to file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"💾 Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager()
