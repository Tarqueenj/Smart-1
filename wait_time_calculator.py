from datetime import datetime, timedelta
import math
import random
from typing import Dict, List, Tuple

class WaitTimeCalculator:
    """Advanced wait time calculation system for realistic healthcare scenarios"""
    
    def __init__(self):
        self.base_wait_times = {
            'RED': 5,      # Critical: 5 minutes
            'YELLOW': 30,   # Urgent: 30 minutes
            'GREEN': 120    # Non-urgent: 2 hours
        }
        
        # Time-based multipliers (peak hours increase wait times)
        self.time_multipliers = {
            'morning_peak': 1.8,    # 8:00-12:00
            'afternoon_peak': 1.5,  # 14:00-18:00
            'evening': 1.2,         # 18:00-22:00
            'night': 0.6,           # 22:00-06:00
            'early_morning': 0.8    # 06:00-08:00
        }
        
        # Day-based multipliers
        self.day_multipliers = {
            'monday': 1.4,
            'tuesday': 1.2,
            'wednesday': 1.1,
            'thursday': 1.2,
            'friday': 1.5,
            'saturday': 0.8,
            'sunday': 0.6
        }
        
        # Facility-specific factors
        self.facility_factors = {
            'MTRH': {'base_multiplier': 1.0, 'capacity_factor': 1.0},
            'KNH': {'base_multiplier': 1.2, 'capacity_factor': 0.9},
            'Mbagathi': {'base_multiplier': 0.9, 'capacity_factor': 1.1},
            'Kenyatta': {'base_multiplier': 1.1, 'capacity_factor': 0.95}
        }
    
    def calculate_wait_time(self, facility_id: str, severity: str, current_patients: int = 0, 
                          facility_capacity: int = 50) -> Dict:
        """
        Calculate realistic wait time based on multiple factors
        
        Args:
            facility_id: Hospital/facility identifier
            severity: Patient triage severity (RED/YELLOW/GREEN)
            current_patients: Current number of patients waiting
            facility_capacity: Total capacity of the facility
            
        Returns:
            Dictionary with detailed wait time information
        """
        now = datetime.now()
        
        # Get base wait time for severity
        base_wait = self.base_wait_times.get(severity, 60)
        
        # Apply time-based multipliers
        time_multiplier = self._get_time_multiplier(now)
        
        # Apply day-based multipliers
        day_multiplier = self._get_day_multiplier(now)
        
        # Apply facility-specific factors
        facility_multiplier = self._get_facility_multiplier(facility_id)
        
        # Calculate capacity-based multiplier
        capacity_multiplier = self._get_capacity_multiplier(current_patients, facility_capacity)
        
        # Calculate seasonal factors (flu season, holidays, etc.)
        seasonal_multiplier = self._get_seasonal_multiplier(now)
        
        # Add random variation for realism
        random_variation = random.uniform(0.9, 1.1)
        
        # Calculate final wait time
        final_wait_time = base_wait * time_multiplier * day_multiplier * \
                         facility_multiplier * capacity_multiplier * \
                         seasonal_multiplier * random_variation
        
        # Ensure minimum wait times
        final_wait_time = max(final_wait_time, self.base_wait_times[severity])
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(final_wait_time, severity)
        
        return {
            'estimated_wait_minutes': round(final_wait_time, 1),
            'confidence_interval': confidence_interval,
            'factors_applied': {
                'base_wait': base_wait,
                'time_multiplier': time_multiplier,
                'day_multiplier': day_multiplier,
                'facility_multiplier': facility_multiplier,
                'capacity_multiplier': capacity_multiplier,
                'seasonal_multiplier': seasonal_multiplier,
                'random_variation': random_variation
            },
            'current_queue_length': current_patients,
            'capacity_utilization': round((current_patients / facility_capacity) * 100, 1),
            'calculation_time': now.isoformat(),
            'severity': severity,
            'facility_id': facility_id
        }
    
    def _get_time_multiplier(self, current_time: datetime) -> float:
        """Get time-based multiplier based on current hour"""
        hour = current_time.hour
        
        if 8 <= hour < 12:
            return self.time_multipliers['morning_peak']
        elif 14 <= hour < 18:
            return self.time_multipliers['afternoon_peak']
        elif 18 <= hour < 22:
            return self.time_multipliers['evening']
        elif 22 <= hour or hour < 6:
            return self.time_multipliers['night']
        else:  # 6 <= hour < 8
            return self.time_multipliers['early_morning']
    
    def _get_day_multiplier(self, current_time: datetime) -> float:
        """Get day-based multiplier"""
        day_name = current_time.strftime('%A').lower()
        return self.day_multipliers.get(day_name, 1.0)
    
    def _get_facility_multiplier(self, facility_id: str) -> float:
        """Get facility-specific multiplier"""
        facility_info = self.facility_factors.get(facility_id, {'base_multiplier': 1.0})
        return facility_info['base_multiplier']
    
    def _get_capacity_multiplier(self, current_patients: int, facility_capacity: int) -> float:
        """Calculate capacity-based multiplier"""
        if facility_capacity == 0:
            return 2.0  # High multiplier for unknown capacity
        
        utilization = current_patients / facility_capacity
        
        if utilization >= 0.9:
            return 2.5  # Very high wait times when over 90% full
        elif utilization >= 0.75:
            return 2.0  # High wait times when over 75% full
        elif utilization >= 0.5:
            return 1.5  # Moderate wait times when over 50% full
        elif utilization >= 0.25:
            return 1.2  # Slightly increased wait times
        else:
            return 1.0  # Normal wait times
    
    def _get_seasonal_multiplier(self, current_time: datetime) -> float:
        """Calculate seasonal multiplier (flu season, holidays, etc.)"""
        month = current_time.month
        
        # Flu season (November to March in Kenya)
        if month in [11, 12, 1, 2, 3]:
            return 1.3
        
        # Holiday seasons
        if month == 12:  # December holidays
            return 1.4
        
        # Rainy season (March to May, October to December)
        if month in [3, 4, 5, 10, 11, 12]:
            return 1.2
        
        return 1.0
    
    def _calculate_confidence_interval(self, wait_time: float, severity: str) -> Dict:
        """Calculate confidence interval for wait time estimate"""
        # Higher severity = more accurate predictions
        if severity == 'RED':
            variance = 0.1  # ±10%
        elif severity == 'YELLOW':
            variance = 0.2  # ±20%
        else:  # GREEN
            variance = 0.3  # ±30%
        
        lower_bound = wait_time * (1 - variance)
        upper_bound = wait_time * (1 + variance)
        
        return {
            'lower_bound': round(lower_bound, 1),
            'upper_bound': round(upper_bound, 1),
            'confidence_level': 0.85
        }
    
    def get_optimal_facility(self, user_lat: float, user_lng: float, 
                           facilities: List[Dict], severity: str) -> Dict:
        """
        Find optimal facility based on distance and wait time
        
        Args:
            user_lat, user_lng: User's coordinates
            facilities: List of facility dictionaries
            severity: Patient triage severity
            
        Returns:
            Dictionary with optimal facility and alternatives
        """
        facility_scores = []
        
        for facility in facilities:
            facility_id = facility.get('facility_id', 'unknown')
            facility_coords = facility.get('coordinates', {})
            
            if not facility_coords:
                continue
            
            facility_lat = facility_coords.get('lat')
            facility_lng = facility_coords.get('lng')
            
            # Calculate distance
            distance = self._calculate_distance(user_lat, user_lng, facility_lat, facility_lng)
            
            # Get current patient count (mock data for now)
            current_patients = random.randint(5, 45)
            facility_capacity = facility.get('capacity', {}).get('emergency_beds', 50)
            
            # Calculate wait time
            wait_time_info = self.calculate_wait_time(
                facility_id, severity, current_patients, facility_capacity
            )
            
            # Calculate composite score (lower is better)
            distance_score = distance / 50  # Normalize distance (max 50km)
            wait_score = wait_time_info['estimated_wait_minutes'] / 240  # Normalize wait time (max 4 hours)
            
            # Weight factors based on severity
            if severity == 'RED':
                distance_weight = 0.3
                wait_weight = 0.7
            elif severity == 'YELLOW':
                distance_weight = 0.5
                wait_weight = 0.5
            else:  # GREEN
                distance_weight = 0.7
                wait_weight = 0.3
            
            composite_score = (distance_score * distance_weight) + (wait_score * wait_weight)
            
            facility_scores.append({
                'facility': facility,
                'distance_km': round(distance, 2),
                'wait_time_info': wait_time_info,
                'composite_score': round(composite_score, 3),
                'recommendation': self._generate_recommendation(composite_score, severity)
            })
        
        # Sort by composite score
        facility_scores.sort(key=lambda x: x['composite_score'])
        
        return {
            'optimal_facility': facility_scores[0] if facility_scores else None,
            'alternatives': facility_scores[1:4] if len(facility_scores) > 1 else [],
            'total_facilities_analyzed': len(facility_scores),
            'calculation_time': datetime.now().isoformat()
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Earth's radius in kilometers
    
    def _generate_recommendation(self, score: float, severity: str) -> str:
        """Generate recommendation based on facility score"""
        if score <= 0.3:
            return "Highly Recommended - Optimal choice"
        elif score <= 0.5:
            return "Recommended - Good option"
        elif score <= 0.7:
            return "Acceptable - Consider alternatives"
        else:
            return "Not Recommended - Look for better options"

# Global instance
wait_time_calculator = WaitTimeCalculator()
