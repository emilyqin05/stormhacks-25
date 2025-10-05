import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google import genai
from google.genai import types
from dotenv import load_dotenv
from supabase import create_client
from gmail_sender import send_schedule_interview_email_declaration, send_schedule_interview_email
import random
from slack_sdk import WebClient
import requests
from io import BytesIO


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
SYSTEM_PROMPT = "You are Alexis, an AI-powered HR partner who automates the entire hiring process from job posting to candidate screening. You act like a human HR specialist — professional, warm, and proactive. You handle tasks like drafting job descriptions, posting roles, shortlisting candidates, and coordinating interview steps, while always checking with the employer before final actions. You understand natural, conversational input (e.g., 'I want to hire a backend engineer') and respond clearly with next steps, summaries, or confirmations. You maintain context across chats, remember prior hiring intents, and adapt your tone to be approachable yet efficient — like a trusted HR manager who also happens to be an automation system. Limit your responses to 100 words maximum"
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

chat_history = [
    {"role": msg["role"], "content": msg["content"]}
    for msg in supabase.table("messages").select("*").order("created_at").execute().data
]

print("got chat")

@app.message("")
def handle_message(message, say):
    user_text = message['text']
    if len(chat_history) == 0:
        chat_history.append({"role": "system", "content": SYSTEM_PROMPT})
        supabase.table("messages").insert([
            {"role": "system", "content": SYSTEM_PROMPT}
        ]).execute()
    chat_history.append({"role": "user", "content": user_text})
    conversation_prompt = "\n".join(
    f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    )


    tools = types.Tool(function_declarations=[send_schedule_interview_email_declaration])
    config = types.GenerateContentConfig(tools=[tools])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[conversation_prompt]
    )
    chat_history.append({"role": "assistant", "content": response.text})
    supabase.table("messages").insert([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response.text}
    ]).execute()
    say(response.text)


def getResume():
    #Magic ats
    response = supabase.table("applicants").select("*").execute()
    rows = response.data

    random_rows = random.sample(rows, 2)
    return random_rows

def sendInterview(email, name):
    ints = [{'id': 'int_001', 'name': 'Emily Qin', 'email': '123emilyqin@gmail.com', 'slack_id': 'U1234ABCD', 'slack_email': 'alice@company.com', 'zoom_link': 'https://zoom.us/j/alice-personal-room', 'role': 'Senior Engineer', 'start_time': '2025-10-06T09:00:00', 'end_time': '2025-10-06T10:00:00'},{'id': 'int_002','name': 'Agent','email': 'candidateagent9@gmail.com','slack_id': 'U5678EFGH','slack_email': 'bob@company.com','zoom_link': 'https://zoom.us/j/bob-personal-room','role': 'Tech Lead','start_time': '2025-10-06T09:00:00','end_time': '2025-10-06T10:00:00'}
    ,{'id': 'int_003','name': 'Agent','email': 'notrealcandidate@gmail.com','slack_id': 'U5678EFGH','slack_email': 'weafbob@company.com','zoom_link': 'https://zoom.us/j/bob-personal-room','role': 'Tech Lead','start_time': '2025-10-08T09:00:00','end_time': '2025-10-08T10:00:00'}]
    
    send_schedule_interview_email("You got the job", "jjforce17@gmail.com", "Fabian")
    


    @app.command("/getresumes")
    def showResume(ack, say, command):
        ack()
        app.logger.info("error  called")
        try:
            resumes = getResume()
            for resume in resumes:
                pdf_url = resume.get("resume_url")  # adjust to your column name in Supabase
                name = resume.get("name", "Candidate")
                email = resume.get("email", "no email avail")

                if pdf_url:
                    # Download PDF into memory
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        file_bytes = BytesIO(response.content)
                        slack_client.files_upload_v2(
                        channel=command["channel_id"],
                        file=file_bytes,
                        filename=f"{name}.pdf",
                        title=f"{name}'s Resume",
                        initial_comment=f"Here is {name}'s resume. And their email is {email}"
                    )
                    else:
                        say(f"Could not download {name}'s resume.")
                else:
                    say(f"{name} does not have a resume uploaded.")
        except Exception as e:
            print("error", e)

if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()