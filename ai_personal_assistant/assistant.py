"""
AI Personal Assistant - Main Controller
Coordinates all modules and handles command execution
"""

import logging
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

from modules.voice_recognition import VoiceRecognizer
from modules.text_to_speech import TextToSpeech
from modules.command_parser import CommandParser
from modules.powerpoint_handler import PowerPointHandler
from modules.email_handler import EmailHandler
from modules.calendar_handler import CalendarHandler
from modules.whatsapp_handler import WhatsAppHandler

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class PersonalAssistant:
    """Main AI Personal Assistant controller"""
    
    def __init__(self, config: dict):
        """
        Initialize the personal assistant
        
        Args:
            config: Configuration dictionary with user settings
        """
        logger.info("Initializing AI Personal Assistant...")
        
        # Initialize configuration
        self.config = config
        self.running = False
        
        # Initialize modules
        try:
            self.voice_recognizer = VoiceRecognizer(
                language=config.get('language', 'en-US')
            )
            self.tts = TextToSpeech(
                rate=config.get('speech_rate', 175),
                volume=config.get('speech_volume', 0.9)
            )
            self.command_parser = CommandParser()
            self.powerpoint_handler = PowerPointHandler()
            
            # Initialize email handler if credentials provided
            email_config = config.get('email', {})
            if email_config.get('address') and email_config.get('password'):
                self.email_handler = EmailHandler(
                    email_address=email_config['address'],
                    password=email_config['password'],
                    smtp_server=email_config.get('smtp_server', 'smtp-mail.outlook.com'),
                    smtp_port=email_config.get('smtp_port', 587),
                    imap_server=email_config.get('imap_server', 'outlook.office365.com'),
                    imap_port=email_config.get('imap_port', 993)
                )
            else:
                self.email_handler = None
                logger.warning("Email handler not initialized - credentials missing")
            
            # Initialize calendar handler
            calendar_config = config.get('calendar', {})
            self.calendar_handler = CalendarHandler(
                credentials_file=calendar_config.get('credentials_file', 'credentials.json'),
                timezone=calendar_config.get('timezone', 'America/Los_Angeles')
            )
            
            # Initialize WhatsApp handler
            self.whatsapp_handler = WhatsAppHandler()
            
            logger.info("All modules initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing modules: {e}")
            raise
    
    def greet_user(self):
        """Greet the user"""
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        message = f"{greeting}! I'm your AI personal assistant. How can I help you today?"
        self.tts.speak(message)
    
    def execute_command(self, command: dict) -> bool:
        """
        Execute a parsed command
        
        Args:
            command: Parsed command dictionary
            
        Returns:
            True if command executed successfully, False otherwise
        """
        command_type = command['type']
        params = command['params']
        
        try:
            if command_type == 'create_presentation':
                return self._handle_create_presentation(params)
            
            elif command_type == 'add_slide':
                return self._handle_add_slide(params)
            
            elif command_type == 'save_presentation':
                return self._handle_save_presentation(params)
            
            elif command_type == 'send_email':
                return self._handle_send_email(params)
            
            elif command_type == 'read_emails':
                return self._handle_read_emails()
            
            elif command_type == 'search_email':
                return self._handle_search_email(params)
            
            elif command_type == 'schedule_meeting':
                return self._handle_schedule_meeting(params)
            
            elif command_type == 'check_calendar':
                return self._handle_check_calendar()
            
            elif command_type == 'send_whatsapp':
                return self._handle_send_whatsapp(params)
            
            elif command_type == 'help':
                return self._handle_help()
            
            elif command_type == 'stop':
                self.tts.speak("Goodbye! Have a great day!")
                return False
            
            else:
                self.tts.speak("I'm sorry, I didn't understand that command. Say 'help' for available commands.")
                return True
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self.tts.speak("I encountered an error while executing that command.")
            return True
    
    def _handle_create_presentation(self, params) -> bool:
        """Handle create presentation command"""
        title = params[0] if params else "New Presentation"
        
        if self.powerpoint_handler.create_presentation(title):
            self.tts.speak(f"Created a new presentation titled {title}")
            return True
        else:
            self.tts.speak("Failed to create presentation")
            return True
    
    def _handle_add_slide(self, params) -> bool:
        """Handle add slide command"""
        title = params[0] if params else "New Slide"
        
        if self.powerpoint_handler.add_slide(title, []):
            self.tts.speak(f"Added a new slide titled {title}")
            return True
        else:
            self.tts.speak("Failed to add slide. Make sure you have a presentation open.")
            return True
    
    def _handle_save_presentation(self, params) -> bool:
        """Handle save presentation command"""
        filename = params[0] if params and params[0] else None
        
        if self.powerpoint_handler.save_presentation(filename):
            self.tts.speak("Presentation saved successfully")
            return True
        else:
            self.tts.speak("Failed to save presentation")
            return True
    
    def _handle_send_email(self, params) -> bool:
        """Handle send email command"""
        if not self.email_handler:
            self.tts.speak("Email functionality is not configured")
            return True
        
        if len(params) >= 3:
            to_address = params[0]
            subject = params[1]
            body = params[2]
            
            if self.email_handler.send_email([to_address], subject, body):
                self.tts.speak(f"Email sent to {to_address}")
                return True
        
        self.tts.speak("Failed to send email. Please check the command format.")
        return True
    
    def _handle_read_emails(self) -> bool:
        """Handle read emails command"""
        if not self.email_handler:
            self.tts.speak("Email functionality is not configured")
            return True
        
        emails = self.email_handler.read_recent_emails(count=3)
        
        if emails:
            self.tts.speak(f"You have {len(emails)} recent emails")
            for i, email in enumerate(emails, 1):
                self.tts.speak(f"Email {i}: From {email['from']}, Subject: {email['subject']}")
        else:
            self.tts.speak("No recent emails found")
        
        return True
    
    def _handle_search_email(self, params) -> bool:
        """Handle search email command"""
        if not self.email_handler:
            self.tts.speak("Email functionality is not configured")
            return True
        
        search_term = params[0] if params else ""
        
        if search_term:
            emails = self.email_handler.search_emails(search_term)
            if emails:
                self.tts.speak(f"Found {len(emails)} emails matching {search_term}")
            else:
                self.tts.speak(f"No emails found matching {search_term}")
        
        return True
    
    def _handle_schedule_meeting(self, params) -> bool:
        """Handle schedule meeting command"""
        if len(params) >= 3:
            title = params[0]
            time_str = params[1]
            duration = int(params[2])
            
            start_time = self.command_parser.parse_datetime(time_str)
            if start_time:
                end_time = start_time + timedelta(hours=duration)
                
                event_id = self.calendar_handler.create_event(
                    title, start_time, end_time
                )
                
                if event_id:
                    self.tts.speak(f"Scheduled {title} for {start_time.strftime('%I:%M %p')}")
                    return True
        
        self.tts.speak("Failed to schedule meeting")
        return True
    
    def _handle_check_calendar(self) -> bool:
        """Handle check calendar command"""
        events = self.calendar_handler.get_today_events()
        
        if events:
            self.tts.speak(f"You have {len(events)} events today")
            for event in events[:3]:  # Read first 3 events
                self.tts.speak(f"{event['summary']} at {event['start']}")
        else:
            self.tts.speak("You have no events scheduled for today")
        
        return True
    
    def _handle_send_whatsapp(self, params) -> bool:
        """Handle send WhatsApp command"""
        if len(params) >= 2:
            recipient = params[0]
            message = params[1]
            
            # Extract phone number
            phone = self.command_parser.extract_phone_number(recipient)
            
            if phone:
                if self.whatsapp_handler.send_message(phone, message):
                    self.tts.speak(f"WhatsApp message sent to {recipient}")
                    return True
        
        self.tts.speak("Failed to send WhatsApp message")
        return True
    
    def _handle_help(self) -> bool:
        """Handle help command"""
        help_text = """
        Here are the available commands:
        
        PowerPoint: Create presentation, add slide, save presentation
        Email: Send email, read emails, search emails
        Calendar: Schedule meeting, check calendar
        WhatsApp: Send WhatsApp message
        
        Say 'stop' to exit the assistant.
        """
        self.tts.speak(help_text)
        return True
    
    def run(self):
        """Main run loop for the assistant"""
        self.running = True
        self.greet_user()
        
        while self.running:
            try:
                # Listen for wake word
                self.tts.speak("I'm listening")
                command_text = self.voice_recognizer.listen_for_command()
                
                if command_text:
                    logger.info(f"Command received: {command_text}")
                    
                    # Parse command
                    command = self.command_parser.parse_command(command_text)
                    
                    # Execute command
                    continue_running = self.execute_command(command)
                    
                    if not continue_running:
                        self.running = False
                        break
                
            except KeyboardInterrupt:
                self.tts.speak("Stopping assistant")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.tts.speak("An error occurred. Continuing to listen.")
        
        logger.info("Assistant stopped")


def main():
    """Main entry point"""
    # Example configuration
    config = {
        'language': 'en-US',
        'speech_rate': 175,
        'speech_volume': 0.9,
        'email': {
            'address': '',  # Set your email
            'password': '',  # Set your password
        },
        'calendar': {
            'credentials_file': 'credentials.json',
            'timezone': 'America/Los_Angeles'
        }
    }
    
    try:
        assistant = PersonalAssistant(config)
        assistant.run()
    except Exception as e:
        logger.error(f"Failed to start assistant: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
