"""
Hugging Face AI Service for Advanced Medical Triage Analysis
Integrates with Hugging Face models for sophisticated symptom analysis
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Hugging Face imports
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from transformers import pipeline
    import torch
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("⚠️ Warning: transformers not installed. Using fallback analysis.")
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
    SentenceTransformer = None
    pipeline = None
    torch = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceAIService:
    """Hugging Face AI service for medical triage analysis"""
    
    def __init__(self, model_name: str = "medical-bert-base-uncased"):
        """
        Initialize the Hugging Face AI service
        
        Args:
            model_name: Name of the Hugging Face model to use
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Initializing Hugging Face AI service with model: {model_name}")
        
        # Load model and tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            logger.info(f"✅ Successfully loaded Hugging Face model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load Hugging Face model {model_name}: {e}")
            raise e
    
    def analyze_symptoms_with_ai(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Analyze symptoms using Hugging Face AI model
        
        Args:
            symptoms: Patient symptoms description
            age: Patient age
            pregnancy_status: Whether patient is pregnant
            additional_context: Additional patient data (vitals, medical history, etc.)
            
        Returns:
            Dictionary containing:
            - severity: RED, YELLOW, GREEN
            - reason: Detailed medical reasoning
            - confidence: AI confidence score (0-1)
            - recommendations: Medical recommendations
            - ai_insights: AI-generated insights
        """
        
        if not self.model or not self.tokenizer:
            logger.warning("Hugging Face model not available, using fallback analysis")
            return self._fallback_analysis(symptoms, age, pregnancy_status)
        
        try:
            # Prepare input for the model
            # Create a comprehensive medical prompt
            medical_prompt = self._create_medical_prompt(symptoms, age, pregnancy_status, additional_context)
            
            # Tokenize input
            inputs = self.tokenizer(
                medical_prompt,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding='max_length'
            )
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process the output
            predictions = torch.softmax(outputs.logits, dim=-1)
            predicted_class_idx = torch.argmax(predictions, dim=-1).item()
            
            # Map prediction to severity
            severity_map = {0: 'GREEN', 1: 'YELLOW', 2: 'RED'}
            severity_labels = ['GREEN', 'YELLOW', 'RED']
            predicted_severity = severity_labels[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])
            
            # Generate detailed reasoning
            reasoning = self._generate_reasoning(
                symptoms, age, pregnancy_status, predicted_severity, confidence
            )
            
            # Get recommendations
            recommendations = self._get_medical_recommendations(predicted_severity)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(
                symptoms, age, pregnancy_status, predicted_severity, confidence
            )
            
            logger.info(f"AI Analysis completed: {predicted_severity} severity with {confidence:.2f} confidence")
            
            return {
                'severity': predicted_severity,
                'reason': reasoning,
                'confidence': confidence,
                'recommendations': recommendations,
                'ai_insights': ai_insights,
                'model_used': self.model_name,
                'analysis_method': 'huggingface'
            }
            
        except Exception as e:
            logger.error(f"Error in Hugging Face AI analysis: {e}")
            return self._fallback_analysis(symptoms, age, pregnancy_status)
    
    def _create_medical_prompt(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict] = None
    ) -> str:
        """
        Create a comprehensive medical prompt for the AI model
        """
        
        prompt_parts = []
        
        # Add system instructions
        prompt_parts.append(
            "You are an advanced medical AI triage system. "
            "Analyze patient symptoms and provide accurate triage assessment. "
            "Consider patient demographics and medical context. "
            "Respond with structured JSON output."
        )
        
        # Add patient context
        prompt_parts.append(f"Patient Information:")
        prompt_parts.append(f"- Age: {age} years")
        prompt_parts.append(f"- Pregnancy Status: {'Yes' if pregnancy_status else 'No'}")
        
        if additional_context:
            prompt_parts.append("Additional Medical Context:")
            for key, value in additional_context.items():
                prompt_parts.append(f"- {key}: {value}")
        
        # Add symptoms
        prompt_parts.append(f"Symptoms: {symptoms}")
        
        # Add task instructions
        prompt_parts.append(
            "Task: Analyze the symptoms and determine triage severity (RED/YELLOW/GREEN). "
            "Provide specific medical reasoning and confidence score."
        )
        
        # Add output format requirements
        prompt_parts.append(
            "Output Format: JSON with keys: "
            "severity (RED/YELLOW/GREEN), "
            "reason (detailed medical reasoning), "
            "confidence (0-1), "
            "recommendations (list of medical recommendations), "
            "ai_insights (AI-generated insights)."
        )
        
        return "\n".join(prompt_parts)
    
    def _generate_reasoning(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        predicted_severity: str, 
        confidence: float
    ) -> str:
        """Generate detailed medical reasoning based on AI analysis"""
        
        severity_reasons = {
            'RED': [
                "Critical symptoms detected requiring immediate emergency care",
                "Life-threatening condition identified - rapid intervention needed",
                "Emergency medical situation - call emergency services"
            ],
            'YELLOW': [
                "Urgent medical symptoms requiring timely evaluation",
                "Moderate severity condition - medical attention needed",
                "Potential for deterioration if not treated"
            ],
            'GREEN': [
                "Non-urgent symptoms - routine care acceptable",
                "Mild condition - self-care may be appropriate",
                "Monitor symptoms for changes"
            ]
        }
        
        # Age-specific considerations
        age_factors = []
        if age > 65:
            age_factors.append("Elderly patient with higher risk factors")
        elif age < 12:
            age_factors.append("Pediatric patient requiring special consideration")
        elif pregnancy_status:
            age_factors.append("Pregnant patient requiring medical evaluation")
        
        # Symptom-specific analysis
        symptom_keywords = {
            'cardiac': ['chest pain', 'heart attack', 'palpitations', 'rapid heartbeat'],
            'respiratory': ['difficulty breathing', 'shortness of breath', 'wheezing'],
            'neurological': ['unconscious', 'fainting', 'confusion', 'seizure', 'stroke'],
            'gastrointestinal': ['severe abdominal pain', 'vomiting', 'diarrhea'],
            'trauma': ['severe bleeding', 'major injury', 'broken bone', 'head injury']
        }
        
        # Check for specific symptom patterns
        detected_patterns = []
        for category, keywords in symptom_keywords.items():
            if any(keyword in symptoms.lower() for keyword in keywords):
                detected_patterns.append(category)
        
        # Build reasoning
        if detected_patterns:
            pattern_reasoning = {
                'cardiac': "Cardiac symptoms detected - potential heart condition",
                'respiratory': "Respiratory distress symptoms - airway compromise possible",
                'neurological': "Neurological symptoms - potential brain injury",
                'gastrointestinal': "GI symptoms - potential abdominal condition",
                'trauma': "Traumatic injury symptoms - immediate care needed"
            }
            
            primary_pattern = detected_patterns[0] if detected_patterns else None
            
            if primary_pattern:
                reasoning = pattern_reasoning.get(primary_pattern, "General medical condition requiring evaluation")
            elif len(detected_patterns) > 1:
                reasoning = "Multiple symptom categories detected - comprehensive evaluation needed"
            else:
                reasoning = "General symptoms requiring medical assessment"
        
        else:
            reasoning = "General symptoms - routine care may be appropriate"
        
        # Add age and pregnancy factors to reasoning
        if age_factors:
            reasoning += f" ({', '.join(age_factors)})"
        
        return reasoning
    
    def _get_medical_recommendations(self, severity: str) -> List[str]:
        """Get medical recommendations based on triage severity"""
        
        recommendations = {
            'RED': [
                "🚑 Call emergency services immediately (999/911)",
                "🏥 Go to nearest emergency department",
                "⏰ Do not wait - time is critical",
                "📞 Have someone drive you if possible",
                "💊 Inform medical staff about symptoms"
            ],
            'YELLOW': [
                "🏥 Visit urgent care or emergency department within 2-4 hours",
                "📞 Call your doctor for immediate appointment",
                "🚗 Have someone available to drive you",
                "💊 Bring current medications list",
                "📋 Monitor symptoms for changes"
            ],
            'GREEN': [
                "📅 Schedule regular doctor appointment",
                "🏠 Monitor symptoms at home",
                "💧 Stay hydrated and rest",
                "📞 Call doctor if symptoms worsen"
            ]
        }
        
        return recommendations.get(severity, [])
    
    def _generate_ai_insights(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        predicted_severity: str, 
        confidence: float
    ) -> List[str]:
        """Generate AI insights based on analysis"""
        
        insights = []
        
        # Risk assessment based on confidence
        if confidence < 0.5:
            insights.append("Low confidence in analysis - recommend clinical confirmation")
        elif confidence < 0.8:
            insights.append("Moderate confidence - clinical correlation recommended")
        else:
            insights.append("High confidence - analysis appears reliable")
        
        # Age-specific insights
        if age > 65:
            insights.append("Elderly patient - consider comorbidities and polypharmacy")
        elif pregnancy_status:
            insights.append("Pregnant patient - obstetric evaluation recommended")
        
        # Symptom complexity insights
        symptom_count = len(symptoms.split())
        if symptom_count > 10:
            insights.append("Complex symptom presentation - detailed examination needed")
        elif symptom_count > 5:
            insights.append("Multiple symptoms - comprehensive assessment needed")
        
        return insights
    
    def _fallback_analysis(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool
    ) -> Dict[str, any]:
        """
        Fallback analysis when Hugging Face model is not available
        Uses keyword-based analysis as fallback
        """
        
        symptoms_lower = symptoms.lower()
        confidence = 0.7  # Default confidence for fallback
        
        # RED FLAG - Critical Emergency Conditions
        red_keywords = [
            'chest pain', 'heart attack', 'palpitations', 'rapid heartbeat',
            'difficulty breathing', 'shortness of breath', 'can\'t breathe', 'wheezing', 'choking',
            'unconscious', 'fainting', 'loss of consciousness', 'confusion', 'seizure', 'stroke',
            'severe bleeding', 'major injury', 'broken bone', 'head injury', 'spinal injury',
            'severe abdominal pain', 'rupture', 'perforation', 'obstruction'
        ]
        
        # YELLOW FLAG - Urgent but Non-Life-Threatening
        yellow_keywords = [
            'moderate pain', 'mild pain', 'headache', 'migraine', 'back pain', 'joint pain',
            'fever', 'chills', 'sweats', 'infection', 'abscess',
            'nausea', 'vomiting', 'diarrhea', 'stomach pain', 'constipation',
            'cough', 'sore throat', 'runny nose', 'congestion',
            'dizziness', 'lightheaded', 'fatigue', 'weakness', 'rash'
        ]
        
        # Check for RED conditions first (highest priority)
        for keyword in red_keywords:
            if keyword in symptoms_lower:
                return {
                    'severity': 'RED',
                    'reason': 'Critical symptoms detected - immediate emergency care required',
                    'confidence': 0.95,
                    'recommendations': self._get_medical_recommendations('RED'),
                    'ai_insights': ['Emergency condition detected - immediate action required'],
                    'analysis_method': 'keyword_fallback'
                }
        
        # Check for YELLOW conditions
        for keyword in yellow_keywords:
            if keyword in symptoms_lower:
                return {
                    'severity': 'YELLOW',
                    'reason': 'Urgent symptoms detected - timely medical evaluation needed',
                    'confidence': 0.85,
                    'recommendations': self._get_medical_recommendations('YELLOW'),
                    'ai_insights': ['Urgent condition - medical attention needed'],
                    'analysis_method': 'keyword_fallback'
                }
        
        # Pregnancy-specific considerations
        if pregnancy_status:
            return {
                'severity': 'YELLOW',
                'reason': 'Pregnant patient with symptoms - medical evaluation recommended',
                'confidence': 0.80,
                'recommendations': self._get_medical_recommendations('YELLOW'),
                'ai_insights': ['Pregnancy requires medical attention'],
                'analysis_method': 'keyword_fallback'
            }
        
        # Age-specific considerations
        if age > 65:
            elderly_keywords = ['confusion', 'weakness', 'fall', 'dizziness', 'pain']
            if any(keyword in symptoms_lower for keyword in elderly_keywords):
                return {
                    'severity': 'YELLOW',
                    'reason': 'Elderly patient with concerning symptoms - medical evaluation needed',
                    'confidence': 0.80,
                    'recommendations': self._get_medical_recommendations('YELLOW'),
                    'ai_insights': ['Elderly patient - consider comprehensive evaluation'],
                    'analysis_method': 'keyword_fallback'
                }
        
        elif age < 12:
            pediatric_keywords = ['fever', 'difficulty breathing', 'lethargic', 'not eating', 'crying']
            if any(keyword in symptoms_lower for keyword in pediatric_keywords):
                return {
                    'severity': 'YELLOW',
                    'reason': 'Pediatric patient with concerning symptoms - medical evaluation needed',
                    'confidence': 0.80,
                    'recommendations': self._get_medical_recommendations('YELLOW'),
                    'ai_insights': ['Pediatric patient - urgent evaluation needed'],
                    'analysis_method': 'keyword_fallback'
                }
        
        # GREEN - Non-urgent conditions
        if symptoms_lower.strip():
            return {
                'severity': 'GREEN',
                'reason': 'Mild symptoms detected - routine care acceptable',
                'confidence': 0.70,
                'recommendations': self._get_medical_recommendations('GREEN'),
                'ai_insights': ['Non-urgent condition - self-care may be appropriate'],
                'analysis_method': 'keyword_fallback'
                }
        
        # No symptoms provided
        return {
            'severity': 'GREEN',
            'reason': 'No specific symptoms reported - routine care if needed',
            'confidence': 0.60,
            'recommendations': self._get_medical_recommendations('GREEN'),
            'ai_insights': ['No symptoms to analyze - routine assessment'],
            'analysis_method': 'keyword_fallback'
                }

class AIServiceManager:
    """Manager for AI services"""
    
    def __init__(self):
        """Initialize AI services"""
        self.huggingface_service = HuggingFaceAIService()
        self.fallback_service = FallbackAnalysisService()
        
    def get_ai_analysis(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Get AI analysis from available services
        """
        try:
            # Try Hugging Face first
            result = self.huggingface_service.analyze_symptoms_with_ai(
                symptoms, age, pregnancy_status, additional_context
            )
            logger.info("✅ Using Hugging Face AI for analysis")
            return result
        except Exception as e:
            logger.error(f"❌ Hugging Face AI failed: {e}")
            # Fallback to keyword analysis
            logger.info("⚠️ Using fallback analysis due to Hugging Face unavailability")
            return self.fallback_service.analyze_symptoms_with_ai(
                symptoms, age, pregnancy_status, additional_context
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Hugging Face models"""
        models = [
            "medical-bert-base-uncased",
            "medical-bert-large-uncased",
            "medical-distilbert-base-uncased",
            "medical-distilbert-large-uncased",
            "medical-emotion-base-uncased",
            "medical-biobert-base-uncased",
            "medical-biobert-large-uncased"
        ]
        return models

class FallbackAnalysisService:
    """Fallback analysis service when Hugging Face is not available"""
    
    def analyze_symptoms_with_ai(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Keyword-based fallback analysis
        """
        return self._analyze_with_keywords(symptoms, age, pregnancy_status)

    def _analyze_with_keywords(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool
    ) -> Dict[str, any]:
        """
        Analyze symptoms using keyword matching
        """
        return self.huggingface_service._fallback_analysis(symptoms, age, pregnancy_status)
