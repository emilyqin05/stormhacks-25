from flask import Flask
import imaplib, smtplib, email, time
from email.mime.text import MIMEText
from threading import Thread
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def check_and_reply():
    while True:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")
        status, messages = imap.search(None, '(UNSEEN)')
        for num in messages[0].split():
            status, data = imap.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            sender = email.utils.parseaddr(msg["From"])[1]
            subject = msg["Subject"]
            send_auto_reply(sender, f"Re: {subject}", "Thanks for reaching out!")
            imap.store(num, '+FLAGS', '\\Seen')
        imap.logout()
        time.sleep(10)  # check every 10 seconds

def send_auto_reply(to, subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

@app.route("/")
def home():
    return "Auto-reply bot running!"

if __name__ == "__main__":
    Thread(target=check_and_reply, daemon=True).start()
    app.run(debug=True)