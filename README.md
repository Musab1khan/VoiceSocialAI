# 🤖 AI Voice Assistant

A comprehensive Flask-based AI Voice Assistant that provides voice command processing, social media automation, and auto-reply functionality. The system integrates multiple AI services including Google's Gemini AI, Facebook Graph API, Gmail API, and WhatsApp Business API.

## ✨ Features

- 🎤 **Voice Recognition**: Browser-based speech recognition for natural voice commands
- 🔊 **Text-to-Speech**: Audio responses using pyttsx3 with customizable voices
- 🤖 **AI Integration**: Multiple AI services (Gemini, OpenAI, Hugging Face, AI/ML API) for intelligent responses
- ✍️ **Advanced Text AI**: Natural human-like content generation for posts, articles, blogs, emails, stories, and more
- 📱 **Social Media Automation**: Automated Facebook posting with AI-generated content
- 📧 **Email Auto-Reply**: Gmail integration with intelligent auto-responses
- 💬 **WhatsApp Integration**: Business API integration for messaging
- 🖼️ **Image Generation**: AI-powered image creation and sharing
- 🔖 **Smart Hashtags**: Automatic hashtag generation and SEO optimization
- 📊 **Dashboard**: Real-time monitoring of activities and system status
- 🔧 **Settings Panel**: Easy API key management and configuration

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (recommended: Python 3.10 or later)
- **Git** (for cloning the repository)
- **Audio System** (speakers/headphones for voice output)
- **Modern Web Browser** (Chrome/Firefox recommended for voice input)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-voice-assistant
```

### 2. Install Python Dependencies

**Method A: Using pip (Standard)**
```bash
pip install -r requirements.txt
```

**Method B: Using uv (Recommended - Faster)**
```bash
# Install uv first
pip install uv

# Install dependencies
uv sync
```

### 3. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install espeak-ng espeak-ng-data
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install espeak-ng
# or for newer versions:
sudo dnf install espeak-ng
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install espeak-ng
brew install espeak-ng
```

**Windows:**
1. Download eSpeak-ng from: https://github.com/espeak-ng/espeak-ng/releases
2. Install the Windows executable
3. Add eSpeak to your system PATH

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=sqlite:///assistant.db

# AI Services (At least one required)
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Social Media (Optional)
FACEBOOK_ACCESS_TOKEN=your-facebook-token
FACEBOOK_PAGE_ID=your-facebook-page-id

# Email Integration (Optional)
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret

# WhatsApp Business (Optional)
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=your-whatsapp-verify-token

# Image Generation APIs (Optional)
DEEPAI_API_KEY=your-deepai-api-key
REPLICATE_API_KEY=your-replicate-api-key
STABILITY_API_KEY=your-stability-api-key

# Voice APIs (Optional)
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

### 5. Initialize the Database

```bash
# Using uv
uv run python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Or using regular python
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run the Application

**Development Mode:**
```bash
# Using uv
uv run python app.py

# Or using regular python
python app.py
```

**Production Mode:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

🎉 **Your AI Voice Assistant is now running at:** http://localhost:5000

## 🔑 Getting API Keys

### 🤖 Google Gemini API Key (Recommended)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

### 🧠 OpenAI API Key (Alternative)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and add billing information
3. Generate a new API key
4. Add to your `.env` file

### 📘 Facebook Integration (Optional)
1. Visit [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Pages" product
4. Get Page Access Token and Page ID
5. Add both to your `.env` file

### 📧 Gmail Integration (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download credentials and extract client_id and client_secret

### 📱 WhatsApp Business API (Optional)
1. Visit [Meta for Developers](https://developers.facebook.com/products/whatsapp/)
2. Set up WhatsApp Business API
3. Get access token and create verify token
4. Configure webhook URL: `https://yourdomain.com/api/whatsapp-webhook`

## 🎯 Usage Guide

### Web Interface
1. **Main Dashboard**: http://localhost:5000
2. **Settings**: http://localhost:5000/settings
3. **Activity Dashboard**: http://localhost:5000/dashboard

