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
from google.genai import types
import calendar_module


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


    interviewTool = types.Tool(function_declarations=[send_schedule_interview_email_declaration])
    resumeTool = types.Tool(function_declarations=[get_resume_declaration])

    config = types.GenerateContentConfig(tools=[interviewTool, resumeTool])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[conversation_prompt],
        config=config,

    )

    # Check if the we trigger a tool call or not
    if response.candidates[0].content.parts[0].function_call:
        print("Gemini wants to call a function")
        #chat_history.append(response.candidates[0].content.parts[0]) #we add the intent to call tool to the chat history
        func_call = response.candidates[0].content.parts[0].function_call
        print("Function call detected:", func_call.name)
        print("Args:", func_call.args)
        if func_call.name == "send_schedule_interview_email":
            result = send_schedule_interview_email(**func_call.args)
            print("Result is", result)
            chat_history.append({"role": "function", "content": f"{func_call.name} returned: {result}"})
            conversation_prompt = "\n".join(
                f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
            )
            response = client.models.generate_content(model="gemini-2.5-flash",contents=[conversation_prompt],config=config,)
            
    chat_history.append({"role": "assistant", "content": response.text})
    supabase.table("messages").insert([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": response.text}
    ]).execute()
    say(response.text)

get_resume_declaration = types.FunctionDeclaration(
    name="showResume",
    description="Fetches a list of candidate resumes from the directory table. Returns the top N resumes randomly selected.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="The number of resumes to fetch (default 3)"
            )
        },
        required=[]
    )
)


def getResume():
    #Magic ats
    response = supabase.table("applicants").select("*").execute()
    rows = response.data

    random_rows = random.sample(rows, 2)
    return random_rows


def sendInterview(email, name):
    interviewers = [
    {
        'id': 'int_001',
        'name': 'Emily Qin',
        'email': '123emilyqin@gmail.com',
        'slack_id': 'U1234ABCD',
        'slack_email': 'emily@company.com',
        'zoom_link': 'https://zoom.us/j/emily-personal-room',
        'role': 'Senior Engineer'
    },
    {
        'id': 'int_002',
        'name': 'Simon',
        'email': 'candidateagent9@gmail.com',
        'slack_id': 'U5678EFGH',
        'slack_email': 'agent@company.com',
        'zoom_link': 'https://zoom.us/j/agent-personal-room',
        'role': 'Tech Lead'
    },
    {
        'id': 'int_003',
        'name': 'Jule',
        'email': 'name@gmail.com',
        'slack_id': 'I5678EFGH',
        'slack_email': 'name@company.com',
        'zoom_link': 'https://zoom.us/j/name-personal-room',
        'role': 'Design Lead'
    }
]
    
    cal_manager = calendar_module.CalendarManager()
    ints = cal_manager.find_interview_slots_any_available(
            interviewers=interviewers,
            num_slots=3,
            duration_minutes=60
        )
    
    send_schedule_interview_email(
        candidate_email=email,
        candidate_name=name,

        interviewer1_slack_id=ints[0]['slack_id'],
        interviewer1_names=ints[0]['name'],
        interviewer1_emails=ints[0]['email'],
        interviewer1_start_times=ints[0]['start_time'],
        interviewer1_end_times=ints[0]['end_time'],
        interviewer1_zoom_links=ints[0]['zoom_link'],

        interviewer2_slack_id=ints[1]['slack_id'],
        interviewer2_names=ints[1]['name'],
        interviewer2_emails=ints[1]['email'],
        interviewer2_start_times=ints[1]['start_time'],
        interviewer2_end_times=ints[1]['end_time'],
        interviewer2_zoom_links=ints[1]['zoom_link'],

        interviewer3_slack_id=ints[2]['slack_id'],
        interviewer3_names=ints[2]['name'],
        interviewer3_emails=ints[2]['email'],
        interviewer3_start_times=ints[2]['start_time'],
        interviewer3_end_times=ints[2]['end_time'],
        interviewer3_zoom_links=ints[2]['zoom_link'],
    )
    

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