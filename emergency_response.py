from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import uuid

class EmergencyResponseSystem:
    """Comprehensive emergency response protocols and management system"""
    
    def __init__(self):
        self.emergency_protocols = self._load_emergency_protocols()
        self.response_teams = self._initialize_response_teams()
        self.equipment_inventory = self._load_equipment_inventory()
        self.emergency_contacts = self._load_emergency_contacts()
        self.disaster_plans = self._load_disaster_plans()
        self.mass_casualty_protocols = self._load_mass_casualty_protocols()
    
    def _load_emergency_protocols(self) -> Dict:
        """Load comprehensive emergency response protocols"""
        return {
            'cardiac_arrest': {
                'code': 'BLUE',
                'priority': 'critical',
                'response_time': '< 2 minutes',
                'team_required': ['code_blue_team', 'respiratory_therapist', 'cardiologist'],
                'equipment': ['defibrillator', 'crash_cart', 'intubation_kit', 'monitor'],
                'medications': ['epinephrine', 'amiodarone', 'atropine', 'lidocaine'],
                'procedures': [
                    'Check responsiveness and breathing',
                    'Call code blue',
                    'Start CPR (30:2 ratio)',
                    'Apply defibrillator pads',
                    'Establish IV/IO access',
                    'Administer medications per ACLS protocol',
                    'Consider advanced airway',
                    'Monitor rhythm and treat accordingly'
                ],
                'documentation_required': [
                    'Time of arrest',
                    'CPR duration',
                    'Medications given',
                    'Rhythm changes',
                    'Team members present',
                    'Patient outcome'
                ]
            },
            'respiratory_arrest': {
                'code': 'BLUE',
                'priority': 'critical',
                'response_time': '< 2 minutes',
                'team_required': ['code_blue_team', 'respiratory_therapist'],
                'equipment': ['bag_valve_mask', 'oxygen', 'intubation_kit', 'suction'],
                'medications': ['succinylcholine', 'rocuronium', 'etomidate'],
                'procedures': [
                    'Assess airway patency',
                    'Provide ventilations with BVM',
                    'Administer 100% oxygen',
                    'Prepare for intubation',
                    'Monitor vital signs',
                    'Consider rapid sequence intubation',
                    'Confirm tube placement',
                    'Secure airway'
                ]
            },
            'severe_bleeding': {
                'code': 'RED',
                'priority': 'critical',
                'response_time': '< 5 minutes',
                'team_required': ['trauma_team', 'surgeon', 'anesthesiologist'],
                'equipment': ['pressure_dressings', 'tourniquets', 'iv_fluids', 'blood_products'],
                'medications': ['tranexamic_acid', 'blood_products', 'crystalloids'],
                'procedures': [
                    'Apply direct pressure',
                    'Elevate injured limb',
                    'Apply tourniquet if needed',
                    'Establish large bore IV access',
                    'Draw blood for type and cross',
                    'Administer fluids/blood',
                    'Prepare for surgical intervention',
                    'Monitor for shock'
                ]
            },
            'anaphylaxis': {
                'code': 'YELLOW',
                'priority': 'urgent',
                'response_time': '< 5 minutes',
                'team_required': ['emergency_team', 'respiratory_therapist'],
                'equipment': ['epinephrine_autoinjector', 'oxygen', 'iv_supplies'],
                'medications': ['epinephrine', 'diphenhydramine', 'corticosteroids', 'albuterol'],
                'procedures': [
                    'Stop allergen exposure',
                    'Administer epinephrine IM',
                    'Call emergency response team',
                    'Administer oxygen',
                    'Position patient supine with legs elevated',
                    'Establish IV access',
                    'Administer antihistamines',
                    'Monitor for biphasic reaction'
                ]
            },
            'seizure': {
                'code': 'YELLOW',
                'priority': 'urgent',
                'response_time': '< 5 minutes',
                'team_required': ['emergency_team', 'neurologist'],
                'equipment': ['oxygen', 'suction', 'bedside_monitor', 'padding'],
                'medications': ['lorazepam', 'diazepam', 'phenytoin', 'levetiracetam'],
                'procedures': [
                    'Ensure patient safety',
                    'Protect airway',
                    'Do not restrain patient',
                    'Time the seizure',
                    'Administer oxygen if needed',
                    'Position patient on side',
                    'Consider benzodiazepines if prolonged',
                    'Monitor vital signs',
                    'Check for injuries'
                ]
            },
            'stroke': {
                'code': 'STROKE',
                'priority': 'critical',
                'response_time': '< 10 minutes',
                'team_required': ['stroke_team', 'neurologist', 'radiology'],
                'equipment': ['ct_scanner', 'mri', 'neuro_monitor', 'iv_pump'],
                'medications': ['tpa', 'aspirin', 'blood_pressure_meds'],
                'procedures': [
                    'Perform rapid stroke assessment (NIHSS)',
                    'Check blood glucose',
                    'Establish IV access',
                    'Order emergent CT/MRI',
                    'Consider thrombolysis if within window',
                    'Monitor neurological status',
                    'Prepare for interventional radiology',
                    'Document time of onset'
                ]
            },
            'trauma': {
                'code': 'TRAUMA',
                'priority': 'critical',
                'response_time': '< 5 minutes',
                'team_required': ['trauma_team', 'surgeon', 'anesthesiologist', 'radiology'],
                'equipment': ['cervical_collar', 'spine_board', 'ultrasound', 'chest_tubes'],
                'medications': ['analgesics', 'sedatives', 'antibiotics', 'blood_products'],
                'procedures': [
                    'Primary survey (ABCDE)',
                    'Cervical spine immobilization',
                    'Control external bleeding',
                    'Establish airway if needed',
                    'Insert chest tubes if indicated',
                    'Perform FAST ultrasound',
                    'Order imaging studies',
                    'Prepare for surgery'
                ]
            }
        }
    
    def _initialize_response_teams(self) -> Dict:
        """Initialize emergency response teams"""
        return {
            'code_blue_team': {
                'members': ['team_leader', 'compressor', 'airway_manager', 'medication_administrator', 'recorder'],
                'activation_criteria': ['cardiac_arrest', 'respiratory_arrest'],
                'response_time_target': 120,  # seconds
                'training_required': ['ACLS', 'BLS', 'Airway_management']
            },
            'trauma_team': {
                'members': ['trauma_surgeon', 'emergency_physician', 'anesthesiologist', 'nurse_coordinator', 'radiologist'],
                'activation_criteria': ['major_trauma', 'multiple_injuries', 'penetrating_trauma'],
                'response_time_target': 300,  # seconds
                'training_required': ['ATLS', 'Trauma_care', 'Surgical_skills']
            },
            'stroke_team': {
                'members': ['neurologist', 'emergency_physician', 'nurse_coordinator', 'radiology_technician'],
                'activation_criteria': ['suspected_stroke', 'neurological_deficits'],
                'response_time_target': 600,  # seconds
                'training_required': ['Stroke_certification', 'Neurology', 'Emergency_medicine']
            },
            'rapid_response_team': {
                'members': ['icu_nurse', 'respiratory_therapist', 'physician'],
                'activation_criteria': ['clinical_deterioration', 'vital_sign_abnormalities'],
                'response_time_target': 300,  # seconds
                'training_required': ['Critical_care', 'Rapid_response', 'Assessment_skills']
            }
        }
    
    def _load_equipment_inventory(self) -> Dict:
        """Load emergency equipment inventory"""
        return {
            'life_support': {
                'defibrillator': {
                    'quantity': 5,
                    'location': ['ed', 'icu', 'floors'],
                    'maintenance_interval': 'monthly',
                    'status': 'operational'
                },
                'ventilator': {
                    'quantity': 10,
                    'location': ['icu', 'ed', 'or'],
                    'maintenance_interval': 'weekly',
                    'status': 'operational'
                },
                'crash_cart': {
                    'quantity': 8,
                    'location': ['ed', 'floors', 'icu'],
                    'maintenance_interval': 'daily',
                    'status': 'checked_daily'
                }
            },
            'airway_equipment': {
                'intubation_kit': {
                    'quantity': 20,
                    'location': ['ed', 'or', 'icu'],
                    'maintenance_interval': 'per_use',
                    'status': 'sterile'
                },
                'bag_valve_mask': {
                    'quantity': 15,
                    'location': ['ed', 'floors', 'icu'],
                    'maintenance_interval': 'weekly',
                    'status': 'cleaned'
                }
            },
            'monitoring': {
                'cardiac_monitor': {
                    'quantity': 25,
                    'location': ['ed', 'icu', 'floors'],
                    'maintenance_interval': 'monthly',
                    'status': 'calibrated'
                }
            }
        }
    
    def _load_emergency_contacts(self) -> Dict:
        """Load emergency contact information"""
        return {
            'internal': {
                'hospital_operator': '0',
                'security': '5555',
                'maintenance': '6666',
                'lab_emergency': '7777',
                'radiology_emergency': '8888',
                'blood_bank': '9999'
            },
            'external': {
                'ambulance_service': '999',
                'fire_department': '997',
                'police': '999',
                'poison_control': '0800-POISON',
                'disaster_management': '0800-DISASTER'
            }
        }
    
    def _load_disaster_plans(self) -> Dict:
        """Load disaster response plans"""
        return {
            'mass_casualty_incident': {
                'activation_triggers': ['>10_patients', 'major_accident', 'natural_disaster'],
                'command_structure': {
                    'incident_commander': 'chief_medical_officer',
                    'triage_officer': 'senior_emergency_physician',
                    'treatment_area_leaders': ['ed_director', 'icu_director'],
                    'logistics_coordinator': 'nursing_director'
                },
                'phases': {
                    'phase_1': 'Alert and activation (0-30min)',
                    'phase_2': 'Patient triage and stabilization (30-90min)',
                    'phase_3': 'Definitive care (90min-4hours)',
                    'phase_4': 'Recovery and decontamination (4hours+)'
                }
            },
            'internal_disaster': {
                'types': ['fire', 'flood', 'power_outage', 'equipment_failure'],
                'evacuation_zones': ['zone_a', 'zone_b', 'zone_c'],
                'assembly_points': ['main_lobby', 'parking_lot_a', 'parking_lot_b']
            }
        }
    
    def _load_mass_casualty_protocols(self) -> Dict:
        """Load mass casualty incident protocols"""
        return {
            'triage_system': 'START',
            'triage_categories': {
                'immediate': {
                    'color': 'RED',
                    'description': 'Immediate life-saving intervention required',
                    'examples': ['airway_obstruction', 'severe_bleeding', 'shock']
                },
                'delayed': {
                    'color': 'YELLOW',
                    'description': 'Serious but stable injuries',
                    'examples': ['major_fractures', 'moderate_burns', 'conscious_head_injury']
                },
                'minor': {
                    'color': 'GREEN',
                    'description': 'Minor injuries, can wait',
                    'examples': ['minor_fractures', 'small_burns', 'lacerations']
                },
                'expectant': {
                    'color': 'BLACK',
                    'description': 'Unlikely to survive with available resources',
                    'examples': ['cardiac_arrest', 'severe_head_injury', 'massive_burns']
                }
            },
            'resource_allocation': {
                'red_zone': '50% of resources',
                'yellow_zone': '30% of resources',
                'green_zone': '15% of resources',
                'black_zone': '5% of resources'
            }
        }
    
    def activate_emergency_protocol(self, emergency_type: str, patient_id: str, 
                                 location: str, additional_info: Dict = None) -> Dict:
        """
        Activate emergency protocol for specific emergency type
        
        Args:
            emergency_type: Type of emergency (cardiac_arrest, trauma, etc.)
            patient_id: Patient identifier
            location: Location within facility
            additional_info: Additional emergency information
            
        Returns:
            Dictionary with activation response and instructions
        """
        if emergency_type not in self.emergency_protocols:
            return {
                'success': False,
                'error': f'Unknown emergency type: {emergency_type}',
                'timestamp': datetime.now().isoformat()
            }
        
        protocol = self.emergency_protocols[emergency_type]
        activation_id = str(uuid.uuid4())
        
        # Create activation record
        activation_record = {
            'activation_id': activation_id,
            'emergency_type': emergency_type,
            'code': protocol['code'],
            'patient_id': patient_id,
            'location': location,
            'activation_time': datetime.now(),
            'priority': protocol['priority'],
            'team_required': protocol['team_required'],
            'equipment_needed': protocol['equipment'],
            'medications_needed': protocol['medications'],
            'procedures': protocol['procedures'],
            'additional_info': additional_info or {},
            'status': 'activated'
        }
        
        # Determine response teams to activate
        teams_to_activate = self._determine_response_teams(emergency_type)
        
        # Check equipment availability
        equipment_status = self._check_equipment_availability(protocol['equipment'])
        
        # Generate immediate actions
        immediate_actions = self._generate_immediate_actions(emergency_type, activation_record)
        
        # Calculate estimated response time
        estimated_response_time = self._calculate_response_time(emergency_type, location)
        
        return {
            'success': True,
            'activation_id': activation_id,
            'emergency_code': protocol['code'],
            'priority': protocol['priority'],
            'teams_activated': teams_to_activate,
            'equipment_status': equipment_status,
            'immediate_actions': immediate_actions,
            'estimated_response_time': estimated_response_time,
            'procedures': protocol['procedures'],
            'medications': protocol['medications'],
            'documentation_required': protocol.get('documentation_required', []),
            'emergency_contacts': self.emergency_contacts['internal'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _determine_response_teams(self, emergency_type: str) -> List[str]:
        """Determine which response teams to activate"""
        team_mapping = {
            'cardiac_arrest': ['code_blue_team'],
            'respiratory_arrest': ['code_blue_team'],
            'severe_bleeding': ['trauma_team'],
            'anaphylaxis': ['rapid_response_team'],
            'seizure': ['rapid_response_team'],
            'stroke': ['stroke_team'],
            'trauma': ['trauma_team']
        }
        
        return team_mapping.get(emergency_type, ['rapid_response_team'])
    
    def _check_equipment_availability(self, required_equipment: List[str]) -> Dict:
        """Check availability of required emergency equipment"""
        equipment_status = {}
        
        for equipment in required_equipment:
            # Check if equipment is in inventory
            found = False
            for category, items in self.equipment_inventory.items():
                if equipment in items:
                    equipment_status[equipment] = {
                        'available': items[equipment]['quantity'] > 0,
                        'quantity': items[equipment]['quantity'],
                        'location': items[equipment]['location'],
                        'status': items[equipment]['status']
                    }
                    found = True
                    break
            
            if not found:
                equipment_status[equipment] = {
                    'available': False,
                    'quantity': 0,
                    'location': 'unknown',
                    'status': 'not_found'
                }
        
        return equipment_status
    
    def _generate_immediate_actions(self, emergency_type: str, activation_record: Dict) -> List[str]:
        """Generate immediate actions for emergency response"""
        immediate_actions = [
            f"Announce Code {activation_record['code']} to {activation_record['location']}",
            f"Page response teams: {', '.join(activation_record['team_required'])}",
            "Prepare emergency equipment",
            "Ensure clear access to patient location",
            "Document activation time and details"
        ]
        
        # Add specific actions based on emergency type
        if emergency_type == 'cardiac_arrest':
            immediate_actions.extend([
                "Start CPR if not already in progress",
                "Apply defibrillator pads",
                "Establish IV/IO access"
            ])
        elif emergency_type == 'trauma':
            immediate_actions.extend([
                "Activate trauma bay",
                "Prepare blood products",
                "Notify operating room"
            ])
        elif emergency_type == 'stroke':
            immediate_actions.extend([
                "Activate stroke protocol",
                "Prepare CT scanner",
                "Calculate time window for thrombolysis"
            ])
        
        return immediate_actions
    
    def _calculate_response_time(self, emergency_type: str, location: str) -> Dict:
        """Calculate estimated response time based on emergency type and location"""
        base_times = {
            'cardiac_arrest': 120,  # 2 minutes
            'respiratory_arrest': 120,
            'severe_bleeding': 300,  # 5 minutes
            'anaphylaxis': 300,
            'seizure': 300,
            'stroke': 600,  # 10 minutes
            'trauma': 300
        }
        
        base_time = base_times.get(emergency_type, 300)
        
        # Adjust for location
        location_multipliers = {
            'emergency_department': 1.0,
            'icu': 1.0,
            'general_floors': 1.5,
            'outpatient': 2.0,
            'remote_location': 3.0
        }
        
        multiplier = location_multipliers.get(location.lower(), 1.5)
        estimated_time = int(base_time * multiplier)
        
        return {
            'estimated_seconds': estimated_time,
            'estimated_minutes': round(estimated_time / 60, 1),
            'base_time': base_time,
            'location_multiplier': multiplier,
            'factors': ['team_availability', 'equipment_location', 'hospital_traffic']
        }
    
    def get_emergency_checklist(self, emergency_type: str) -> Dict:
        """Get comprehensive emergency response checklist"""
        if emergency_type not in self.emergency_protocols:
            return {'error': 'Unknown emergency type'}
        
        protocol = self.emergency_protocols[emergency_type]
        
        return {
            'emergency_type': emergency_type,
            'code': protocol['code'],
            'priority': protocol['priority'],
            'team_members': self._get_team_checklist(protocol['team_required']),
            'equipment_checklist': self._get_equipment_checklist(protocol['equipment']),
            'medication_checklist': self._get_medication_checklist(protocol['medications']),
            'procedure_checklist': protocol['procedures'],
            'documentation_checklist': protocol.get('documentation_required', []),
            'safety_considerations': self._get_safety_considerations(emergency_type),
            'communication_protocols': self._get_communication_protocols(emergency_type)
        }
    
    def _get_team_checklist(self, team_required: List[str]) -> List[Dict]:
        """Generate team member checklist"""
        team_checklist = []
        for team in team_required:
            team_info = self.response_teams.get(team, {})
            team_checklist.append({
                'team': team,
                'members': team_info.get('members', []),
                'training_required': team_info.get('training_required', []),
                'status': 'pending'
            })
        return team_checklist
    
    def _get_equipment_checklist(self, equipment: List[str]) -> List[Dict]:
        """Generate equipment checklist"""
        equipment_checklist = []
        for item in equipment:
            equipment_checklist.append({
                'item': item,
                'status': 'pending',
                'checked_by': None,
                'time_checked': None
            })
        return equipment_checklist
    
    def _get_medication_checklist(self, medications: List[str]) -> List[Dict]:
        """Generate medication checklist"""
        medication_checklist = []
        for med in medications:
            medication_checklist.append({
                'medication': med,
                'dose': 'per_protocol',
                'route': 'per_protocol',
                'status': 'pending',
                'administered_by': None,
                'time_administered': None
            })
        return medication_checklist
    
    def _get_safety_considerations(self, emergency_type: str) -> List[str]:
        """Get safety considerations for emergency type"""
        safety_considerations = {
            'cardiac_arrest': [
                'Ensure electrical safety with defibrillator',
                'Protect team members during CPR',
                'Check for do-not-resuscitate orders'
            ],
            'trauma': [
                'Use personal protective equipment',
                'Consider hazardous materials',
                'Ensure scene safety'
            ],
            'stroke': [
                'Check for contraindications to thrombolysis',
                'Monitor for hemorrhagic complications',
                'Protect airway if decreased consciousness'
            ]
        }
        
        return safety_considerations.get(emergency_type, ['Follow standard safety protocols'])
    
    def _get_communication_protocols(self, emergency_type: str) -> Dict:
        """Get communication protocols for emergency response"""
        return {
            'internal_communication': [
                'Use emergency code system',
                'Activate overhead paging',
                'Use designated emergency channels'
            ],
            'external_communication': [
                'Notify family if appropriate',
                'Contact receiving facilities if transfer needed',
                'Document all communications'
            ],
            'documentation': [
                'Record activation time',
                'Document team member arrival times',
                'Log all interventions performed',
                'Note patient outcomes'
            ]
        }

# Global instance
emergency_response_system = EmergencyResponseSystem()
