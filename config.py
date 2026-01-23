# SmartTriage AI Configuration
# Copy this file to .env and fill in your actual values

# Google Places API Configuration
# Get your API key from: https://console.cloud.google.com/apis/credentials
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_GOOGLE_PLACES_API_KEY_HERE')

# Hugging Face API Configuration
# Get your API token from: https://huggingface.co/settings/tokens
HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN', 'YOUR_HUGGINGFACE_API_TOKEN_HERE')

# API Settings
GOOGLE_PLACES_SEARCH_RADIUS = 10000  # 10km radius in meters
GOOGLE_PLACES_COUNTRY_RESTRICTION = "ke"  # Kenya
GOOGLE_PLACES_PLACE_TYPES = ["hospital", "clinic", "health", "medical_center", "emergency_room"]

import os
