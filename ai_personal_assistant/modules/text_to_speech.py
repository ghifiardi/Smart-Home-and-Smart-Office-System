"""
Text-to-Speech Module
Handles voice feedback and responses
"""

import pyttsx3
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech system for voice responses"""
    
    def __init__(self, rate: int = 175, volume: float = 0.9, voice_index: int = 0):
        """
        Initialize text-to-speech engine
        
        Args:
            rate: Speaking rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_index: Index of voice to use
        """
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > voice_index:
                self.engine.setProperty('voice', voices[voice_index].id)
                
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return False
            
        try:
            logger.info(f"Speaking: {text}")
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            
            return True
        except Exception as e:
            logger.error(f"Error during text-to-speech: {e}")
            return False
    
    def stop(self):
        """Stop current speech"""
        try:
            if self.engine:
                self.engine.stop()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices
        
        Returns:
            List of available voice names
        """
        if not self.engine:
            return []
            
        try:
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_index: int):
        """
        Set voice by index
        
        Args:
            voice_index: Index of voice to use
        """
        if not self.engine:
            return
            
        try:
            voices = self.engine.getProperty('voices')
            if voices and 0 <= voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                logger.info(f"Voice changed to: {voices[voice_index].name}")
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
