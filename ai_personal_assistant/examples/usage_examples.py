"""
Example usage script for AI Personal Assistant
Demonstrates how to use the assistant programmatically
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.powerpoint_handler import PowerPointHandler
from modules.email_handler import EmailHandler
from modules.calendar_handler import CalendarHandler
from modules.whatsapp_handler import WhatsAppHandler
from datetime import datetime, timedelta


def example_powerpoint():
    """Example: Create a PowerPoint presentation"""
    print("\n=== PowerPoint Example ===")
    
    ppt = PowerPointHandler()
    
    # Create presentation
    ppt.create_presentation("Quarterly Business Review")
    
    # Add slides
    ppt.add_slide("Executive Summary", [
        "Revenue increased 25% YoY",
        "Customer satisfaction at all-time high",
        "Expanded to 3 new markets"
    ])
    
    ppt.add_slide("Financial Performance", [
        "Q4 Revenue: $5.2M",
        "Profit Margin: 18%",
        "Operating Expenses reduced by 12%"
    ])
    
    ppt.add_slide("Next Quarter Goals", [
        "Launch new product line",
        "Increase market share by 15%",
        "Expand team by 20 employees"
    ])
    
    # Save presentation
    ppt.save_presentation("quarterly_review.pptx")
    
    print(f"Created presentation with {ppt.get_slide_count()} slides")
    print("Saved as: quarterly_review.pptx")


def example_email():
    """Example: Send an email (requires credentials)"""
    print("\n=== Email Example ===")
    
    # Note: Replace with your actual credentials
    email_address = "your-email@outlook.com"
    password = "your-password"
    
    if email_address == "your-email@outlook.com":
        print("Please configure email credentials in the script")
        return
    
    email_handler = EmailHandler(email_address, password)
    
    # Send email
    success = email_handler.send_email(
        to_addresses=["recipient@example.com"],
        subject="Test Email from AI Assistant",
        body="This is a test email sent by the AI Personal Assistant."
    )
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email")
    
    # Read recent emails
    emails = email_handler.read_recent_emails(count=3)
    print(f"\nFound {len(emails)} recent emails:")
    for email in emails:
        print(f"  - {email['subject']} from {email['from']}")


def example_calendar():
    """Example: Create calendar event"""
    print("\n=== Calendar Example ===")
    
    calendar = CalendarHandler()
    
    # Schedule a meeting
    start_time = datetime.now() + timedelta(days=1)
    start_time = start_time.replace(hour=14, minute=0, second=0)
    end_time = start_time + timedelta(hours=1)
    
    event_id = calendar.create_event(
        summary="Team Standup Meeting",
        start_time=start_time,
        end_time=end_time,
        description="Daily team standup to discuss progress",
        location="Conference Room A"
    )
    
    if event_id:
        print(f"Meeting scheduled for {start_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Get today's events
    events = calendar.get_today_events()
    print(f"\nEvents today: {len(events)}")
    for event in events:
        print(f"  - {event['summary']} at {event['start']}")


def example_whatsapp():
    """Example: Send WhatsApp message"""
    print("\n=== WhatsApp Example ===")
    
    whatsapp = WhatsAppHandler()
    
    # Note: Replace with actual phone number
    phone_number = "+1234567890"
    
    if phone_number == "+1234567890":
        print("Please configure a phone number in the script")
        return
    
    # Send message
    message = "Hello from AI Personal Assistant! This is a test message."
    
    print(f"Preparing to send WhatsApp message to {phone_number}")
    print("Note: This will open WhatsApp Web in your browser")
    
    # Uncomment to actually send
    # success = whatsapp.send_message(phone_number, message)
    # if success:
    #     print("Message sent successfully!")


def main():
    """Run all examples"""
    print("AI Personal Assistant - Example Usage\n")
    print("=" * 50)
    
    # Run examples
    example_powerpoint()
    
    # Uncomment to run other examples (requires credentials)
    # example_email()
    # example_calendar()
    # example_whatsapp()
    
    print("\n" + "=" * 50)
    print("\nExamples completed!")
    print("\nNote: Some examples require configuration:")
    print("  - Email: Set email_address and password")
    print("  - Calendar: Set up credentials.json")
    print("  - WhatsApp: Set phone_number and ensure WhatsApp Web is logged in")


if __name__ == "__main__":
    main()
