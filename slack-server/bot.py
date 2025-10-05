import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google import genai
from google.genai import types
from dotenv import load_dotenv

from tools import gmail_function

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

SYSTEM_PROMPT = "You are a helpful assistant that answers Slack messages clearly and concisely."


@app.message("")
def handle_message(message, say):
    user_text = message['text']

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text}
    ]

    tools = types.Tool(function_declarations=[gmail_function])
    config = types.GenerateContentConfig(tools=[tools])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_text,
        config=config,
    )
    
    say(response.text)


if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
