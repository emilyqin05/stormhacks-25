import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")
app = App(token=os.getenv("SLACK_BOT_TOKEN"))  # xoxb-... token

@app.message("")
def handle_message(message, say):
    user_text = message['text']

    response = model.generate_content(user_text)

    say(response.text)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
