# 🤖 AI Voice Assistant - Local Setup Instructions

## System Requirements

- **Python 3.8+** (recommended: Python 3.10 or later)
- **Operating System**: Linux, macOS, or Windows
- **Audio System**: Speakers/headphones for text-to-speech output
- **Microphone**: For voice input (browser-based)

## Installation Steps

### 1. Clone/Download the Project
```bash
# If from GitHub
git clone [your-repository-url]
cd ai-voice-assistant

# Or download and extract the ZIP file
```

### 2. Install Python Dependencies

**Option A: Using pip (Standard)**
```bash
pip install -r requirements.txt
```

**Option B: Using uv (Faster - Recommended)**
```bash
# Install uv first
pip install uv

# Install dependencies with uv
uv pip install -r requirements.txt
```

### 3. Install System Dependencies (Linux/macOS)

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install espeak-ng espeak-ng-data
```

**For CentOS/RHEL:**
```bash
sudo yum install espeak-ng
```

**For macOS:**
```bash
brew install espeak-ng
```

**For Windows:**
- Download eSpeak-ng from: https://github.com/espeak-ng/espeak-ng/releases
- Install the Windows executable
- Add eSpeak to your system PATH

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.example .env

# Edit the file with your API keys
nano .env
```

Required environment variables:
```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///voice_assistant.db

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Social Media (Optional)
FACEBOOK_ACCESS_TOKEN=your-facebook-token
FACEBOOK_PAGE_ID=your-facebook-page-id

# Email Integration (Optional)
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret

# WhatsApp Business (Optional)
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=your-whatsapp-verify-token

# OpenAI (Optional - Backup AI Service)
OPENAI_API_KEY=your-openai-api-key
```

### 5. Initialize the Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run the Application

**Development Mode:**
```bash
python app.py
```

**Production Mode:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

The application will be available at: http://localhost:5000

## Getting API Keys

### 🤖 Google Gemini API Key (Required)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to your `.env` file

### 📘 Facebook Integration (Optional)
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Pages" product
4. Get Page Access Token
5. Find your Page ID from your Facebook page settings

### 📧 Gmail Integration (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials JSON
6. Extract client_id and client_secret

### 📱 WhatsApp Business (Optional)
1. Go to [Meta for Developers](https://developers.facebook.com/products/whatsapp/)
2. Set up WhatsApp Business API
3. Get access token and verify token
4. Configure webhook URL: `https://yourdomain.com/whatsapp-webhook`

## Features Available

### ✅ Core Features (No API Keys Required)
- Voice recognition (browser-based)
- Text-to-speech output
- System status commands
- Web interface

### 🔑 Premium Features (Require API Keys)
- AI text generation and responses
- Image generation with AI
- Facebook post automation
- Email auto-reply system
- WhatsApp message automation

## Usage

1. **Open the web interface**: http://localhost:5000
2. **Voice Commands**: Click "Start Listening" and speak
3. **Settings**: Configure API keys at http://localhost:5000/settings
4. **Dashboard**: View activity at http://localhost:5000/dashboard

## Common Voice Commands

- **"How are you"** → System status
- **"Generate an image of [description]"** → AI image creation
- **"Create a Facebook post about [topic]"** → Social media post
- **"What is [question]"** → AI-powered answers
- **"Check auto-reply status"** → Email monitoring status

## Troubleshooting

### Voice Not Working
```bash
# Test eSpeak installation
espeak "Hello, this is a test"

# Check audio system
aplay /usr/share/sounds/alsa/Front_Left.wav  # Linux
```

### Database Errors
```bash
# Reset database
rm -f voice_assistant.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### API Key Issues
- Verify keys are correct in `.env` file
- Check API key permissions and quotas
- Restart the application after changing keys

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)

# Or use different port
python app.py --port 8080
```

## Project Structure

```
ai-voice-assistant/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── routes/
│   ├── api_routes.py     # API endpoints
│   └── main_routes.py    # Web page routes
├── services/
│   ├── voice_service.py  # Text-to-speech
│   ├── gemini_service.py # AI integration
│   ├── facebook_service.py # Social media
│   └── email_service.py  # Email automation
├── templates/            # HTML templates
├── static/              # CSS, JS, images
└── voice_assistant.db   # SQLite database (auto-created)
```

## Production Deployment

For production deployment, consider:

1. **Use PostgreSQL** instead of SQLite
2. **Set up proper SSL** certificates
3. **Configure firewall** rules
4. **Use environment-specific** configuration
5. **Set up monitoring** and logging
6. **Use a reverse proxy** like Nginx

Example production command:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure API keys have proper permissions
4. Test with minimal configuration first

Happy voice commanding! 🎤✨