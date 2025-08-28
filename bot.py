from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "mehrdad_secret")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{8458321601:AAHwxoNqSQIN_WSQZyC_8IDVFOkZ0c-pEho}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.args.get("secret") != WEBHOOK_SECRET:
        return {"status": "forbidden"}, 403

    data = request.json
    alert_message = data.get("message", "سیگنال جدید!")
    send_to_telegram(f"📊 مهرداد سیگنال:\n{alert_message}")
    return {"status": "ok"}, 200

@app.route("/")
def home():
    return "Mehrdad Signal Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
