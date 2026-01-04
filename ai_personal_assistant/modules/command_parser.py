"""
Command Parser Module
Parses and interprets voice commands for the assistant
"""

import logging
import re
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CommandParser:
    """Parser for voice commands"""
    
    def __init__(self):
        """Initialize command parser"""
        self.command_patterns = {
            # PowerPoint commands
            'create_presentation': [
                r'create (?:a )?presentation (?:called |named |titled )?(.+)',
                r'make (?:a )?(?:new )?presentation (?:called |named |titled )?(.+)',
                r'new presentation (?:called |named |titled )?(.+)'
            ],
            'add_slide': [
                r'add (?:a )?slide (?:called |titled )?(.+)',
                r'new slide (?:called |titled )?(.+)',
                r'create (?:a )?slide (?:called |titled )?(.+)'
            ],
            'save_presentation': [
                r'save (?:the )?presentation(?: as (.+))?',
                r'save (?:this|it)(?: as (.+))?'
            ],
            
            # Email commands
            'send_email': [
                r'send (?:an )?email to (.+?) (?:with )?subject (.+?) (?:saying |message |body )?(.+)',
                r'email (.+?) about (.+?) (?:saying |message )?(.+)',
                r'compose email to (.+?) subject (.+?) message (.+)'
            ],
            'read_emails': [
                r'read (?:my )?(?:recent )?emails',
                r'check (?:my )?(?:inbox|email)',
                r'what (?:are )?(?:my )?new emails'
            ],
            'search_email': [
                r'search (?:for )?emails? (?:about |containing |with )?(.+)',
                r'find emails? (?:about |containing |with )?(.+)'
            ],
            
            # Calendar commands
            'schedule_meeting': [
                r'schedule (?:a )?meeting (?:called |titled )?(.+?) (?:at|on) (.+?) (?:for|lasting) (\d+) (?:minutes|hours?)',
                r'create (?:a )?(?:calendar )?event (?:called |titled )?(.+?) (?:at|on) (.+?) (?:for|lasting) (\d+) (?:minutes|hours?)',
                r'book (?:a )?meeting (?:called |titled )?(.+?) (?:at|on) (.+?) (?:for|lasting) (\d+) (?:minutes|hours?)'
            ],
            'check_calendar': [
                r'what(?:\'s| is) (?:on )?(?:my )?(?:calendar|schedule)(?: today| tomorrow)?',
                r'show (?:me )?(?:my )?(?:calendar|schedule)(?: today| tomorrow)?',
                r'list (?:my )?(?:events|meetings)(?: today| tomorrow)?'
            ],
            
            # WhatsApp commands
            'send_whatsapp': [
                r'send (?:a )?whatsapp (?:message )?to (.+?) (?:saying |message )?(.+)',
                r'whatsapp (.+?) (?:saying |message )?(.+)',
                r'message (.+?) on whatsapp (?:saying )?(.+)'
            ],
            
            # General commands
            'help': [
                r'help',
                r'what can you do',
                r'show (?:me )?commands'
            ],
            'stop': [
                r'stop',
                r'exit',
                r'quit',
                r'goodbye',
                r'bye'
            ]
        }
    
    def parse_command(self, command_text: str) -> Dict[str, any]:
        """
        Parse voice command text into structured command
        
        Args:
            command_text: Raw command text from voice recognition
            
        Returns:
            Dictionary with command type and parameters
        """
        command_text = command_text.lower().strip()
        
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, command_text, re.IGNORECASE)
                if match:
                    return {
                        'type': command_type,
                        'params': match.groups(),
                        'raw': command_text
                    }
        
        # No pattern matched
        return {
            'type': 'unknown',
            'params': (),
            'raw': command_text
        }
    
    def parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse datetime string into datetime object
        
        Args:
            datetime_str: Natural language datetime string
            
        Returns:
            datetime object or None if parsing failed
        """
        datetime_str = datetime_str.lower().strip()
        now = datetime.now()
        
        try:
            # Handle relative dates
            if 'today' in datetime_str:
                base_date = now
            elif 'tomorrow' in datetime_str:
                base_date = now + timedelta(days=1)
            elif 'next week' in datetime_str:
                base_date = now + timedelta(weeks=1)
            else:
                base_date = now
            
            # Extract time
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', datetime_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                
                # Handle AM/PM
                if time_match.group(3):
                    if time_match.group(3) == 'pm' and hour < 12:
                        hour += 12
                    elif time_match.group(3) == 'am' and hour == 12:
                        hour = 0
                
                return base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return base_date
            
        except Exception as e:
            logger.error(f"Error parsing datetime: {e}")
            return None
    
    def extract_phone_number(self, text: str) -> Optional[str]:
        """
        Extract phone number from text
        
        Args:
            text: Text containing phone number
            
        Returns:
            Phone number string or None
        """
        # Look for phone number patterns
        patterns = [
            r'\+\d{1,3}\d{10}',  # International format
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',  # US format
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'  # (123) 456-7890
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
