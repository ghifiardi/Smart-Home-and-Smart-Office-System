# AI Personal Assistant for Mac & iPhone

A voice-controlled personal assistant that handles routine tasks including PowerPoint presentations, Outlook emails, calendar management, and WhatsApp messaging.

## Features

### 🎤 Voice Commands
- Natural language processing for intuitive voice commands
- Wake word activation ("assistant")
- Real-time speech recognition
- Voice feedback for all operations

### 📊 PowerPoint Automation
- Create presentations with voice commands
- Add slides with titles and content
- Save and manage presentations
- Example: "Create a presentation called Quarterly Report"

### 📧 Email Management
- Send emails via Outlook/Office 365
- Read recent emails
- Search emails by keyword
- Example: "Send an email to john@example.com subject Meeting message Let's schedule a call"

### 📅 Calendar Integration
- Schedule meetings and events
- Check today's schedule
- View upcoming events
- Google Calendar integration
- Example: "Schedule a meeting called Team Standup at 2 PM for 1 hour"

### 💬 WhatsApp Messaging
- Send WhatsApp messages
- Schedule messages for later
- Send to individuals or groups
- Example: "Send a WhatsApp to +1234567890 saying Hello from my assistant"

## Installation

### Prerequisites
- Python 3.8 or higher
- Mac OS or iOS device
- Microphone access
- Internet connection

### Setup Steps

1. **Clone the repository**
   ```bash
   cd ai_personal_assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install PyAudio (Mac OS)**
   ```bash
   brew install portaudio
   pip install pyaudio
   ```

4. **Configure credentials**
   - Copy `config/config.template.json` to `config/config.json`
   - Update with your email credentials
   - For Gmail, use app-specific password
   - For Outlook, use account password or app password

5. **Set up Google Calendar (Optional)**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Google Calendar API
   - Download credentials.json
   - Place in the ai_personal_assistant directory

6. **Create logs directory**
   ```bash
   mkdir logs
   ```

## Usage

### Starting the Assistant

```bash
python assistant.py
```

### Voice Commands

#### PowerPoint Commands
- "Create a presentation called [title]"
- "Add a slide titled [title]"
- "Save the presentation"
- "Save presentation as [filename]"

#### Email Commands
- "Send an email to [address] subject [subject] message [body]"
- "Read my emails"
- "Check my inbox"
- "Search for emails about [topic]"

#### Calendar Commands
- "Schedule a meeting called [title] at [time] for [duration] hours"
- "What's on my calendar today"
- "Show my schedule"
- "Check my calendar"

#### WhatsApp Commands
- "Send a WhatsApp to [phone] saying [message]"
- "WhatsApp [contact] message [text]"

#### General Commands
- "Help" - List available commands
- "Stop" or "Exit" - Stop the assistant

## Configuration

Edit `config/config.json` to customize:

```json
{
  "language": "en-US",
  "speech_rate": 175,
  "speech_volume": 0.9,
  "email": {
    "address": "your-email@outlook.com",
    "password": "your-password"
  }
}
```

### Email Setup

#### Outlook/Office 365
- Use your Outlook email and password
- SMTP: smtp-mail.outlook.com:587
- IMAP: outlook.office365.com:993

#### Gmail
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password in config
4. SMTP: smtp.gmail.com:587
5. IMAP: imap.gmail.com:993

### WhatsApp Setup
- WhatsApp Web must be logged in
- Phone numbers must include country code
- Format: +1234567890

## Troubleshooting

### Microphone Issues
```bash
# Check microphone permissions in System Preferences > Security & Privacy
# Test microphone:
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### PyAudio Installation Error
```bash
# Mac OS
brew install portaudio
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
```

### Email Connection Error
- Check email and password are correct
- For Gmail, use app-specific password
- Ensure "Less secure app access" is enabled (if applicable)
- Check SMTP/IMAP server addresses

### Calendar Not Working
- Ensure credentials.json is in the correct location
- Run the assistant to trigger OAuth flow
- Check token.pickle file is created

### WhatsApp Not Sending
- Ensure WhatsApp Web is logged in on default browser
- Check Chrome is the default browser
- Verify phone number format includes country code

## Architecture

```
ai_personal_assistant/
├── assistant.py              # Main controller
├── modules/
│   ├── voice_recognition.py  # Speech-to-text
│   ├── text_to_speech.py     # Text-to-speech
│   ├── command_parser.py     # Command parsing
│   ├── powerpoint_handler.py # PowerPoint automation
│   ├── email_handler.py      # Email operations
│   ├── calendar_handler.py   # Calendar operations
│   └── whatsapp_handler.py   # WhatsApp messaging
├── config/
│   └── config.template.json  # Configuration template
├── logs/                     # Log files
└── requirements.txt          # Dependencies
```

## Security Best Practices

1. **Never commit credentials**
   - Keep config.json in .gitignore
   - Use environment variables for sensitive data

2. **Use app-specific passwords**
   - Enable 2FA on email accounts
   - Generate app-specific passwords

3. **Secure credential storage**
   - Use system keychain when possible
   - Encrypt sensitive configuration files

4. **Regular updates**
   - Keep dependencies updated
   - Check for security patches

## Limitations

- Requires active internet connection
- Voice recognition accuracy depends on microphone quality
- WhatsApp requires browser automation
- Email operations depend on email provider settings
- Calendar requires Google Calendar API setup

## Future Enhancements

- [ ] Support for multiple email accounts
- [ ] Integration with Slack
- [ ] Task management (Todoist, Trello)
- [ ] File management operations
- [ ] Smart home device control
- [ ] Meeting transcription
- [ ] Advanced NLP with GPT integration
- [ ] Custom voice commands
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- Add tests for new features
- Update documentation
- Test on Mac OS before submitting

## License

This project is part of the Smart Home and Smart Office System.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `logs/assistant.log`
3. Open an issue on GitHub

## Acknowledgments

- SpeechRecognition library
- pyttsx3 for text-to-speech
- python-pptx for PowerPoint automation
- pywhatkit for WhatsApp integration
- Google Calendar API