### Voice Commands Examples

#### Text Generation Commands
- **"Write a blog article about artificial intelligence"** → AI blog post creation
- **"Create a social media post about healthy eating"** → Social media content with hashtags
- **"Write an email reply about the project update"** → Professional email responses
- **"Generate a product description for smartphones"** → Marketing copywriting
- **"Write a creative story about space exploration"** → Imaginative storytelling
- **"Create a tutorial on web development"** → Educational content
- **"Write a review of the latest movie"** → Balanced review content

#### Other Commands
- **"How are you"** → System status and health check
- **"Generate an image of a sunset"** → AI image creation
- **"Create a Facebook post about technology"** → Automated social media posting
- **"What is artificial intelligence?"** → AI-powered question answering
- **"Check auto-reply status"** → Email monitoring system status

### Manual Controls
- **Voice Test**: Test text-to-speech functionality
- **API Configuration**: Update API keys through web interface
- **Manual Auto-Reply**: Trigger email processing manually
- **Command History**: View all processed voice commands

## 🛠️ Troubleshooting

### Voice Not Working
```bash
# Test eSpeak installation
espeak "Hello, this is a test"

# Check audio system (Linux)
aplay /usr/share/sounds/alsa/Front_Left.wav

# macOS audio test
say "Hello, this is a test"
```

### Database Issues
```bash
# Reset database completely
rm -f assistant.db
uv run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)

# Or use different port
python app.py --port 8080
```

### API Key Issues
- Verify API keys are correct and have proper permissions
- Check API quotas and billing status
- Restart the application after updating keys
- Test individual APIs through the settings page

### Permission Errors (Linux/macOS)
```bash
# Fix audio permissions
sudo usermod -a -G audio $USER

# Reboot or re-login after adding to audio group
```

## 📁 Project Structure

```
ai-voice-assistant/
├── app.py                 # Main Flask application
├── main.py               # Entry point
├── models.py             # Database models
├── pyproject.toml        # Python dependencies (uv)
├── requirements.txt      # Python dependencies (pip)
├── .env                  # Environment variables (create this)
├── routes/
│   ├── api_routes.py     # REST API endpoints
│   └── main_routes.py    # Web page routes
├── services/
│   ├── voice_service.py  # Text-to-speech engine
│   ├── gemini_service.py # Google Gemini AI
│   ├── multi_ai_service.py # Multiple AI providers
│   ├── facebook_service.py # Social media automation
│   ├── email_service.py  # Gmail integration
│   ├── whatsapp_service.py # WhatsApp Business API
│   └── command_processor.py # Voice command processing
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── settings.html
├── static/              # CSS, JavaScript, assets
│   ├── css/style.css
│   └── js/
│       ├── voice-control.js
│       └── dashboard.js
└── assistant.db        # SQLite database (auto-created)
```

## 🚀 Production Deployment

### Using Gunicorn (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y espeak-ng
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Environment Considerations
- Use PostgreSQL instead of SQLite for production
- Set up SSL certificates (HTTPS)
- Configure firewall rules
- Use environment-specific configuration
- Set up monitoring and logging
- Use a reverse proxy like Nginx

## 🔧 Configuration Options

### Voice Settings
- Voice speed, pitch, and volume can be adjusted
- Multiple voice engines supported
- Language and accent selection

### AI Models
- Multiple AI providers supported
- Fallback mechanisms for reliability
- Custom prompt templates

### Security
- API key encryption in transit
- Session management
- CORS configuration
- Proxy support for deployment

## 📊 Monitoring & Logs

### Application Logs
- All activities are logged with timestamps
- Error tracking and debugging information
- Performance metrics available

### Dashboard Features
- Real-time command processing status
- API usage statistics
- System health monitoring
- Recent activity timeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify dependencies** are installed correctly
3. **Test API keys** have proper permissions
4. **Try minimal configuration** first
5. **Restart the application** after changes

For additional help, please open an issue in the repository.

---

**Happy voice commanding! 🎤✨**