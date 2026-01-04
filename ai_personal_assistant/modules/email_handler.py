"""
Email Handler Module
Handles email operations for Outlook and other email clients
"""

import logging
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailHandler:
    """Handler for email operations compatible with Mac and iPhone"""
    
    def __init__(self, email_address: str, password: str, 
                 smtp_server: str = "smtp-mail.outlook.com",
                 smtp_port: int = 587,
                 imap_server: str = "outlook.office365.com",
                 imap_port: int = 993):
        """
        Initialize email handler
        
        Args:
            email_address: Email address
            password: Email password or app-specific password
            smtp_server: SMTP server address
            smtp_port: SMTP port
            imap_server: IMAP server address
            imap_port: IMAP port
        """
        self.email_address = email_address
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        
    def send_email(self, to_addresses: List[str], subject: str, 
                   body: str, cc_addresses: Optional[List[str]] = None) -> bool:
        """
        Send an email
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body
            cc_addresses: List of CC email addresses (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            if cc_addresses:
                msg['Cc'] = ', '.join(cc_addresses)
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.password)
                
                # Send email
                all_recipients = to_addresses + (cc_addresses or [])
                server.send_message(msg)
                
            logger.info(f"Email sent to {', '.join(to_addresses)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def read_recent_emails(self, folder: str = "INBOX", 
                          count: int = 5) -> List[Dict[str, str]]:
        """
        Read recent emails from inbox
        
        Args:
            folder: Email folder to read from
            count: Number of emails to retrieve
            
        Returns:
            List of email dictionaries with subject, from, date, and body
        """
        emails = []
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select(folder)
            
            # Search for all emails
            status, messages = mail.search(None, 'ALL')
            
            if status == 'OK':
                email_ids = messages[0].split()
                # Get most recent emails
                recent_ids = email_ids[-count:] if len(email_ids) >= count else email_ids
                
                for email_id in reversed(recent_ids):
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Extract email details
                        subject = email_message['Subject']
                        from_addr = email_message['From']
                        date = email_message['Date']
                        
                        # Get email body
                        body = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = email_message.get_payload(decode=True).decode()
                        
                        emails.append({
                            'subject': subject,
                            'from': from_addr,
                            'date': date,
                            'body': body[:200]  # First 200 characters
                        })
            
            mail.close()
            mail.logout()
            
            logger.info(f"Retrieved {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return []
    
    def search_emails(self, search_term: str, folder: str = "INBOX") -> List[Dict[str, str]]:
        """
        Search for emails containing specific term
        
        Args:
            search_term: Term to search for in subject or body
            folder: Email folder to search in
            
        Returns:
            List of matching emails
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select(folder)
            
            # Search for emails with term in subject
            status, messages = mail.search(None, f'(SUBJECT "{search_term}")')
            
            emails = []
            if status == 'OK':
                email_ids = messages[0].split()
                
                for email_id in email_ids[-10:]:  # Last 10 matches
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        emails.append({
                            'subject': email_message['Subject'],
                            'from': email_message['From'],
                            'date': email_message['Date']
                        })
            
            mail.close()
            mail.logout()
            
            logger.info(f"Found {len(emails)} emails matching '{search_term}'")
            return emails
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
