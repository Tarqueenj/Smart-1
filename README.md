# SmartTriage AI

An AI-powered patient triage and prioritization platform designed to improve emergency and outpatient care in high-volume hospitals in Eldoret, Kenya.

## 🚀 Quick Setup (Windows)

1. **Clone and run setup script:**
   ```bash
   git clone https://github.com/Tarqueenj/Smart-1.git
   cd Smart-1
   setup.bat
   ```

2. **Or manual setup:**
   ```bash
   git clone https://github.com/Tarqueenj/Smart-1.git
   cd Smart-1
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   python app.py
   ```

3. **Access the application:**
   - Main: http://localhost:5000
   - Login: http://localhost:5000/login
   - Nurse: http://localhost:5000/nurse
   - Clinician: http://localhost:5000/clinician
   - Admin: http://localhost:5000/admin

4. **Test credentials:**
   - Nurse: `nurse` / `nurse123`
   - Clinician: `clinician` / `clinician123`
   - Admin: `admin` / `admin123`

📖 **Detailed setup**: See `GITHUB_SETUP.txt` for complete instructions

## 🏥 Overview

SmartTriage AI enables patients to report symptoms through a simple mobile or web interface using text or voice. Using OpenAI's natural language processing, the system analyzes patient-reported symptoms against established clinical triage protocols and assigns a real-time severity score (Red, Yellow, or Green).

The system moves beyond traditional digital registration by actively supporting clinical decision-making, surfacing high-risk cases with "silent" symptoms such as sepsis, internal bleeding, or pregnancy-related complications.

## 🌟 Key Features

### Patient-Facing Features
- **Symptom Reporting**: Text and voice input with local language support
- **AI Pre-Triage**: Real-time severity scoring (Red/Yellow/Green)
- **Facility Recommendation**: Google Maps integration for optimal facility routing

### Nurse Dashboard
- **Real-Time Patient Queue**: Live prioritized patient list
- **Risk Flags**: Automatic alerts for critical conditions
- **Queue Management**: Update patient status and track progress

### Clinician Interface
- **Clinical Summaries**: AI-generated patient assessments
- **Decision Support**: Differential diagnosis suggestions
- **Quick Actions**: Order labs, imaging, and prescriptions

### Admin Dashboard
- **Analytics**: Patient flow and resource utilization
- **Performance Metrics**: AI accuracy and system uptime
- **Resource Optimization**: Staff allocation and capacity management

## 🛠 Technology Stack

### Backend
- **Flask**: Python web framework
- **MongoDB**: NoSQL database for patient data
- **Flask-PyMongo**: MongoDB integration
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **HTML5/CSS3/JavaScript**: Responsive web interface
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Data visualization
- **Font Awesome**: Icon library

### AI & APIs
- **OpenAI NLP**: Natural language processing for symptom analysis
- **Google Maps API**: Facility routing and distance calculation
- **Mock AI Logic**: Simulated triage scoring for demonstration

## 🚀 Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Node.js 14+ (for development tools)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smarttriage-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   ```bash
   # Start MongoDB service
   mongod
   
   # Create database (automatically created on first run)
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Main site: http://localhost:5000
   - Patient Portal: http://localhost:5000/patient
   - Nurse Dashboard: http://localhost:5000/nurse
   - Clinician View: http://localhost:5000/clinician
   - Admin Panel: http://localhost:5000/admin

## 📱 Mobile Responsiveness

The application is fully responsive and optimized for mobile devices:
- Touch-friendly interfaces
- Adaptive layouts for all screen sizes
- Voice input support on compatible devices
- Progressive Web App capabilities

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/smarttriage_db

# API Keys (for production)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### Customization
- Modify AI triage logic in `app.py` - `calculate_triage_score()` function
- Update hospital facilities in `/api/get_facilities` endpoint
- Customize styling in `templates/base.html` and CSS files

## 🏗 Project Structure

