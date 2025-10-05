import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep

# Scope for read/write access
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def create_message(to, subject, message_text):
    """Create a message for an email reply."""
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def func():
    """Auto-replies to unread emails in Gmail inbox (within the same thread)."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)

        # Step 1: Get unread messages
        response = service.users().messages().list(userId="me", labelIds=["INBOX", "UNREAD"]).execute()
        messages = response.get("messages", [])

        if not messages:
            print("No unread messages.")
            return

        print(f"Found {len(messages)} unread messages.")

        for msg in messages:
            msg_id = msg["id"]

            # Get the full metadata of the message including thread ID and headers
            message = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "Subject", "Message-ID"]
            ).execute()

            headers = message["payload"]["headers"]
            sender = subject = message_id_header = None

            for h in headers:
                if h["name"] == "From":
                    sender = h["value"]
                elif h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "Message-ID":
                    message_id_header = h["value"]

            thread_id = message.get("threadId")

            if sender and message_id_header:
                print(f"Replying to: {sender}, Subject: {subject}")
                reply_subject = subject or "your message"
                full_msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
                payload = full_msg.get("payload", {})
                parts = payload.get("parts", [])

                original_body = ""

                # Try to find plain text part
                for part in parts:
                    if part.get("mimeType") == "text/plain":
                        body_data = part.get("body", {}).get("data")
                        if body_data:
                            original_body = base64.urlsafe_b64decode(body_data).decode("utf-8").strip()
                            break

                # Fallback if there's no multipart
                if not original_body and payload.get("mimeType") == "text/plain":
                    body_data = payload.get("body", {}).get("data")
                    if body_data:
                        original_body = base64.urlsafe_b64decode(body_data).decode("utf-8").strip()

                #make api call here
                

                # Compose the reply
                reply_body = f"{original_body}, confirmed!" if original_body else "Confirmed!"  

                reply_msg = create_reply_message(
                    to=sender,
                    subject=reply_subject,
                    message_text=reply_body,
                    thread_id=thread_id,
                    message_id=message_id_header
                )

                service.users().messages().send(userId="me", body=reply_msg).execute()

                # Mark the original message as read
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

def create_reply_message(to, subject, message_text, thread_id, message_id):
    """Create a reply message that stays in the same thread."""
    from email.mime.text import MIMEText
    import base64

    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = f"Re: {subject}"
    message["In-Reply-To"] = message_id
    message["References"] = message_id

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {
        "raw": raw_message,
        "threadId": thread_id
    }

def main():
  while(True):
    func()
    sleep(3)

if __name__ == "__main__":
    main()
