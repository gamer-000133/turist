# 🛡️ Smart Tourist Safety Monitoring System

A comprehensive Flask-based web application for monitoring tourist safety with AI-powered anomaly detection, real-time alerts, and emergency response features.

## 🚀 Features

### Tourist Portal
- **Digital Tourist ID**: Generate QR code-based digital IDs
- **Emergency Panic Button**: Instant alert system with GPS location
- **Real-time Location Tracking**: Continuous GPS monitoring
- **Multilingual Support**: English and Hindi (expandable)

### Police Dashboard
- **Live Tourist Heatmap**: Real-time location visualization
- **Alert Management**: View and resolve emergency alerts
- **E-FIR System**: Digital incident reporting
- **Tourist Registry**: Complete tourist database

### AI Anomaly Detection
- **Inactivity Detection**: Alerts when tourist inactive >15 minutes
- **Route Deviation**: Detects significant movement from expected paths
- **Suspicious Activity**: AI-powered behavioral analysis
- **Automated Alerts**: Real-time notifications to authorities

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5 + Leaflet.js
- **Database**: SQLite
- **AI Engine**: Python-based anomaly detection
- **Maps**: OpenStreetMap via Leaflet
- **QR Codes**: Python qrcode library

## 📦 Installation

1. **Clone/Download the project**
   ```bash
   cd smart-tourist-safety
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup (optional)**
   ```bash
   python setup.py
   ```

4. **Start the Flask application**
   ```bash
   python app.py
   ```

5. **Start AI monitoring (in another terminal)**
   ```bash
   python ai_engine.py
   ```

6. **Open your browser**
   ```
   http://127.0.0.1:5000/
   ```

## 🎯 Usage Guide

### For Tourists:
1. Visit the Tourist Portal
2. Register with your details
3. Save your QR code and Tourist ID
4. Use the panic button in emergencies
5. Keep location services enabled

### For Authorities:
1. Access the Police Dashboard
2. Monitor live tourist locations
3. Respond to alerts and incidents
4. Create E-FIRs for incidents
5. Track tourist safety metrics

### AI Monitoring:
- The AI engine runs continuously
- Automatically detects anomalies
- Sends alerts to the dashboard
- No manual intervention required

## 🗂️ Project Structure

```
smart-tourist-safety/
├── app.py              # Main Flask application
├── models.py           # Database models
├── ai_engine.py        # AI anomaly detection
├── requirements.txt    # Python dependencies
├── setup.py           # Setup script
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── tourist.html
│   └── dashboard.html
├── static/            # CSS/JS files (auto-created)
└── tourist.db         # SQLite database (auto-created)
```

## 🔧 Configuration

### Database
- SQLite database is created automatically
- Location: `tourist.db` in project root
- No additional setup required

### AI Engine Settings
- Inactivity threshold: 15 minutes (configurable in `ai_engine.py`)
- Route deviation sensitivity: 5km (adjustable)
- Monitoring interval: 60 seconds

### Security
- Change the secret key in `app.py` for production
- Enable HTTPS for production deployment
- Implement proper authentication for dashboard access

## 🌐 API Endpoints

- `POST /register` - Tourist registration
- `POST /login` - Tourist login
- `POST /panic_alert` - Emergency alert
- `GET /api/tourists` - Get all tourists
- `GET /api/alerts` - Get active alerts
- `POST /api/create_incident` - Create E-FIR

## 🚨 Testing the System

1. **Register a Tourist**:
   - Go to Tourist Portal
   - Fill registration form
   - Save the generated QR code

2. **Test Panic Button**:
   - Login with Tourist ID
   - Click the red panic button
   - Check dashboard for alert

3. **AI Anomaly Detection**:
   - Run `python ai_engine.py`
   - Wait for automatic alerts
   - Check dashboard for AI-generated alerts

## 🔮 Future Enhancements

- Real blockchain integration for tourist IDs
- Advanced ML models for anomaly detection
- Mobile app development
- Integration with government databases
- Multi-language support expansion
- Real-time chat support
- Geofencing capabilities
- Weather and safety advisories

## 📝 License

This project is for educational and demonstration purposes. Modify as needed for production use.

## 🤝 Contributing

Feel free to fork, modify, and improve this system. Pull requests welcome!

---

**⚠️ Note**: This is a demonstration system. For production use, implement proper security measures, authentication, and data protection protocols.