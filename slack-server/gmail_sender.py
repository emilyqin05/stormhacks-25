import base64
from email.message import EmailMessage
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_schedule_interview_email(message_content, applicant_email, applicant_name):
    """
    Sends an email reply using the Gmail API.

    Args:
      sender: Email address of the receiver.
      reply_subject: The subject of the email.
      reply_body: The body text of the email.
      thread_id: The thread ID to reply to (optional).
      message_id_header: The message ID to reply to for In-Reply-To header (optional).
    """
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


send_email_declaration = {
    "name": "send_schedule_interview_email",
    "description": "Sends email to interview candidate. Use this when you want to send an email to an interview candidate.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

if __name__ == "__main__":
    send_schedule_interview_email("Hello, this is a test email.", "test@test.com", "Test User")
