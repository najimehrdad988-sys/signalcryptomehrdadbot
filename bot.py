import requests
import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Environment Variables
TELEGRAM_TOKEN = os.getenv("8458321601:AAHwxoNqSQIN_WSQZyC_8IDVFOkZ0c-pEho")

# لیست کاربران ثبت‌نام شده
users = []

# ارزها و سطوح ساده
SYMBOLS = {
    "BTCUSDT": {"support": 24150, "resistance": 24500},
    "ETHUSDT": {"support": 1750, "resistance": 1800}
}

# ثبت‌نام با /start
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id not in users:
        users.append(chat_id)
    context.bot.send_message(chat_id, "✅ ثبت‌نام شما انجام شد! از این پس سیگنال‌ها را دریافت می‌کنید.")

# ارسال پیام به همه کاربران
def send_to_telegram(message):
    for chat_id in users:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)

# دریافت قیمت
def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url).json()
    return float(response['price'])

# بررسی سیگنال
def check_signals():
    for symbol, levels in SYMBOLS.items():
        price = get_price(symbol)
        message = f"<b>{symbol}</b>\nقیمت فعلی: {price}"
        if price <= levels["support"]:
            send_to_telegram("📊 خرید " + message + " 🚀")
        elif price >= levels["resistance"]:
            send_to_telegram("📉 فروش " + message + " 🔻")

# اجرای ربات
def run_signals():
    while True:
        try:
            check_signals()
            time.sleep(60)
        except Exception as e:
            send_to_telegram(f"⚠️ خطا در ربات: {e}")
            time.sleep(60)

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()

    # اجرای سیگنال‌ها در پس‌زمینه
    import threading
    t = threading.Thread(target=run_signals)
    t.start()

    updater.idle()

if __name__ == "__main__":
    main()
