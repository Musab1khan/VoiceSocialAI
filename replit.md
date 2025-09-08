# AI Voice Assistant

## Overview

This is a Flask-based AI Voice Assistant that provides voice command processing, social media automation, and auto-reply functionality. The system integrates multiple services including Google's Gemini AI, Facebook Graph API, Gmail API, and WhatsApp Business API to create a comprehensive digital assistant. Users can issue voice commands to post on Facebook, generate AI responses, manage email auto-replies, and monitor system activities through a web dashboard.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with configurable database URL via environment variables
- **Background Processing**: APScheduler for background task management including email monitoring
- **Session Management**: Flask sessions with configurable secret key

### Voice Processing System
- **Speech Recognition**: Web-based SpeechRecognition API (webkitSpeechRecognition) for voice input
- **Text-to-Speech**: pyttsx3 library for voice output with configurable voice properties
- **Command Classification**: AI-powered command processing using Gemini API for natural language understanding

### AI Integration
- **Primary AI Service**: Google Gemini 2.5-flash model for text generation, command processing, and content creation
- **Content Generation**: Specialized prompts for Facebook posts, auto-replies, and general queries
- **Response Processing**: Structured response handling with success/error states

### Social Media Integration
- **Facebook**: Graph API v17.0 integration for text and photo posts to Facebook pages
- **Content Strategy**: AI-generated posts with emoji support and hashtag optimization
- **Post Tracking**: Database logging of all social media posts with status tracking

### Communication Services
- **Email**: Gmail API integration with OAuth2 authentication for reading and sending emails
- **WhatsApp**: WhatsApp Business API integration for message sending and webhook processing
- **Auto-Reply System**: Scheduled background monitoring with AI-generated contextual responses

### Database Schema
- **CommandHistory**: Tracks all voice commands with execution status and results
- **AutoReplyLog**: Logs all auto-reply activities across platforms
- **SocialMediaPost**: Records all social media posts with metadata
- **Settings**: Key-value store for application configuration

### Frontend Architecture
- **UI Framework**: Bootstrap with dark theme for consistent styling
- **JavaScript**: Vanilla JavaScript for voice control, dashboard updates, and real-time status
- **Real-time Updates**: AJAX-based dashboard refreshing and command status updates
- **Responsive Design**: Mobile-friendly interface with progressive enhancement

### Security & Configuration
- **Environment Variables**: All API keys and sensitive configuration via environment variables
- **OAuth Integration**: Google OAuth2 for Gmail access with token refresh handling
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

## External Dependencies

### AI Services
- **Google Gemini API**: Text generation, command processing, and content creation
- **Gemini 2.5-flash model**: Primary AI model for all natural language tasks

### Social Media APIs
- **Facebook Graph API v17.0**: Page posting and content management
- **WhatsApp Business API**: Message sending and webhook handling

### Google Services
- **Gmail API**: Email reading and sending with OAuth2 authentication
- **Google Auth Libraries**: OAuth2 flow and credential management

### Voice Processing
- **pyttsx3**: Text-to-speech synthesis
- **Web Speech API**: Browser-based speech recognition

### Infrastructure
- **Flask**: Web framework with SQLAlchemy ORM
- **APScheduler**: Background task scheduling
- **SQLite**: Default database (configurable for other databases)