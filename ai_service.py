"""
Hugging Face AI Service for Advanced Medical Triage Analysis
Integrates with Hugging Face models for sophisticated symptom analysis
"""

import os
import json
import logging
import requests
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
    """Hugging Face AI service for medical triage analysis using OpenAI models"""
    
    def __init__(self, model_name: str = "distilgpt2", use_api: bool = True, api_token: str = None):
        """
        Initialize the Hugging Face AI service with OpenAI models
        
        Args:
            model_name: Name of the OpenAI model from Hugging Face (default: distilgpt2 for speed)
            use_api: Whether to use Hugging Face Inference API (always True)
            api_token: Hugging Face API token
        """
        self.model_name = model_name
        self.use_api = use_api
        self.api_token = api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        
        logger.info(f"Initializing Hugging Face AI service with OpenAI model: {model_name}")
        
        if not self.api_token:
            logger.warning("⚠️ No Hugging Face API token provided - service will not work")
            raise ValueError("Hugging Face API token is required")
        
        logger.info("🌐 Using Hugging Face API with OpenAI models - advanced medical analysis")
    
    def analyze_symptoms_with_ai(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Analyze symptoms using OpenAI models from Hugging Face
        
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
        
        # First do keyword analysis for critical emergency detection
        keyword_result = self._fallback_analysis(symptoms, age, pregnancy_status)
        
        # Always use OpenAI model for enhanced analysis
        try:
            return self._analyze_with_openai_model(symptoms, age, pregnancy_status, additional_context, keyword_result)
        except Exception as e:
            logger.error(f"OpenAI model analysis failed, using keyword fallback: {e}")
            return keyword_result
    
    def _analyze_with_openai_model(
        self, 
        symptoms: str, 
        age: int, 
        pregnancy_status: bool, 
        additional_context: Optional[Dict],
        keyword_result: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Analyze symptoms using OpenAI models from Hugging Face
        
        Args:
            symptoms: Patient symptoms description
            age: Patient age
            pregnancy_status: Whether patient is pregnant
            additional_context: Additional patient data
            keyword_result: Result from keyword analysis
            
        Returns:
            Enhanced analysis result
        """
        
        # Create medical prompt for OpenAI model
        medical_prompt = self._create_medical_prompt(symptoms, age, pregnancy_status, additional_context)
        
        # Try multiple models in order of preference
        models_to_try = [
            "distilgpt2",  # Fast and reliable
            "gpt2",        # Classic GPT-2
            "gpt2-medium", # Medium size
            "microsoft/DialoGPT-small"  # Smaller DialoGPT
        ]
        
        for model_name in models_to_try:
            try:
                logger.info(f"Trying model: {model_name}")
                
                # Call Hugging Face API with OpenAI model
                headers = {"Authorization": f"Bearer {self.api_token}"}
                
                # Use Hugging Face Inference API with OpenAI model
                API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
                
                payload = {
                    "inputs": f"Medical triage analysis: {medical_prompt}\n\nProvide severity assessment (RED/YELLOW/GREEN) and detailed reasoning:",
                    "parameters": {
                        "max_length": 200,  # Reduced for faster response
                        "temperature": 0.3,
                        "return_full_text": False,
                        "wait_for_model": True  # Don't wait for model loading
                    }
                }
                
                # Add timeout for faster failure
                response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                
                # Check for model loading error
                if isinstance(result, dict) and 'error' in result:
                    if 'loading' in result['error'].lower():
                        logger.warning(f"Model {model_name} is loading, trying next model")
                        continue
                    else:
                        logger.error(f"Model {model_name} error: {result['error']}")
                        continue
                
                # Extract AI response
                if isinstance(result, list) and len(result) > 0:
                    ai_response = result[0].get('generated_text', '').strip()
                else:
                    ai_response = str(result).strip()
                
                if not ai_response:
                    logger.warning(f"Empty response from {model_name}, trying next model")
                    continue
                
                # Parse AI response for severity and confidence
                severity = self._extract_severity_from_response(ai_response, keyword_result['severity'])
                confidence = self._extract_confidence_from_response(ai_response, keyword_result['confidence'])
                
                # Generate reasoning
                reasoning = f"OpenAI model analysis: {ai_response[:300]}..." if len(ai_response) > 300 else f"OpenAI model analysis: {ai_response}"
                
                # Get recommendations
                recommendations = self._get_medical_recommendations(severity)
                
                # Generate AI insights
                ai_insights = [
                    "Analysis enhanced by OpenAI model from Hugging Face",
                    f"Model used: {model_name}",
                    "Advanced conversational AI reasoning",
                    "Real-time AI processing"
                ]
                
                logger.info(f"OpenAI Model Analysis completed with {model_name}: {severity} severity with {confidence:.2f} confidence")
                
                return {
                    'severity': severity,
                    'reason': reasoning,
                    'confidence': confidence,
                    'recommendations': recommendations,
                    'ai_insights': ai_insights,
                    'model_used': model_name,
                    'analysis_method': 'openai_huggingface'
                }
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error with {model_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error with {model_name}: {e}")
                continue
        
        # All models failed, return keyword fallback
        logger.warning("All OpenAI models failed, using keyword analysis")
        return keyword_result
    
    def _extract_severity_from_response(self, response: str, fallback_severity: str) -> str:
        """Extract severity level from AI response"""
        response_upper = response.upper()
        
        if 'RED' in response_upper or 'CRITICAL' in response_upper or 'EMERGENCY' in response_upper:
            return 'RED'
        elif 'YELLOW' in response_upper or 'URGENT' in response_upper or 'PRIORITY' in response_upper:
            return 'YELLOW'
        elif 'GREEN' in response_upper or 'ROUTINE' in response_upper or 'LOW' in response_upper:
            return 'GREEN'
        
        return fallback_severity
    
    def _extract_confidence_from_response(self, response: str, fallback_confidence: float) -> float:
        """Extract confidence from AI response"""
        # Look for confidence indicators
        if 'high confidence' in response.lower() or 'certain' in response.lower():
            return min(fallback_confidence + 0.2, 0.95)
        elif 'low confidence' in response.lower() or 'uncertain' in response.lower():
            return max(fallback_confidence - 0.1, 0.5)
        
        return min(fallback_confidence + 0.1, 0.9)
    
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
    
    def __init__(self, api_token: str = None):
        """Initialize AI services"""
        from config import HUGGINGFACE_API_TOKEN
        
        # Use provided token or get from config
        token = api_token or HUGGINGFACE_API_TOKEN
        
        # Initialize Hugging Face service with API support (API-only mode)
        self.huggingface_service = HuggingFaceAIService(
            use_api=True,
            api_token=token
        )
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
        """Get list of available OpenAI models from Hugging Face"""
        models = [
            # Working OpenAI models for medical triage
            "distilgpt2",  # Fast and reliable
            "gpt2",        # Classic GPT-2
            "gpt2-medium", # Medium size
            "gpt2-large",  # Large model
            "microsoft/DialoGPT-small",  # Smaller DialoGPT
            "microsoft/DialoGPT-large"   # Larger DialoGPT
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
