import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Dict, Optional
import json

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarManager:
    """
    Manages Google Calendar operations for interview scheduling.
    Designed to be called by Slack bot with interviewer data.
    """
    
    def __init__(self, credentials_path: str = './email-server/credentials.json', token_path: str = 'token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Calendar API authenticated")
    
    def find_interview_slots(
        self,
        interviewers: List[Dict],
        duration_minutes: int = 60,
        days_ahead: int = 14,
        max_slots: int = 5,
        business_hours: tuple = (9, 17)
    ) -> List[Dict]:
        """
        Find available interview slots for multiple interviewers.
        
        Args:
            interviewers: List of dicts with 'email', 'name', 'slack_id' keys
            duration_minutes: Interview duration (default 60)
            days_ahead: How many days to search (default 14)
            max_slots: Maximum number of slots to return (default 5)
            business_hours: Tuple of (start_hour, end_hour) in 24h format
            
        Returns:
            List of available time slots with interviewer info
        """
        
        if not interviewers:
            raise ValueError("Must provide at least one interviewer")
        
        # Extract emails for calendar lookup
        interviewer_emails = [i['email'] for i in interviewers]
        
        print(f"\n🔍 Finding slots for {len(interviewers)} interviewers:")
        for interviewer in interviewers:
            print(f"  • {interviewer['name']} ({interviewer['email']})")
        
        # Get free/busy data
        freebusy_data = self._get_freebusy(interviewer_emails, days_ahead)
        
        # Find common free slots
        free_slots = self._find_common_slots(
            freebusy_data,
            duration_minutes,
            max_slots,
            business_hours
        )
        
        # Attach interviewer info to each slot
        for slot in free_slots:
            slot['interviewers'] = interviewers
            slot['num_interviewers'] = len(interviewers)
        
        return free_slots
    
    def find_interview_slots_any_available(
        self,
        interviewers: List[Dict],
        num_slots: int = 3,
        duration_minutes: int = 60,
        days_ahead: int = 14,
        business_hours: tuple = (9, 17)
    ) -> List[Dict]:
        """
        Find interview slots where AT LEAST ONE interviewer is available.
        Returns slots with the available interviewer assigned.
        
        Args:
            interviewers: List of dicts with 'id', 'email', 'name', 'slack_id', 'slack_email', 'zoom_link', 'role' keys
            num_slots: Number of slots to return (default 3)
            duration_minutes: Interview duration (default 60)
            days_ahead: How many days to search (default 14)
            business_hours: Tuple of (start_hour, end_hour) in 24h format
            
        Returns:
            List of interview slots, each with one available interviewer assigned
        """
        
        if not interviewers:
            raise ValueError("Must provide at least one interviewer")
        
        # Extract emails for calendar lookup
        interviewer_emails = [i['email'] for i in interviewers]
        
        print(f"\n🔍 Finding {num_slots} slots where at least 1 of {len(interviewers)} interviewers is available")
        
        # Get free/busy data
        freebusy_data = self._get_freebusy(interviewer_emails, days_ahead)
        calendars = freebusy_data.get('calendars', {})
        
        # Find slots with at least one available interviewer
        interview_slots = []
        start_hour, end_hour = business_hours
        
        # Start searching from tomorrow at start of business hours
        search_start = datetime.now().replace(
            hour=start_hour, 
            minute=0, 
            second=0, 
            microsecond=0
        ) + timedelta(days=1)
        
        search_end = search_start + timedelta(days=days_ahead)
        current = search_start
        
        print(f"⏰ Searching for {duration_minutes}-min slots between {start_hour}:00-{end_hour}:00...")
        
        while current < search_end and len(interview_slots) < num_slots:
            # Skip weekends
            if current.weekday() >= 5:
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            # Ensure we're in business hours
            if current.hour < start_hour:
                current = current.replace(hour=start_hour, minute=0)
                continue
            elif current.hour >= end_hour:
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            slot_end = current + timedelta(minutes=duration_minutes)
            
            # Don't let slots extend past business hours
            if slot_end.hour > end_hour or (slot_end.hour == end_hour and slot_end.minute > 0):
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            # Find which interviewers are available for this slot
            available_interviewers = self._get_available_interviewers_for_slot(
                calendars, interviewers, current, slot_end
            )
            
            if available_interviewers:
                # Pick the first available interviewer for this slot
                selected_interviewer = available_interviewers[0]
                
                interview_slots.append({
                    'id': selected_interviewer.get('id', f'int_{len(interview_slots)+1:03d}'),
                    'name': selected_interviewer['name'],
                    'email': selected_interviewer['email'],
                    'slack_id': selected_interviewer.get('slack_id', ''),
                    'slack_email': selected_interviewer.get('slack_email', selected_interviewer['email']),
                    'zoom_link': selected_interviewer.get('zoom_link', ''),
                    'role': selected_interviewer.get('role', ''),
                    'start_time': current.isoformat(),
                    'end_time': slot_end.isoformat()
                })
                
                print(f"  ✓ Found: {current.strftime('%a %m/%d at %I:%M %p')} - {selected_interviewer['name']}")
                
                # Skip ahead more to get different time slots
                current += timedelta(hours=2)
            else:
                # Check every 30 minutes
                current += timedelta(minutes=30)
        
        print(f"\n✅ Found {len(interview_slots)} interview slots")
        return interview_slots
    
    def _get_available_interviewers_for_slot(
        self,
        calendars: Dict,
        interviewers: List[Dict],
        slot_start: datetime,
        slot_end: datetime
    ) -> List[Dict]:
        """Get list of interviewers who are available for a specific time slot"""
        
        available = []
        
        for interviewer in interviewers:
            email = interviewer['email']
            cal_data = calendars.get(email, {})
            busy_times = cal_data.get('busy', [])
            
            is_free = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                # Make timezone-naive for comparison
                busy_start = busy_start.replace(tzinfo=None)
                busy_end = busy_end.replace(tzinfo=None)
                
                # Check for any overlap
                if not (slot_end <= busy_start or slot_start >= busy_end):
                    is_free = False
                    break
            
            if is_free:
                available.append(interviewer)
        
        return available
    
    def _get_freebusy(self, emails: List[str], days_ahead: int) -> Dict:
        """Get free/busy information for specified email addresses"""
        
        time_min = datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "America/Los_Angeles",  # Adjust to your timezone
            "items": [{"id": email} for email in emails]
        }
        
        try:
            result = self.service.freebusy().query(body=body).execute()
            return result
        except Exception as e:
            print(f"❌ Error fetching free/busy: {e}")
            raise
    
    def _find_common_slots(
        self,
        freebusy_data: Dict,
        duration_minutes: int,
        max_slots: int,
        business_hours: tuple
    ) -> List[Dict]:
        """Find time slots when all interviewers are available"""
        
        calendars = freebusy_data.get('calendars', {})
        start_hour, end_hour = business_hours
        
        # Start searching from tomorrow at start of business hours
        search_start = datetime.now().replace(
            hour=start_hour, 
            minute=0, 
            second=0, 
            microsecond=0
        ) + timedelta(days=1)
        
        search_end = search_start + timedelta(days=14)
        
        free_slots = []
        current = search_start
        
        print(f"\n⏰ Searching for {duration_minutes}-min slots between {start_hour}:00-{end_hour}:00...")
        
        while current < search_end and len(free_slots) < max_slots:
            # Skip weekends
            if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            # Ensure we're in business hours
            if current.hour < start_hour:
                current = current.replace(hour=start_hour, minute=0)
                continue
            elif current.hour >= end_hour:
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            slot_end = current + timedelta(minutes=duration_minutes)
            
            # Don't let slots extend past business hours
            if slot_end.hour > end_hour or (slot_end.hour == end_hour and slot_end.minute > 0):
                current += timedelta(days=1)
                current = current.replace(hour=start_hour, minute=0)
                continue
            
            # Check if all interviewers are free
            if self._is_slot_free_for_all(calendars, current, slot_end):
                free_slots.append({
                    'start_time': current.isoformat(),
                    'end_time': slot_end.isoformat(),
                    'start_datetime': current,
                    'end_datetime': slot_end,
                    'display': current.strftime('%A, %B %d at %I:%M %p'),
                    'display_short': current.strftime('%a %m/%d at %I:%M %p'),
                    'date': current.strftime('%Y-%m-%d'),
                    'time': current.strftime('%I:%M %p'),
                    'duration_minutes': duration_minutes
                })
                
                print(f"  ✓ Found: {current.strftime('%a %m/%d at %I:%M %p')}")
            
            # Check every 30 minutes
            current += timedelta(minutes=30)
        
        print(f"\n✅ Found {len(free_slots)} available slots")
        return free_slots
    
    def _is_slot_free_for_all(
        self,
        calendars: Dict,
        slot_start: datetime,
        slot_end: datetime
    ) -> bool:
        """Check if time slot is free for all people"""
        
        for email, cal_data in calendars.items():
            busy_times = cal_data.get('busy', [])
            
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                # Make timezone-naive for comparison
                busy_start = busy_start.replace(tzinfo=None)
                busy_end = busy_end.replace(tzinfo=None)
                
                # Check for any overlap
                if not (slot_end <= busy_start or slot_start >= busy_end):
                    return False  # Overlap found - slot is not free
        
        return True
    
    def get_interviewer_availability_summary(self, interviewers: List[Dict], days: int = 7) -> Dict:
        """
        Get a summary of each interviewer's availability.
        Useful for debugging or displaying to hiring manager.
        """
        
        emails = [i['email'] for i in interviewers]
        freebusy_data = self._get_freebusy(emails, days)
        
        summary = {}
        calendars = freebusy_data.get('calendars', {})
        
        for interviewer in interviewers:
            email = interviewer['email']
            cal_data = calendars.get(email, {})
            busy_times = cal_data.get('busy', [])
            
            summary[interviewer['name']] = {
                'email': email,
                'slack_id': interviewer.get('slack_id'),
                'num_busy_slots': len(busy_times),
                'busy_times': [
                    {
                        'start': datetime.fromisoformat(b['start'].replace('Z', '+00:00')).strftime('%a %m/%d %I:%M %p'),
                        'end': datetime.fromisoformat(b['end'].replace('Z', '+00:00')).strftime('%I:%M %p')
                    }
                    for b in busy_times[:10]  # Limit to first 10
                ]
            }
        
        return summary
    
    def select_interviewers_for_slot(
        self,
        available_interviewers: List[Dict],
        time_slot: Dict,
        num_interviewers: int = 2
    ) -> List[Dict]:
        """
        From a pool of available interviewers, select N for a specific time slot.
        This checks their calendar one more time to ensure availability.
        
        Args:
            available_interviewers: Pool of interviewers to choose from
            time_slot: The specific time slot dict with 'start_datetime', 'end_datetime'
            num_interviewers: How many to select (default 2)
            
        Returns:
            List of selected interviewers
        """
        
        emails = [i['email'] for i in available_interviewers]
        
        # Re-check availability for this specific slot
        freebusy_data = self._get_freebusy(emails, days_ahead=1)
        calendars = freebusy_data.get('calendars', {})
        
        available_for_slot = []
        
        for interviewer in available_interviewers:
            email = interviewer['email']
            cal_data = calendars.get(email, {})
            busy_times = cal_data.get('busy', [])
            
            is_free = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00')).replace(tzinfo=None)
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00')).replace(tzinfo=None)
                
                slot_start = time_slot['start_datetime']
                slot_end = time_slot['end_datetime']
                
                if not (slot_end <= busy_start or slot_start >= busy_end):
                    is_free = False
                    break
            
            if is_free:
                available_for_slot.append(interviewer)
        
        # Return the requested number (or all if fewer available)
        return available_for_slot[:num_interviewers]


def format_slots_for_slack(slots: List[Dict]) -> str:
    """Format slots nicely for Slack message"""
    if not slots:
        return "❌ No available slots found"
    
    message = f"📅 *Found {len(slots)} available interview slots:*\n\n"
    
    for i, slot in enumerate(slots, 1):
        message += f"{i}. {slot['display']}\n"
        message += f"   _Duration: {slot['duration_minutes']} minutes_\n"
        if 'interviewers' in slot:
            interviewers_names = [interviewer['name'] for interviewer in slot['interviewers']]
            message += f"   _Interviewers: {', '.join(interviewers_names)}_\n"
        message += "\n"
    
    return message


def format_slots_for_email(slots: List[Dict]) -> str:
    """Format slots for email (HTML)"""
    if not slots:
        return "<p>No available slots found.</p>"
    
    html = "<p>Please select one of the following available times:</p><ul>"
    
    for slot in slots:
        html += f"<li>{slot['display']} ({slot['duration_minutes']} minutes)</li>"
    
    html += "</ul>"
    
    return html