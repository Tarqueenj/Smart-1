from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
import json

class MedicalDecisionSupport:
    """Advanced medical decision support system with clinical protocols"""
    
    def __init__(self):
        self.clinical_protocols = self._load_clinical_protocols()
        self.differential_diagnoses = self._load_differential_diagnoses()
        self.emergency_protocols = self._load_emergency_protocols()
        self.medications_database = self._load_medications_database()
        self.lab_tests_database = self._load_lab_tests_database()
    
    def _load_clinical_protocols(self) -> Dict:
        """Load clinical protocols for common conditions"""
        return {
            'chest_pain': {
                'red_flags': [
                    'crushing chest pain', 'radiating pain to arm/jaw', 'shortness of breath',
                    'sweating', 'nausea', 'dizziness', 'syncope'
                ],
                'immediate_actions': [
                    'Call emergency services immediately',
                    'Administer aspirin 325mg if available',
                    'Monitor vital signs',
                    'Prepare for cardiac monitoring',
                    'Establish IV access'
                ],
                'diagnostic_tests': ['ECG', 'Cardiac enzymes', 'Chest X-ray', 'Blood gases'],
                'differential_diagnoses': ['Acute MI', 'Angina', 'Pulmonary embolism', 'Aortic dissection'],
                'special_considerations': ['Age > 65', 'Diabetes', 'Previous cardiac history']
            },
            'difficulty_breathing': {
                'red_flags': [
                    'stridor', 'inability to speak full sentences', 'cyanosis',
                    'altered mental status', 'use of accessory muscles'
                ],
                'immediate_actions': [
                    'Assess airway patency',
                    'Administer oxygen',
                    'Monitor oxygen saturation',
                    'Prepare for intubation if needed',
                    'Position patient upright'
                ],
                'diagnostic_tests': ['Chest X-ray', 'ABG', 'CBC', 'Pulse oximetry'],
                'differential_diagnoses': ['Asthma', 'COPD exacerbation', 'Pneumonia', 'Pulmonary embolism', 'Heart failure'],
                'special_considerations': ['History of asthma/COPD', 'Allergies', 'Medication use']
            },
            'abdominal_pain': {
                'red_flags': [
                    'rigid abdomen', 'rebound tenderness', 'guarding',
                    'fever with chills', 'vomiting blood', 'black stools'
                ],
                'immediate_actions': [
                    'NPO (nothing by mouth)',
                    'IV fluids if dehydrated',
                    'Pain management (avoid narcotics until diagnosis)',
                    'Monitor vital signs',
                    'Surgical consultation if needed'
                ],
                'diagnostic_tests': ['CBC', 'Comprehensive metabolic panel', 'Lipase', 'Amylase', 'CT abdomen'],
                'differential_diagnoses': ['Appendicitis', 'Pancreatitis', 'Cholecystitis', 'Bowel obstruction', 'Perforation'],
                'special_considerations': ['Pregnancy', 'Elderly patients', 'Immunocompromised']
            },
            'headache': {
                'red_flags': [
                    'worst headache of life', 'sudden onset', 'neck stiffness',
                    'fever', 'focal neurological deficits', 'altered consciousness'
                ],
                'immediate_actions': [
                    'Neurological assessment',
                    'Monitor vital signs',
                    'Consider CT scan if red flags present',
                    'Pain management after assessment',
                    'Neurology consultation if needed'
                ],
                'diagnostic_tests': ['CT head', 'MRI brain', 'Lumbar puncture', 'CBC'],
                'differential_diagnoses': ['Subarachnoid hemorrhage', 'Meningitis', 'Migraine', 'Tension headache', 'Cluster headache'],
                'special_considerations': ['Anticoagulant use', 'Cancer history', 'Immunocompromised']
            },
            'fever': {
                'red_flags': [
                    'temperature > 40°C', 'altered mental status', 'hypotension',
                    'rash with fever', 'difficulty breathing', 'seizures'
                ],
                'immediate_actions': [
                    'Temperature control',
                    'IV fluids if needed',
                    'Blood cultures before antibiotics',
                    'Broad-spectrum antibiotics if indicated',
                    'Monitor for sepsis'
                ],
                'diagnostic_tests': ['Blood cultures', 'CBC', 'CRP', 'Urinalysis', 'Chest X-ray'],
                'differential_diagnoses': ['Sepsis', 'Meningitis', 'Pneumonia', 'UTI', 'Viral infection'],
                'special_considerations': ['Immunocompromised', 'Elderly', 'Pregnancy', 'Recent travel']
            }
        }
    
    def _load_differential_diagnoses(self) -> Dict:
        """Load differential diagnosis database"""
        return {
            'cardiovascular': {
                'symptoms': ['chest pain', 'shortness of breath', 'palpitations', 'edema'],
                'conditions': {
                    'acute_myocardial_infarction': {
                        'key_symptoms': ['crushing chest pain', 'radiating pain', 'sweating'],
                        'risk_factors': ['age > 45', 'smoking', 'diabetes', 'hypertension'],
                        'urgency': 'critical'
                    },
                    'angina': {
                        'key_symptoms': ['chest tightness', 'exertional pain', 'relieved by rest'],
                        'risk_factors': ['coronary artery disease', 'age > 50'],
                        'urgency': 'urgent'
                    },
                    'heart_failure': {
                        'key_symptoms': ['shortness of breath', 'edema', 'fatigue'],
                        'risk_factors': ['previous MI', 'hypertension', 'diabetes'],
                        'urgency': 'urgent'
                    }
                }
            },
            'respiratory': {
                'symptoms': ['cough', 'shortness of breath', 'wheezing', 'chest pain'],
                'conditions': {
                    'pneumonia': {
                        'key_symptoms': ['fever', 'productive cough', 'chest pain'],
                        'risk_factors': ['age > 65', 'immunocompromised', 'smoking'],
                        'urgency': 'urgent'
                    },
                    'copd_exacerbation': {
                        'key_symptoms': ['wheezing', 'increased dyspnea', 'cough'],
                        'risk_factors': ['COPD history', 'smoking'],
                        'urgency': 'urgent'
                    },
                    'pulmonary_embolism': {
                        'key_symptoms': ['sudden dyspnea', 'pleuritic chest pain', 'tachycardia'],
                        'risk_factors': ['DVT', 'immobility', 'recent surgery'],
                        'urgency': 'critical'
                    }
                }
            },
            'neurological': {
                'symptoms': ['headache', 'confusion', 'weakness', 'seizures'],
                'conditions': {
                    'stroke': {
                        'key_symptoms': ['focal weakness', 'speech difficulty', 'facial droop'],
                        'risk_factors': ['hypertension', 'atrial fibrillation', 'diabetes'],
                        'urgency': 'critical'
                    },
                    'meningitis': {
                        'key_symptoms': ['headache', 'fever', 'neck stiffness', 'photophobia'],
                        'risk_factors': ['immunocompromised', 'recent infection'],
                        'urgency': 'critical'
                    }
                }
            }
        }
    
    def _load_emergency_protocols(self) -> Dict:
        """Load emergency response protocols"""
        return {
            'cardiac_arrest': {
                'steps': [
                    'Check responsiveness and breathing',
                    'Call emergency services',
                    'Start CPR (30:2 ratio)',
                    'Use AED if available',
                    'Administer epinephrine every 3-5 minutes',
                    'Consider advanced airway',
                    'Monitor rhythm and treat accordingly'
                ],
                'medications': ['epinephrine', 'amiodarone', 'lidocaine'],
                'equipment': ['defibrillator', 'bag valve mask', 'intubation kit']
            },
            'anaphylaxis': {
                'steps': [
                    'Stop allergen exposure',
                    'Administer epinephrine IM',
                    'Call emergency services',
                    'Administer oxygen',
                    'Prepare airway for intubation',
                    'Give antihistamines and steroids',
                    'Monitor vital signs'
                ],
                'medications': ['epinephrine', 'diphenhydramine', 'corticosteroids'],
                'equipment': ['oxygen', 'bag valve mask', 'IV supplies']
            },
            'seizure': {
                'steps': [
                    'Ensure patient safety',
                    'Protect airway',
                    'Do not restrain patient',
                    'Time the seizure',
                    'Administer oxygen if needed',
                    'Consider benzodiazepines if prolonged',
                    'Monitor vital signs'
                ],
                'medications': ['lorazepam', 'diazepam', 'phenytoin'],
                'equipment': ['oxygen', 'suction', 'monitoring equipment']
            }
        }
    
    def _load_medications_database(self) -> Dict:
        """Load medications database with dosing information"""
        return {
            'emergency_medications': {
                'epinephrine': {
                    'indications': ['cardiac arrest', 'anaphylaxis', 'severe hypotension'],
                    'dosing': {
                        'cardiac_arrest': '1mg IV/IO every 3-5 minutes',
                        'anaphylaxis': '0.3-0.5mg IM (1:1000)',
                        'hypotension': '2-10mcg/min IV infusion'
                    },
                    'contraindications': ['tachyarrhythmias', 'angle-closure glaucoma'],
                    'side_effects': ['tachycardia', 'hypertension', 'anxiety']
                },
                'aspirin': {
                    'indications': ['chest pain', 'MI prevention'],
                    'dosing': {
                        'chest_pain': '325mg chewable immediately',
                        'prevention': '81-325mg daily'
                    },
                    'contraindications': ['active bleeding', 'allergy', 'peptic ulcer'],
                    'side_effects': ['GI bleeding', 'tinnitus', 'allergic reaction']
                },
                'nitroglycerin': {
                    'indications': ['chest pain', 'acute pulmonary edema'],
                    'dosing': {
                        'chest_pain': '0.4mg sublingual every 5 minutes (max 3 doses)',
                        'pulmonary_edema': 'IV infusion 5-200mcg/min'
                    },
                    'contraindications': ['hypotension', 'PDE5 inhibitors', 'right MI'],
                    'side_effects': ['headache', 'hypotension', 'reflex tachycardia']
                }
            }
        }
    
    def _load_lab_tests_database(self) -> Dict:
        """Load laboratory tests database"""
        return {
            'emergency_labs': {
                'cbc': {
                    'purpose': 'Complete blood count',
                    'indicates': ['anemia', 'infection', 'bleeding disorders'],
                    'turnaround_time': '30-60 minutes',
                    'critical_values': {
                        'hemoglobin': '<7 g/dL',
                        'platelets': '<20,000/mm³',
                        'wbc': '<2,000 or >50,000/mm³'
                    }
                },
                'cmp': {
                    'purpose': 'Comprehensive metabolic panel',
                    'indicates': ['electrolyte abnormalities', 'renal function', 'liver function'],
                    'turnaround_time': '45-90 minutes',
                    'critical_values': {
                        'potassium': '<2.5 or >6.5 mEq/L',
                        'creatinine': '>3.0 mg/dL',
                        'glucose': '<40 or >600 mg/dL'
                    }
                },
                'cardiac_enzymes': {
                    'purpose': 'Cardiac injury markers',
                    'indicates': ['myocardial infarction', 'cardiac injury'],
                    'turnaround_time': '60-90 minutes',
                    'critical_values': {
                        'troponin': '>0.1 ng/mL',
                        'ck_mb': '>25 ng/mL'
                    }
                }
            }
        }
    
    def get_clinical_guidance(self, symptoms: str, patient_age: int, 
                           vital_signs: Dict = None) -> Dict:
        """
        Get comprehensive clinical guidance based on symptoms and patient data
        
        Args:
            symptoms: Patient-reported symptoms
            patient_age: Patient age in years
            vital_signs: Dictionary with vital sign values
            
        Returns:
            Dictionary with clinical recommendations and protocols
        """
        symptoms_lower = symptoms.lower()
        
        # Identify relevant protocols
        relevant_protocols = self._identify_relevant_protocols(symptoms_lower)
        
        # Check for red flags
        red_flags = self._check_red_flags(symptoms_lower, relevant_protocols)
        
        # Generate differential diagnoses
        differential_dx = self._generate_differential_diagnoses(symptoms_lower, patient_age)
        
        # Recommend diagnostic tests
        recommended_tests = self._recommend_diagnostic_tests(relevant_protocols, differential_dx)
        
        # Suggest medications
        medication_suggestions = self._suggest_medications(relevant_protocols, differential_dx)
        
        # Provide immediate actions
        immediate_actions = self._get_immediate_actions(relevant_protocols, red_flags)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(red_flags, vital_signs, patient_age)
        
        return {
            'relevant_protocols': relevant_protocols,
            'red_flags': red_flags,
            'differential_diagnoses': differential_dx,
            'recommended_tests': recommended_tests,
            'medication_suggestions': medication_suggestions,
            'immediate_actions': immediate_actions,
            'risk_score': risk_score,
            'clinical_priority': self._determine_priority(risk_score, red_flags),
            'special_considerations': self._get_special_considerations(patient_age, symptoms_lower),
            'consultation_needed': self._determine_consultation_needs(differential_dx, risk_score),
            'guidance_timestamp': datetime.now().isoformat()
        }
    
    def _identify_relevant_protocols(self, symptoms: str) -> List[str]:
        """Identify relevant clinical protocols based on symptoms"""
        relevant = []
        
        for protocol_name, protocol_data in self.clinical_protocols.items():
            for red_flag in protocol_data['red_flags']:
                if red_flag in symptoms:
                    relevant.append(protocol_name)
                    break
        
        return list(set(relevant))
    
    def _check_red_flags(self, symptoms: str, relevant_protocols: List[str]) -> List[str]:
        """Check for red flag symptoms"""
        red_flags_found = []
        
        for protocol in relevant_protocols:
            if protocol in self.clinical_protocols:
                protocol_data = self.clinical_protocols[protocol]
                for red_flag in protocol_data['red_flags']:
                    if red_flag in symptoms:
                        red_flags_found.append(red_flag)
        
        return list(set(red_flags_found))
    
    def _generate_differential_diagnoses(self, symptoms: str, age: int) -> List[Dict]:
        """Generate differential diagnoses based on symptoms and age"""
        differentials = []
        
        for system, system_data in self.differential_diagnoses.items():
            for condition_name, condition_data in system_data['conditions'].items():
                # Check if symptoms match
                symptom_match = any(symptom in symptoms for symptom in condition_data['key_symptoms'])
                
                if symptom_match:
                    differentials.append({
                        'condition': condition_name,
                        'system': system,
                        'urgency': condition_data['urgency'],
                        'key_symptoms': condition_data['key_symptoms'],
                        'risk_factors': condition_data['risk_factors'],
                        'confidence': self._calculate_diagnosis_confidence(symptoms, condition_data['key_symptoms'])
                    })
        
        # Sort by confidence and urgency
        differentials.sort(key=lambda x: (x['confidence'], x['urgency']), reverse=True)
        
        return differentials[:5]  # Return top 5
    
    def _recommend_diagnostic_tests(self, protocols: List[str], differentials: List[Dict]) -> List[Dict]:
        """Recommend diagnostic tests based on protocols and differentials"""
        tests = []
        
        # Tests from protocols
        for protocol in protocols:
            if protocol in self.clinical_protocols:
                for test in self.clinical_protocols[protocol]['diagnostic_tests']:
                    if test in self.lab_tests_database['emergency_labs']:
                        test_info = self.lab_tests_database['emergency_labs'][test]
                        tests.append({
                            'test_name': test,
                            'purpose': test_info['purpose'],
                            'indicates': test_info['indicates'],
                            'turnaround_time': test_info['turnaround_time'],
                            'priority': 'high',
                            'source': 'protocol'
                        })
        
        # Tests from differentials
        for differential in differentials:
            if differential['urgency'] == 'critical':
                # Add critical tests for critical conditions
                tests.append({
                    'test_name': 'CBC',
                    'purpose': 'Complete blood count',
                    'indicates': ['infection', 'anemia'],
                    'turnaround_time': '30-60 minutes',
                    'priority': 'critical',
                    'source': 'differential'
                })
        
        return list({test['test_name']: test for test in tests}.values())  # Remove duplicates
    
    def _suggest_medications(self, protocols: List[str], differentials: List[Dict]) -> List[Dict]:
        """Suggest medications based on protocols and differentials"""
        medications = []
        
        # Emergency medications for critical cases
        critical_differentials = [d for d in differentials if d['urgency'] == 'critical']
        if critical_differentials:
            for med_name, med_data in self.medications_database['emergency_medications'].items():
                medications.append({
                    'medication': med_name,
                    'indications': med_data['indications'],
                    'dosing': med_data['dosing'],
                    'contraindications': med_data['contraindications'],
                    'side_effects': med_data['side_effects'],
                    'priority': 'emergency'
                })
        
        return medications
    
    def _get_immediate_actions(self, protocols: List[str], red_flags: List[str]) -> List[str]:
        """Get immediate actions based on protocols and red flags"""
        actions = []
        
        # Actions from protocols
        for protocol in protocols:
            if protocol in self.clinical_protocols:
                actions.extend(self.clinical_protocols[protocol]['immediate_actions'])
        
        # General emergency actions if red flags present
        if red_flags:
            actions.extend([
                'Continuous vital sign monitoring',
                'Establish IV access',
                'Prepare emergency medications',
                'Notify emergency team'
            ])
        
        return list(set(actions))
    
    def _calculate_risk_score(self, red_flags: List[str], vital_signs: Dict = None, age: int = 0) -> float:
        """Calculate overall patient risk score"""
        score = 0.0
        
        # Red flags contribute to risk
        score += len(red_flags) * 15
        
        # Age risk
        if age > 75:
            score += 20
        elif age > 65:
            score += 15
        elif age < 2:
            score += 25
        
        # Vital signs risk (if provided)
        if vital_signs:
            if vital_signs.get('heart_rate', 0) > 120 or vital_signs.get('heart_rate', 0) < 50:
                score += 15
            if vital_signs.get('blood_pressure_systolic', 0) > 180 or vital_signs.get('blood_pressure_systolic', 0) < 90:
                score += 20
            if vital_signs.get('oxygen_saturation', 100) < 90:
                score += 25
            if vital_signs.get('temperature', 37) > 39 or vital_signs.get('temperature', 37) < 35:
                score += 15
        
        return min(score, 100)  # Cap at 100
    
    def _determine_priority(self, risk_score: float, red_flags: List[str]) -> str:
        """Determine clinical priority based on risk score and red flags"""
        if risk_score >= 70 or len(red_flags) >= 3:
            return 'critical'
        elif risk_score >= 40 or len(red_flags) >= 1:
            return 'urgent'
        else:
            return 'routine'
    
    def _get_special_considerations(self, age: int, symptoms: str) -> List[str]:
        """Get special considerations based on age and symptoms"""
        considerations = []
        
        if age < 12:
            considerations.append('Pediatric dosing and equipment required')
            considerations.append('Consider pediatric specialist consultation')
        elif age > 65:
            considerations.append('Consider multiple comorbidities')
            considerations.append('Medication interactions likely')
            considerations.append('Fall risk assessment needed')
        
        if 'pregnancy' in symptoms:
            considerations.append('Radiation safety for fetus')
            considerations.append('Medication safety in pregnancy')
        
        if 'allergy' in symptoms:
            considerations.append('Allergy history critical for medication selection')
        
        return considerations
    
    def _determine_consultation_needs(self, differentials: List[Dict], risk_score: float) -> List[str]:
        """Determine which specialist consultations are needed"""
        consultations = []
        
        critical_conditions = [d for d in differentials if d['urgency'] == 'critical']
        
        for condition in critical_conditions:
            system = condition['system']
            if system == 'cardiovascular':
                consultations.append('Cardiology')
            elif system == 'neurological':
                consultations.append('Neurology')
            elif system == 'respiratory':
                consultations.append('Pulmonology')
        
        if risk_score >= 70:
            consultations.append('Emergency Medicine')
        
        return list(set(consultations))
    
    def _calculate_diagnosis_confidence(self, symptoms: str, key_symptoms: List[str]) -> float:
        """Calculate confidence score for a diagnosis"""
        matching_symptoms = sum(1 for symptom in key_symptoms if symptom in symptoms)
        total_symptoms = len(key_symptoms)
        
        if total_symptoms == 0:
            return 0.0
        
        confidence = (matching_symptoms / total_symptoms) * 100
        return min(confidence, 95)  # Cap at 95%

# Global instance
medical_decision_support = MedicalDecisionSupport()
