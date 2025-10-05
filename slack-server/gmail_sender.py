import base64
from email.message import EmailMessage
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_schedule_interview_email(message_content: str, applicant_email: str, applicant_name: str):
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

    try:
        # Call the Gmail API to send the email
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        # TODO: make template for message content

        # TODO: have scheduling link in message content
        message.set_content(message_content)
        message["To"] = applicant_email
        message["From"] = "candidateagent9@gmail.com"

        subject = f"Congrats {applicant_name}! You've been scheduled for an interview."
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}


        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )

    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


send_schedule_interview_email_declaration = {
    "name": "send_schedule_interview_email",
    "description": "Sends email to schedule an interview. Use this when you want to schedule an interview with shortlisted candidiates.",
    "parameters": {
        "type": "object",
        "properties": {
            "message_content": {
                "type": "string",
                "description": "Plain text body of the email to send to the candidate.",
            },
            "applicant_email": {
                "type": "string",
                "format": "email",
                "description": "Candidate's email address.",
            },
            "applicant_name": {
                "type": "string",
                "description": "Candidate's full name used in the email subject/body.",
            },
        },
        "required": ["message_content", "applicant_email", "applicant_name"],
    },
}