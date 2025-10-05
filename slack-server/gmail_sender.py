import base64
import os.path

from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_schedule_interview_email(sender, reply_subject, reply_body, thread_id, message_id_header):
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

        reply_msg = create_reply_message(
            to=sender,
            subject=reply_subject,
            message_text=reply_body,
            thread_id=thread_id,
            message_id=message_id_header
        )

        result = service.users().messages().send(userId="me", body=reply_msg).execute()
        print(f"Email sent successfully! Message ID: {result.get('id')}")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def create_reply_message(to, subject, message_text, thread_id=None, message_id=None):
    """
    Create a message for an email reply.

    Args:
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      thread_id: The thread ID to reply to.
      message_id: The message ID to reply to (for In-Reply-To header).

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    if message_id:
        message['In-Reply-To'] = message_id
        message['References'] = message_id

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    body = {'raw': raw_message}
    if thread_id:
        body['threadId'] = thread_id

    return body


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
    send_schedule_interview_email("", "Interview Schedule", "Hello, this is a test email.", "1234567890", "1234567890")
