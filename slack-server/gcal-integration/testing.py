import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Dict
import pytz

# Scopes - what permissions we need
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate():
    """Authenticate and return calendar service"""
    creds = None
    
    # token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../../email-server/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def get_freebusy(service, emails: List[str], days_ahead: int = 14):
    """Get free/busy info for a list of email addresses"""
    
    time_min = datetime.utcnow().isoformat() + 'Z'
    time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
    
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": email} for email in emails]
    }
    
    print(f"\n🔍 Checking availability for: {', '.join(emails)}")
    print(f"📅 From: {time_min}")
    print(f"📅 To: {time_max}\n")
    
    freebusy_result = service.freebusy().query(body=body).execute()
    
    return freebusy_result

def print_busy_times(freebusy_result):
    """Print busy times for each person"""
    
    calendars = freebusy_result.get('calendars', {})
    
    for email, cal_data in calendars.items():
        print(f"\n👤 {email}")
        print("=" * 50)
        
        busy_times = cal_data.get('busy', [])
        
        if not busy_times:
            print("  ✅ No busy times found!")
        else:
            print(f"  🔴 {len(busy_times)} busy periods:")
            for busy in busy_times:
                start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                print(f"    • {start.strftime('%a %b %d, %I:%M %p')} - {end.strftime('%I:%M %p')}")

def find_common_free_slots(freebusy_result, duration_minutes: int = 60, max_slots: int = 5):
    """Find time slots when ALL people are free"""
    
    print(f"\n\n🎯 Finding {duration_minutes}-minute slots when everyone is free...")
    print("=" * 50)
    
    calendars = freebusy_result.get('calendars', {})
    
    # Start from tomorrow at 9 AM
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end_search = start_time + timedelta(days=14)
    
    free_slots = []
    current = start_time
    
    while current < end_search and len(free_slots) < max_slots:
        # Skip weekends
        if current.weekday() >= 5:
            current += timedelta(days=1)
            current = current.replace(hour=9, minute=0)
            continue
        
        # Only check business hours (9 AM - 5 PM)
        if current.hour < 9:
            current = current.replace(hour=9, minute=0)
        elif current.hour >= 17:
            current += timedelta(days=1)
            current = current.replace(hour=9, minute=0)
            continue
        
        slot_end = current + timedelta(minutes=duration_minutes)
        
        # Check if this slot is free for ALL people
        if is_slot_free_for_all(calendars, current, slot_end):
            free_slots.append({
                'start': current,
                'end': slot_end,
                'display': current.strftime('%A, %B %d at %I:%M %p')
            })
        
        # Move to next 30-minute interval
        current += timedelta(minutes=30)
    
    return free_slots

def is_slot_free_for_all(calendars: Dict, slot_start: datetime, slot_end: datetime) -> bool:
    """Check if a time slot is free for all people"""
    
    local_tz = pytz.timezone("America/Vancouver")

    for email, cal_data in calendars.items():
        busy_times = cal_data.get('busy', [])
        
        for busy in busy_times:

            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            busy_start = busy_start.astimezone(local_tz) 

            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            busy_end = busy_end.astimezone(local_tz) 
            
            # Make timezone-naive for comparison
            busy_start = busy_start.replace(tzinfo=None)
            busy_end = busy_end.replace(tzinfo=None)
            
            # Check for overlap
            if not (slot_end <= busy_start or slot_start >= busy_end):
                return False  # There's an overlap, slot is not free
    
    return True

def print_free_slots(free_slots):
    """Print the free slots found"""
    
    if not free_slots:
        print("\n❌ No common free slots found!")
        return
    
    print(f"\n✅ Found {len(free_slots)} available slots:\n")
    
    for i, slot in enumerate(free_slots, 1):
        print(f"  {i}. {slot['display']}")
        print(f"     ({slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')})")
        print()

def main():
    """Main test function"""
    
    print("🚀 Google Calendar Availability Checker")
    print("=" * 50)
    
    # Authenticate
    service = authenticate()
    print("✅ Authenticated successfully!\n")
    
    # Get email addresses to check
    # Replace these with actual email addresses
    emails = input("Enter email addresses (comma-separated): ").strip().split(',')
    emails = [email.strip() for email in emails]
    
    if not emails or emails == ['']:
        print("❌ No emails provided. Using example...")
        emails = ["interviewer1@example.com", "interviewer2@example.com"]
    
    # Get free/busy info
    freebusy_result = get_freebusy(service, emails)
    
    # Print busy times for each person
    print_busy_times(freebusy_result)
    
    # Find common free slots
    free_slots = find_common_free_slots(freebusy_result, duration_minutes=60, max_slots=5)
    
    # Print results
    print_free_slots(free_slots)
    
    # Test with different duration
    print("\n" + "=" * 50)
    print("Testing with 30-minute slots...")
    free_slots_30 = find_common_free_slots(freebusy_result, duration_minutes=30, max_slots=3)
    print_free_slots(free_slots_30)

if __name__ == "__main__":
    main()