```
smarttriage-ai/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page
│   ├── patient.html     # Patient portal
│   ├── nurse.html       # Nurse dashboard
│   ├── clinician.html   # Clinician interface
│   └── admin.html       # Admin dashboard
├── static/              # Static assets
│   ├── css/
│   │   └── mobile.css   # Mobile-specific styles
│   └── js/
│       └── app.js       # Main JavaScript application
└── venv/               # Virtual environment
```

## 🤖 AI Triage Logic

The system uses a sophisticated triage algorithm that considers:

### Emergency (Red) Indicators
- Severe pain, chest pain, difficulty breathing
- Unconsciousness, seizures, confusion
- Bleeding, fever with fast breathing
- Pregnancy complications

### Urgent (Yellow) Indicators
- Moderate pain, headache, nausea
- Vomiting, diarrhea, cough, sore throat
- Fatigue, dizziness

### Non-Urgent (Green) Indicators
- Mild symptoms not requiring immediate attention
- Routine follow-up cases

## 📊 Analytics & Reporting

The admin dashboard provides comprehensive analytics:
- Patient flow analysis by time period
- Severity distribution trends
- Department capacity monitoring
- Staff allocation optimization
- AI performance metrics

## 🔒 Security Features

- HIPAA-compliant data handling principles
- Encrypted data transmission
- Role-based access control
- Audit logging for all actions
- Secure session management

## 🌐 API Endpoints

### Patient Management
- `POST /api/submit_symptoms` - Submit patient symptoms for triage
- `GET /api/get_patients` - Retrieve patient queue
- `POST /api/update_patient_status` - Update patient status

### Analytics
- `GET /api/get_analytics` - Retrieve dashboard analytics
- `GET /api/get_facilities` - Get facility recommendations

### Search & Updates
- `GET /api/search` - Quick search functionality
- `GET /api/updates` - Real-time updates

## 🧪 Testing

### Manual Testing
1. **Patient Flow Test**:
   - Visit `/patient`
   - Enter test symptoms (e.g., "severe chest pain and difficulty breathing")
   - Verify AI triage results
   - Check facility recommendations

2. **Nurse Dashboard Test**:
   - Visit `/nurse`
   - Verify patient queue displays correctly
   - Test status updates
   - Check critical alerts

3. **Clinician Interface Test**:
   - Visit `/clinician`
   - Select a patient from queue
   - Review clinical summary
   - Test AI recommendations

4. **Admin Dashboard Test**:
   - Visit `/admin`
   - Verify analytics display
   - Check charts and metrics
   - Test resource optimization features

### Automated Testing
```bash
# Run Python tests (if implemented)
python -m pytest tests/

# Run JavaScript tests (if implemented)
npm test
```

## 🚀 Deployment

### Production Setup
1. **Environment Setup**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret
   ```

2. **Database Configuration**:
   - Configure MongoDB with authentication
   - Set up replica sets for high availability
   - Implement backup strategy

3. **Web Server**:
   ```bash
   # Using Gunicorn
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Reverse Proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@smarttriage.ai
- Documentation: [Project Wiki]
- Issues: [GitHub Issues]

## 🙏 Acknowledgments

- Moi Teaching and Referral Hospital (MTRH) for partnership
- OpenAI for NLP capabilities
- Google Maps API for location services
- Healthcare professionals in Eldoret for clinical insights

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Basic triage functionality
- ✅ Multi-user dashboards
- ✅ Mobile responsiveness
- ✅ Analytics dashboard

### Phase 2 (Upcoming)
- 🔄 Real WebSocket integration
- 🔄 Advanced AI model training
- 🔄 Multi-language support
- 🔄 Integration with hospital EMR systems

### Phase 3 (Future)
- 📋 Machine learning for outcome prediction
- 📋 Telemedicine integration
- 📋 Mobile app development
- 📋 Regional expansion

---

**SmartTriage AI** - Revolutionizing emergency care in Kenya through intelligent triage and prioritization.
