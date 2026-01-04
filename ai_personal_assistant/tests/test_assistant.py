"""
Basic tests for AI Personal Assistant modules
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.command_parser import CommandParser
from modules.powerpoint_handler import PowerPointHandler
from datetime import datetime


class TestCommandParser(unittest.TestCase):
    """Test command parser functionality"""
    
    def setUp(self):
        self.parser = CommandParser()
    
    def test_create_presentation_command(self):
        """Test parsing create presentation command"""
        command = self.parser.parse_command("create a presentation called Test Presentation")
        self.assertEqual(command['type'], 'create_presentation')
        self.assertIn('test presentation', command['params'][0])
    
    def test_add_slide_command(self):
        """Test parsing add slide command"""
        command = self.parser.parse_command("add a slide titled Introduction")
        self.assertEqual(command['type'], 'add_slide')
        self.assertIn('introduction', command['params'][0])
    
    def test_send_email_command(self):
        """Test parsing send email command"""
        command = self.parser.parse_command(
            "send an email to john@test.com subject Meeting message Let's meet"
        )
        self.assertEqual(command['type'], 'send_email')
        self.assertEqual(len(command['params']), 3)
    
    def test_read_emails_command(self):
        """Test parsing read emails command"""
        command = self.parser.parse_command("read my emails")
        self.assertEqual(command['type'], 'read_emails')
    
    def test_check_calendar_command(self):
        """Test parsing check calendar command"""
        command = self.parser.parse_command("what's on my calendar today")
        self.assertEqual(command['type'], 'check_calendar')
    
    def test_whatsapp_command(self):
        """Test parsing WhatsApp command"""
        command = self.parser.parse_command(
            "send a whatsapp to John saying Hello"
        )
        self.assertEqual(command['type'], 'send_whatsapp')
    
    def test_help_command(self):
        """Test parsing help command"""
        command = self.parser.parse_command("help")
        self.assertEqual(command['type'], 'help')
    
    def test_stop_command(self):
        """Test parsing stop command"""
        command = self.parser.parse_command("stop")
        self.assertEqual(command['type'], 'stop')
    
    def test_unknown_command(self):
        """Test parsing unknown command"""
        command = self.parser.parse_command("do something random")
        self.assertEqual(command['type'], 'unknown')
    
    def test_parse_datetime(self):
        """Test datetime parsing"""
        # Test parsing "today at 2 pm"
        dt = self.parser.parse_datetime("today at 2 pm")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.hour, 14)
        
        # Test parsing "tomorrow at 3:30 pm"
        dt = self.parser.parse_datetime("tomorrow at 3:30 pm")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.hour, 15)
        self.assertEqual(dt.minute, 30)


class TestPowerPointHandler(unittest.TestCase):
    """Test PowerPoint handler functionality"""
    
    def setUp(self):
        self.handler = PowerPointHandler()
    
    def test_create_presentation(self):
        """Test creating a presentation"""
        result = self.handler.create_presentation("Test Presentation")
        self.assertTrue(result)
        self.assertIsNotNone(self.handler.current_presentation)
    
    def test_add_slide(self):
        """Test adding a slide"""
        self.handler.create_presentation("Test")
        result = self.handler.add_slide("Test Slide", ["Point 1", "Point 2"])
        self.assertTrue(result)
        self.assertEqual(self.handler.get_slide_count(), 2)  # Title slide + new slide
    
    def test_get_slide_count(self):
        """Test getting slide count"""
        self.handler.create_presentation("Test")
        count = self.handler.get_slide_count()
        self.assertEqual(count, 1)  # Should have title slide
    
    def test_close_presentation(self):
        """Test closing presentation"""
        self.handler.create_presentation("Test")
        self.handler.close_presentation()
        self.assertIsNone(self.handler.current_presentation)


class TestModuleImports(unittest.TestCase):
    """Test that all modules can be imported"""
    
    def test_import_voice_recognition(self):
        """Test importing voice recognition module"""
        try:
            from modules.voice_recognition import VoiceRecognizer
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import VoiceRecognizer")
    
    def test_import_text_to_speech(self):
        """Test importing text-to-speech module"""
        try:
            from modules.text_to_speech import TextToSpeech
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import TextToSpeech")
    
    def test_import_email_handler(self):
        """Test importing email handler module"""
        try:
            from modules.email_handler import EmailHandler
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import EmailHandler")
    
    def test_import_calendar_handler(self):
        """Test importing calendar handler module"""
        try:
            from modules.calendar_handler import CalendarHandler
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import CalendarHandler")
    
    def test_import_whatsapp_handler(self):
        """Test importing WhatsApp handler module"""
        try:
            from modules.whatsapp_handler import WhatsAppHandler
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import WhatsAppHandler")


if __name__ == '__main__':
    unittest.main()
