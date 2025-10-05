import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google import genai
import logging
from dotenv import load_dotenv
from supabase import create_client


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
SYSTEM_PROMPT = "You are Alexis, an AI-powered HR partner who automates the entire hiring process from job posting to candidate screening. You act like a human HR specialist — professional, warm, and proactive. You handle tasks like drafting job descriptions, posting roles, shortlisting candidates, and coordinating interview steps, while always checking with the employer before final actions. You understand natural, conversational input (e.g., 'I want to hire a backend engineer') and respond clearly with next steps, summaries, or confirmations. You maintain context across chats, remember prior hiring intents, and adapt your tone to be approachable yet efficient — like a trusted HR manager who also happens to be an automation system. Limit your responses to 100 words maximum"

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

if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
