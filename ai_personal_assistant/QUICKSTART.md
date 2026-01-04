# Quick Start Guide - AI Personal Assistant

## Get Started in 5 Minutes

### 1. Install Dependencies
```bash
cd ai_personal_assistant
pip install -r requirements.txt
```

For Mac users, install PyAudio:
```bash
brew install portaudio
pip install pyaudio
```

### 2. Basic Configuration

Create a simple config file:
```bash
cp config/config.template.json config/config.json
```

Edit `config/config.json` with your email:
```json
{
  "language": "en-US",
  "email": {
    "address": "your-email@outlook.com",
    "password": "your-password"
  }
}
```

### 3. Test Without Voice

Run the example script to test functionality without voice:
```bash
python examples/usage_examples.py
```

This will create a sample PowerPoint presentation to verify the setup.

### 4. Run the Assistant

```bash
python assistant.py
```

### 5. Try Your First Command

When the assistant says "I'm listening":
- "Create a presentation called My First Presentation"
- "Add a slide titled Introduction"
- "Save the presentation"

## Common Voice Commands

### PowerPoint
- "Create presentation called Project Update"
- "Add slide titled Overview"
- "Save presentation"

### Email (requires email config)
- "Read my emails"
- "Send email to john@example.com subject Hello message How are you"

### Calendar (requires Google Calendar setup)
- "Check my calendar"
- "Schedule meeting called Team Sync at 2 PM for 1 hour"

### WhatsApp (requires WhatsApp Web logged in)
- "Send WhatsApp to +1234567890 saying Hello"

## Troubleshooting

### "No module named speech_recognition"
```bash
pip install SpeechRecognition
```

### Microphone not working
Check System Preferences > Security & Privacy > Microphone
Grant permission to Terminal or your Python IDE

### PyAudio won't install
```bash
brew install portaudio
pip install pyaudio
```

### Email not sending
- Verify email and password in config.json
- For Gmail, use app-specific password
- For Outlook, may need to enable "Less secure apps"

## Next Steps

1. **Set up Google Calendar**
   - Get credentials.json from Google Cloud Console
   - Enable Calendar API
   - Place file in ai_personal_assistant directory

2. **Configure WhatsApp**
   - Log into WhatsApp Web in your default browser
   - Keep browser open when sending messages

3. **Customize Voice**
   - Run `examples/usage_examples.py`
   - Check available voices
   - Update speech_rate and volume in config

4. **Add More Commands**
   - Edit `modules/command_parser.py`
   - Add new patterns
   - Implement handlers in `assistant.py`

## Tips

- Speak clearly and not too fast
- Wait for "I'm listening" before speaking
- Say "help" to hear available commands
- Say "stop" to exit
- Check `logs/assistant.log` for debugging

## Security

⚠️ Never commit config.json with your credentials!

The .gitignore file is configured to exclude:
- config/config.json
- credentials.json
- token.pickle
- *.log files

## Need Help?

- Check README.md for detailed documentation
- Review logs/assistant.log for errors
- Ensure microphone permissions are granted
- Test internet connection

Happy automating! 🚀
