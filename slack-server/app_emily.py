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
# TOKEN_FILE = './slack-server/gcal-integration/token.pickle'
# CREDENTIALS_FILE = './slack-server/credentials.json'

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())



# @app.get('/book-interview')
def book_interview(interviewer_email, applicant_email, start_time, end_time, zoom_link, interviewer_name):  
    # Validate required parameters
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
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
    # app.run(host='0.0.0.0', port=5001, debug=True)
    main()