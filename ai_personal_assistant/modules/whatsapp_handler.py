"""
WhatsApp Handler Module
Handles WhatsApp messaging operations
"""

import logging
import re
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import pywhatkit as kit
    PYWHATKIT_AVAILABLE = True
except Exception as e:
    logger.warning(f"pywhatkit not available: {e}")
    PYWHATKIT_AVAILABLE = False


class WhatsAppHandler:
    """Handler for WhatsApp messaging operations"""
    
    def __init__(self):
        """Initialize WhatsApp handler"""
        if not PYWHATKIT_AVAILABLE:
            logger.warning("WhatsApp handler initialized but pywhatkit is not available")
        else:
            logger.info("WhatsApp handler initialized")
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for international format with country code
        pattern = r'^\+\d{1,3}\d{7,14}$'
        if re.match(pattern, phone_number):
            return True
        
        logger.warning(f"Invalid phone number format: {phone_number}. Expected format: +1234567890")
        return False
    
    def send_message(self, phone_number: str, message: str, 
                    schedule_time: Optional[datetime] = None) -> bool:
        """
        Send a WhatsApp message
        
        Args:
            phone_number: Recipient phone number with country code (e.g., +1234567890)
            message: Message text to send
            schedule_time: Optional datetime to schedule the message
            
        Returns:
            True if successful, False otherwise
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("pywhatkit is not available")
            return False
        
        if not self._validate_phone_number(phone_number):
            return False
            
        try:
            if schedule_time:
                # Schedule message for specific time
                hour = schedule_time.hour
                minute = schedule_time.minute
                
                kit.sendwhatmsg(phone_number, message, hour, minute)
                logger.info(f"Message scheduled to {phone_number} at {hour}:{minute}")
            else:
                # Send message immediately (with small delay for WhatsApp Web to open)
                now = datetime.now()
                send_time = now + timedelta(minutes=1)
                
                kit.sendwhatmsg(
                    phone_number, 
                    message, 
                    send_time.hour, 
                    send_time.minute,
                    wait_time=15,
                    tab_close=True
                )
                logger.info(f"Message sent to {phone_number}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_message_instantly(self, phone_number: str, message: str) -> bool:
        """
        Send a WhatsApp message instantly (opens WhatsApp Web immediately)
        
        Args:
            phone_number: Recipient phone number with country code
            message: Message text to send
            
        Returns:
            True if successful, False otherwise
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("pywhatkit is not available")
            return False
            
        try:
            kit.sendwhatmsg_instantly(
                phone_number, 
                message,
                wait_time=10,
                tab_close=True
            )
            logger.info(f"Instant message sent to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending instant WhatsApp message: {e}")
            return False
    
    def send_to_group(self, group_id: str, message: str,
                     schedule_time: Optional[datetime] = None) -> bool:
        """
        Send a message to a WhatsApp group
        
        Args:
            group_id: WhatsApp group ID
            message: Message text to send
            schedule_time: Optional datetime to schedule the message
            
        Returns:
            True if successful, False otherwise
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("pywhatkit is not available")
            return False
            
        try:
            if schedule_time:
                hour = schedule_time.hour
                minute = schedule_time.minute
                
                kit.sendwhatmsg_to_group(group_id, message, hour, minute)
                logger.info(f"Group message scheduled at {hour}:{minute}")
            else:
                now = datetime.now()
                send_time = now + timedelta(minutes=1)
                
                kit.sendwhatmsg_to_group(
                    group_id,
                    message,
                    send_time.hour,
                    send_time.minute,
                    wait_time=15,
                    tab_close=True
                )
                logger.info(f"Message sent to group {group_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending group message: {e}")
            return False
    
    def send_image(self, phone_number: str, image_path: str, 
                  caption: str = "") -> bool:
        """
        Send an image via WhatsApp
        
        Args:
            phone_number: Recipient phone number with country code
            image_path: Path to image file
            caption: Optional caption for the image
            
        Returns:
            True if successful, False otherwise
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("pywhatkit is not available")
            return False
            
        try:
            kit.sendwhats_image(
                phone_number,
                image_path,
                caption,
                wait_time=15,
                tab_close=True
            )
            logger.info(f"Image sent to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending image: {e}")
            return False
