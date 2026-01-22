# Google Places API Integration Setup

## Overview
SmartTriage AI now supports Google Places API for finding hospitals and medical facilities near the user's location.

## Features Added
- **Google Places Autocomplete**: Smart search suggestions as you type
- **Nearby Hospital Search**: Find hospitals within 10km radius
- **Real-time Data**: Ratings, opening hours, photos, and more
- **Fallback System**: Uses local database if Google Places fails

## Setup Instructions

### 1. Get Google Places API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable **Places API** from the API library
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy your API key

### 2. Configure the Application

#### Option A: Update Config File (Recommended)
Edit `config.py` and replace:
```python
GOOGLE_PLACES_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

#### Option B: Update Frontend Directly
Edit `templates/patient.html` and replace:
```javascript
let GOOGLE_PLACES_API_KEY = 'YOUR_ACTUAL_API_KEY_HERE';
```

#### Option C: Environment Variable (Production)
```bash
export GOOGLE_PLACES_API_KEY="your_api_key_here"
```

### 3. Restart the Application
```bash
python simple_app.py  # or python app.py
```

## API Features

### Search Types
- **Text Search**: "hospital nairobi" → finds hospitals in Nairobi
- **Nearby Search**: Uses GPS location to find nearby hospitals
- **Autocomplete**: Real-time suggestions as you type

### Data Provided
- Hospital name and address
- GPS coordinates
- Distance from user location
- Google ratings and reviews
- Opening hours status
- Phone numbers (when available)
- Place photos (when available)

## Usage Examples

### Frontend JavaScript
```javascript
// Search for hospitals
const hospitals = await googlePlacesSearch("hospital nairobi");

// Get nearby hospitals
const nearby = await getCurrentLocationHospitals();
```

### Backend API Endpoints
```bash
# Search hospitals
POST /api/google_places_search
{
  "query": "hospital nairobi",
  "location": {"lat": -1.2921, "lng": 36.8219}
}

# Response
{
  "success": true,
  "hospitals": [...],
  "total_found": 15,
  "search_type": "text_search"
}
```

## Rate Limits
- **Google Places**: $2.83 per 1000 requests (free tier: $200 monthly credit)
- **Application**: 20 requests per minute per user

## Security Notes
- API key is client-side (required for Google Places JavaScript)
- In production, consider using a backend proxy to hide the API key
- Enable API key restrictions in Google Cloud Console

## Troubleshooting

### Common Issues
1. **"API key not configured"** → Update config.py with your API key
2. **"OVER_QUERY_LIMIT"** → Wait and retry, or upgrade your plan
3. **"REQUEST_DENIED"** → Check API key permissions and restrictions

### Fallback Behavior
If Google Places API fails:
- Falls back to local hospital database
- Still provides basic hospital information
- Shows error message but remains functional

## Testing
1. Open Patient Portal: http://localhost:5000/patient
2. Click "Search Hospitals"
3. Type "hospital" + your location
4. Select a hospital from suggestions
5. View detailed hospital information

## Production Deployment
For production use:
1. Use environment variables for API keys
2. Enable API key restrictions (IP addresses, referrers)
3. Monitor usage in Google Cloud Console
4. Consider implementing a backend proxy for API calls
