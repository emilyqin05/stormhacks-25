import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import jsonify, request
from time import sleep
import google.generativeai as genai

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.5-pro")

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
                # Send prompt to Gemini
                prompt = f"""Given this job description, About the job
We help the world run better

At SAP, we keep it simple: you bring your best to us, and we'll bring out the best in you. We're builders touching over 20 industries and 80% of global commerce, and we need your unique talents to help shape what's next. The work is challenging – but it matters. You'll find a place where you can be yourself, prioritize your wellbeing, and truly belong. What's in it for you? Constant learning, skill growth, great benefits, and a team that wants you to grow and succeed.

About The SAP Internship Experience Program

The SAP Internship Experience Program is SAP’s global, strategic, paid internship program that provides university students with opportunities to find purpose in their careers.

Three reasons to intern at SAP

Culture of collaboration: meet with mentors, make new friends across the globe and create a thriving personal network.
Project-driven experience: gain cross-functional skills from our virtual and in-person learning sessions, diverse subject matter experts, and project deliverables. 
Gain visibility: with SAP Internship Experience Program in your title, you’ll have a global network of SAP leaders, entrepreneurs and career development opportunities at your fingertips. 

What You’ll Do

Position Title: SAP iXp Intern - Agile Developer, Business Data Cloud

Location: Vancouver, BC

Expected Start Date to End Date: January 05, 2026 – August 28, 2026

Internship Duration: 8 months

Work Hours: 40 hours per week desired

Engage in practical coding, test, and design.
Develop, test, and enhance software by understanding requirements, implementing, testing features, writing automated tests, and resolving issues.
Gain experience in maintaining and improving a codebase.
Embrace lean and agile software development principles by participating in daily stand-ups, sprint planning, and retrospectives.
Learn from team members through code reviews, sprint demos, knowledge-sharing sessions, and regular 1:1 coaching.
Grow in leadership, presentation, and other soft skills.
Collaborate with designers, product managers, and engineers to deliver high-quality products.

What You Bring

We’re looking for someone who takes initiative, perseveres, and stays curious. You like to work on meaningful innovative projects and are energized by lifelong learning.

Currently registered in Computer Science or Engineering at an accredited post-secondary institution.
Ability to work well in a team as well as independently
Possesses a positive self-motivated can-do attitude
Working knowledge of HTML, CSS, JavaScript, and/or Java
Strong motivation to learn, teach, and grow
Critical thinker with a passion for customers, engineering, and product quality
Must commit to an 8-month internship starting January 2026 on-site at our beautiful SAP Vancouver, Canada office location
Familiarity with cloud computing concepts
Basic understanding of data structures and algorithms
Experience with version control systems (e.g., Git)
Strong communication and documentation skills

Meet your team

Business Data Cloud (BDC) is a global team with members in various countries, serving hundreds of thousands of customers around the world. BDC is a cloud-based data & analytics solution that integrates business intelligence, planning, and predictive analytics into a single platform.

If you have less than three years' professional experience, you'll be part of SAP Next Gen.

SAP Next Gen connects curious, ambitious, team-oriented students and early talent to SAP's global community of innovators, peers, and leaders.

With access to hands-on experiences that sharpen skills, and the wisdom of the leaders shaping what's next, knowledge becomes impact and mentors become allies. 

SAP Next Gen doesn't just prepare you for the future, it nurtures your talents and your drive so that you can create it with us, together.

Bring out your best

SAP innovations help more than four hundred thousand customers worldwide work together more efficiently and use business insight more effectively. Originally known for leadership in enterprise resource planning (ERP) software, SAP has evolved to become a market leader in end-to-end business application software and related services for database, analytics, intelligent technologies, and experience management. As a cloud company with two hundred million users and more than one hundred thousand employees worldwide, we are purpose-driven and future-focused, with a highly collaborative team ethic and commitment to personal development. Whether connecting global industries, people, or platforms, we help ensure every challenge gets the solution it deserves. At SAP, you can bring out your best.

We win with inclusion

SAP’s culture of inclusion, focus on health and well-being, and flexible working models help ensure that everyone – regardless of background – feels included and can run at their best. At SAP, we believe we are made stronger by the unique capabilities and qualities that each person brings to our company, and we invest in our employees to inspire confidence and help everyone realize their full potential. We ultimately believe in unleashing all talent and creating a better world.

SAP is committed to the values of Equal Employment Opportunity and provides accessibility accommodations to applicants with physical and/or mental disabilities. If you are interested in applying for employment with SAP and are in need of accommodation or special assistance to navigate our website or to complete your application, please send an e-mail with your request to Recruiting Operations Team: Careers@sap.com.

For SAP employees: Only permanent roles are eligible for the SAP Employee Referral Program, according to the eligibility rules set in the SAP Referral Policy. Specific conditions may apply for roles in Vocational Training.

Qualified applicants will receive consideration for employment without regard to their age, race, religion, national origin, ethnicity, gender (including pregnancy, childbirth, et al), sexual orientation, gender identity or expression, protected veteran status, or disability, in compliance with applicable federal, state, and local legal requirements.

SAP believes the value of pay transparency contributes towards an honest and supportive culture and is a significant step toward demonstrating SAP’s commitment to pay equity. SAP provides the hourly base salary rate range applicable for the posted role. The targeted range for this position is 18.00 - 40.00 CAD. The actual amount to be offered to the successful candidates will be within that range, dependent upon the key aspects of each case which may include education, skills, experience, scope of the role, location, etc. as determined through the selection process. SAP offers limited benefits for employees hired into hourly or like roles subject to appliable plan/policy terms. A summary of benefits and eligibility requirements can be found by clicking this link: www.SAPNorthAmericaBenefits.com.

Due to the nature of the role, which involves global interactions with SAP entities, as well as with employees and stakeholders in Canada, functional proficiency in English is required for positions based in the Quebec.

AI Usage in the Recruitment Process

For information on the responsible use of AI in our recruitment process, please refer to our Guidelines for Ethical Usage of AI in the Recruiting Process.

Please note that any violation of these guidelines may result in disqualification from the hiring process.

Requisition ID: 431304 | Work Area: Information Technology | Expected Travel: 0 - 10% | Career Status: Student | Employment Type: Limited Full Time | Additional Locations: #SAPNextGen
And given that the interview process will be a one hour interview, with two medium or easy leet code questions, with a code review and behavioural section towards the end of the interview.
This is done with a single interviewer.
When answering, make sure to never say that this context is provided by me. The context is from you, the AI recruiter.
Given this context, answer the question from the candidate in a human way and keep it short and consise, like how a recruiter would and make sure to not say CANDIDATE NAME, make sure to not refer to the canditate by name. This is the question below, {original_body}."""
                response = model.generate_content(prompt)

                # Get the text
                answer = response.text

                # Print to console (optional)
                print("Prompt:", prompt)
                print("Response:", answer)

                # Compose the reply
                reply_body = f"{answer}" if original_body else "Sorry I couldn't get that. Can you resend you message?"  

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
