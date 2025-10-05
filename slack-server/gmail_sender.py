import base64
from email.mime.text import MIMEText
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from interviewscheduling import html_template

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def send_schedule_interview_email(
    candidate_email: str,
    candidate_name: str,

    interviewer1_slack_id: str,
    interviewer1_names: str,
    interviewer1_emails: str,
    interviewer1_start_times: str,
    interviewer1_end_times: str,
    interviewer1_zoom_link: str,

    interviewer2_slack_id: str,
    interviewer2_names: str,
    interviewer2_emails: str,
    interviewer2_start_times: str,
    interviewer2_end_times: str,
    interviewer2_zoom_link: str,

    interviewer3_slack_id: str,
    interviewer3_names: str,
    interviewer3_emails: str,
    interviewer3_start_times: str,
    interviewer3_end_times: str,
    interviewer3_zoom_link: str,
):
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
        service = build("gmail", "v1", credentials=creds)

        link1 = getButtonLink(
            candidate_email,
            candidate_name,
            interviewer1_slack_id,
            interviewer1_names,
            interviewer1_emails,
            interviewer1_start_times,
            interviewer1_end_times,
            interviewer1_zoom_link,
        )
        link2 = getButtonLink(
            candidate_email,
            candidate_name,
            interviewer2_slack_id,
            interviewer2_names,
            interviewer2_emails,
            interviewer2_start_times,
            interviewer2_end_times,
            interviewer2_zoom_link,
        )
        link3 = getButtonLink(
            candidate_email,
            candidate_name,
            interviewer3_slack_id,
            interviewer3_names,
            interviewer3_emails,
            interviewer3_start_times,
            interviewer3_end_times,
            interviewer3_zoom_link,
        )

        # Inject generated links into the interview scheduling HTML template
        html = (
            html_template
            .replace("link1", link1)
            .replace("link2", link2)
            .replace("link3", link3)
        )
        message = MIMEText(html, 'text/html')
        message["To"] = candidate_email
        message["From"] = "candidateagent9@gmail.com"

        subject = f"Congrats {candidate_name}! You've been scheduled for an interview."
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


def getButtonLink(
    candidate_email: str,
    candidate_name: str,
    interviewer_slack_id: str,
    interviewer_names: str,
    interviewer_emails: str,
    interviewer_start_times: str,
    interviewer_end_times: str,
    interviewer_zoom_link: str,
):
    base_url = "http://127.0.0.1:5001/book-interview"
    return (
        f"{base_url}?"
        f"candidate_email={candidate_email}&"
        f"candidate_name={candidate_name}&"
        f"interviewer_slack_id={interviewer_slack_id}&"
        f"interviewer_names={interviewer_names}&"
        f"interviewer_emails={interviewer_emails}&"
        f"interviewer_start_times={interviewer_start_times}&"
        f"interviewer_end_times={interviewer_end_times}&"
        f"interviewer_zoom_link={interviewer_zoom_link}"
    )


def main():
    # Mock data for testing send_schedule_interview_email
    candidate_email = "test.candidate@example.com"
    candidate_name = "TestCandidate"

    interviewer1_slack_id = "U123456"
    interviewer1_names = "InterviewerOne"
    interviewer1_emails = "interviewer1@example.com"
    interviewer1_start_times = "2025-10-10T09:00:00"
    interviewer1_end_times = "2025-10-10T10:00:00"
    interviewer1_zoom_link = "https://zoom.us/j/1234567890"

    interviewer2_slack_id = "U234567"
    interviewer2_names = "InterviewerTwo"
    interviewer2_emails = "interviewer2@example.com"
    interviewer2_start_times = "2025-10-10T11:00:00"
    interviewer2_end_times = "2025-10-10T12:00:00"
    interviewer2_zoom_link = "https://zoom.us/j/2345678901"

    interviewer3_slack_id = "U345678"
    interviewer3_names = "InterviewerThree"
    interviewer3_emails = "interviewer3@example.com"
    interviewer3_start_times = "2025-10-10T13:00:00"
    interviewer3_end_times = "2025-10-10T14:00:00"
    interviewer3_zoom_link = "https://zoom.us/j/3456789012"

    send_schedule_interview_email(
        candidate_email,
        candidate_name,
        interviewer1_slack_id,
        interviewer1_names,
        interviewer1_emails,
        interviewer1_start_times,
        interviewer1_end_times,
        interviewer1_zoom_link,
        interviewer2_slack_id,
        interviewer2_names,
        interviewer2_emails,
        interviewer2_start_times,
        interviewer2_end_times,
        interviewer2_zoom_link,
        interviewer3_slack_id,
        interviewer3_names,
        interviewer3_emails,
        interviewer3_start_times,
        interviewer3_end_times,
        interviewer3_zoom_link,
    )

if __name__ == "__main__":
    main()