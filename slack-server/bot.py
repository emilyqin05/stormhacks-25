import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google import genai
import logging
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

SYSTEM_PROMPT = "You are a helpful assistant that answers Slack messages clearly and concisely."

chat_history = {}

@app.message("")
def handle_message(message, say):
    channel_id = message['channel']
    user_text = message['text']
    
    if channel_id not in chat_history:
        chat_history[channel_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    chat_history[channel_id].append({"role": "user", "content": user_text})
    
    conversation_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[channel_id]
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conversation_text
    )
    
    chat_history[channel_id].append({"role": "assistant", "content": response.text})
    
    say(response.text)


if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
