# app.py - MVP Interview Booking Service (OAuth)
from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

app = Flask(__name__)

# Configuration
CALENDAR_ID = 'candidateagent9@gmail.com'
SCOPES = ['https://www.googleapis.com/auth/calendar']  # Full read/write access
TOKEN_FILE = './slack-server/gcal-integration/token.pickle'
CREDENTIALS_FILE = './slack-server/credentials.json'


def get_calendar_service():
    creds = None
    
    # Load saved credentials
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials OR scope changed, re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                print("🔄 Deleting old token and re-authenticating...")
                os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ New credentials obtained!")
        
        # Save credentials for next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)


@app.get('/book-interview')
def book_interview():
    # Get query parameters
    interviewer_email = request.args.get('interviewer_email')
    applicant_email = request.args.get('applicant_email')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    zoom_link = request.args.get('zoom_link')
    interviewer_name = request.args.get('interviewer_name', 'Team Member')
    
    # Validate required parameters
    if not all([interviewer_email, applicant_email, start_time, end_time, zoom_link]):
        return jsonify({"ok": False, "error": "Missing required parameters"}), 400
    
    try:
        # Ensure timezone format
        if not start_time.endswith('Z'):
            start_time += 'Z'
        if not end_time.endswith('Z'):
            end_time += 'Z'
        
        # Build calendar event
        event = {
            'summary': f'Interview: {interviewer_name} + Candidate',
            'location': zoom_link,
            'description': f'Zoom Link: {zoom_link}',
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [
                {'email': interviewer_email},
                {'email': applicant_email}
            ]
        }
        
        # Create event
        service = get_calendar_service()
        created_event = service.events().insert(
            calendarId='primary',  # Use 'primary' when using OAuth
            body=event,
            sendUpdates='all'
        ).execute()
        
        return jsonify({
            "ok": True,
            "message": "Interview booked successfully",
            "event_link": created_event.get('htmlLink')
        }), 200
        
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)