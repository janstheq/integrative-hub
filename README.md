# IntegrativeHub - Academic Wellness & Productivity Platform

A comprehensive Flask web application with Google OAuth authentication, featuring weather monitoring, joke automation, text encryption, and an academic wellness tracker powered by FastAPI.

## 🚀 Features

- **🔐 Google OAuth 2.0** - Secure login with Gmail
- **☀️ Weather Monitoring** - Real-time weather data with OpenWeatherMap API
- **🎭 Joke Automation** - Random jokes with QR code generation and email sharing
- **🔒 Text Encryption** - Multiple cipher support (Atbash, Caesar, Vigenere)
- **💚 Wellness Tracker** - Track mood, sleep, goals, and breaks (FastAPI microservice)

## 📋 Prerequisites

- Python 3.8+
- Gmail account (for OAuth and email features)
- OpenWeatherMap API key
- Google Cloud Project (for OAuth credentials)

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/integrative-hub.git
cd integrative-hub
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create `config.py` with your API keys
```python
OPENWEATHER_API_KEY = 'your_key'
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
GOOGLE_CLIENT_ID = 'your_client_id'
GOOGLE_CLIENT_SECRET = 'your_client_secret'
```

4. Start the FastAPI wellness tracker
```bash
python wellness_api.py
```

5. Start the Flask app (in another terminal)
```bash
python app.py
```

6. Visit `http://127.0.0.1:8000`

## 📁 Project Structure
```
integrative-hub/
├── app.py                 # Main Flask application
├── wellness_api.py        # FastAPI wellness tracker
├── config.py             # API keys (not in git)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── static/
│   └── styles.css       # Main stylesheet
└── templates/
    ├── base.html        # Base template
    ├── home.html        # Landing page
    ├── dashboard.html   # Main dashboard
    ├── weather.html     # Weather monitoring
    ├── jokes.html       # Joke automation
    ├── encrypt.html     # Text encryption
    ├── wellness.html    # Wellness tracker
    └── profile.html     # User profile
```

## 🔑 Environment Variables

Set these environment variables or use `config.py`:

- `OPENWEATHER_API_KEY` - OpenWeatherMap API key
- `EMAIL_ADDRESS` - Your Gmail address
- `EMAIL_PASSWORD` - Gmail app password
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

## 📦 Dependencies

See `requirements.txt` for full list:
- Flask
- FastAPI
- Authlib
- qrcode
- requests
- uvicorn

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📄 License

MIT License

## 👤 Author

Janus Daquio - https://github.com/janstheq
```

---

### **Step 4: Create requirements.txt**

Create `requirements.txt` with all your dependencies:
```
Flask==3.0.0
authlib==1.3.0
requests==2.31.0
qrcode[pil]==7.4.2
Pillow==10.1.0
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
