"""
Voice Recognition Module
Handles speech-to-text conversion for voice commands
"""

import speech_recognition as sr
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """Voice recognition system for capturing and processing voice commands"""
    
    def __init__(self, language: str = "en-US"):
        """
        Initialize voice recognizer
        
        Args:
            language: Language code for speech recognition (default: en-US)
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.microphone = None
        
        # Configure recognizer settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def listen_for_command(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for voice command from microphone
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time for phrase duration
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening for command...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("Processing audio...")
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during voice recognition: {e}")
            return None
    
    def listen_for_wake_word(self, wake_word: str = "assistant") -> bool:
        """
        Listen for wake word to activate assistant
        
        Args:
            wake_word: The wake word to listen for
            
        Returns:
            True if wake word detected, False otherwise
        """
        command = self.listen_for_command(timeout=10)
        if command and wake_word.lower() in command:
            logger.info("Wake word detected!")
            return True
        return False
