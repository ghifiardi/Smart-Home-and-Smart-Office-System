"""
Modules package for AI Personal Assistant
Contains all handler and utility modules
"""

# Import with error handling for testing environments
try:
    from .voice_recognition import VoiceRecognizer
    from .text_to_speech import TextToSpeech
    from .command_parser import CommandParser
    from .powerpoint_handler import PowerPointHandler
    from .email_handler import EmailHandler
    from .calendar_handler import CalendarHandler
    from .whatsapp_handler import WhatsAppHandler
    
    __all__ = [
        'VoiceRecognizer',
        'TextToSpeech',
        'CommandParser',
        'PowerPointHandler',
        'EmailHandler',
        'CalendarHandler',
        'WhatsAppHandler'
    ]
except Exception as e:
    # Allow imports to fail gracefully in test environments
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}")
    __all__ = []
