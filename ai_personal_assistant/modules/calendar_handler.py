"""
Calendar Handler Module
Handles calendar operations for scheduling and event management
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarHandler:
    """Handler for calendar operations using Google Calendar API"""
    
    def __init__(self, credentials_file: str = "credentials.json", timezone: str = "America/Los_Angeles"):
        """
        Initialize calendar handler
        
        Args:
            credentials_file: Path to Google Calendar API credentials file
            timezone: Timezone for events (default: America/Los_Angeles)
        """
        self.credentials_file = credentials_file
        self.timezone = timezone
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_file = 'token.pickle'
        
        try:
            # Load existing credentials
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.warning("Credentials file not found - calendar features disabled")
                    return
                
                # Save credentials for next time
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Calendar service authenticated successfully")
            
        except Exception as e:
            logger.error(f"Error authenticating with calendar: {e}")
    
    def create_event(self, summary: str, start_time: datetime, 
                    end_time: datetime, description: str = "",
                    location: str = "") -> Optional[str]:
        """
        Create a calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Calendar service not authenticated")
            return None
        
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': self.timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Event created: {summary} (ID: {event.get('id')})")
            return event.get('id')
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming calendar events
        
        Args:
            max_results: Maximum number of events to retrieve
            
        Returns:
            List of event dictionaries
        """
        if not self.service:
            logger.error("Calendar service not authenticated")
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            logger.info(f"Retrieved {len(formatted_events)} upcoming events")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def get_today_events(self) -> List[Dict]:
        """
        Get today's calendar events
        
        Returns:
            List of today's events
        """
        if not self.service:
            logger.error("Calendar service not authenticated")
            return []
        
        try:
            # Get start and end of today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=today_start.isoformat() + 'Z',
                timeMax=today_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            logger.info(f"Retrieved {len(formatted_events)} events for today")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return []
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Calendar service not authenticated")
            return False
        
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"Event deleted: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False
