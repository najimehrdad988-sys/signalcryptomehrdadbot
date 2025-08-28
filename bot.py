import requests
import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# مراحل ثبت نام
NAME, PHONE = range(2)
users = {}  # ذخیره کاربران ثبت‌نام شده

# ارزها و سطوح
SYMBOLS = {
    "BTCUSDT": {"support": 24150, "resistance": 24500},
    "ETHUSDT": {"support": 1750, "resistance": 1800},
    "ADAUSDT": {"support": 0.50, "resistance": 0.55},
    "SOLUSDT": {"support": 35, "resistance": 38},
    "DOGEUSDT": {"support": 0.08, "resistance": 0.085}
}

# ثبت نام
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! لطفا نام و نام خانوادگی خودت را وارد کن:")
    return NAME

def get_name(update: Update, context: CallbackContext):
    users[update.message.chat_id] = {"name": update.message.text}
    update.message.reply_text("خیلی خوب! حالا شماره تماس خودت را وارد کن:")
    return PHONE

def get_phone(update: Update, context: CallbackContext):
    users[update.message.chat_id]["phone"] = update.message.text
    update.message.reply_text("✅ ثبت نام با موفقیت انجام شد! حالا سیگنال‌ها را دریافت می‌کنی.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ ثبت نام لغو شد.")
    return ConversationHandler.END

# توابع سیگنال
def send_to_telegram(message):
    for chat_id in users.keys():  # فقط به کاربران ثبت‌نام شده
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url).json()
    return float(response['price'])

def get_klines(symbol, interval="1m", limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    closes = [float(item[4]) for item in data]
    return closes

def EMA(prices, period):
    ema_values = []
    k = 2 / (period + 1)
    for i, price in enumerate(prices):
        if i == 0:
            ema_values.append(price)
        else:
            ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values[-1]

def RSI(prices, period=14):
    gains, losses = 0, 0
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / period
    avg_loss = losses / period if losses != 0 else 0.0001
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def check_signals():
    for symbol, levels in SYMBOLS.items():
        price = get_price(symbol)
        closes = get_klines(symbol)
        ema_short = EMA(closes, 7)
        ema_long = EMA(closes, 25)
        rsi = RSI(closes)
        message = f"<b>{symbol}</b>\nقیمت فعلی: {price}\nEMA7: {ema_short:.2f}, EMA25: {ema_long:.2f}\nRSI: {rsi:.2f}"

        if price <= levels["support"] and ema_short > ema_long and rsi < 30:
            send_to_telegram("📊 خرید " + message + " 🚀")
        elif price >= levels["resistance"] and ema_short < ema_long and rsi > 70:
            send_to_telegram("📉 فروش " + message + " 🔻")
        elif abs(price - closes[-2])/closes[-2] > 0.01:
            send_to_telegram("⚠️ نوسان شدید " + message)

def run_signals(updater):
    while True:
        try:
            check_signals()
            time.sleep(60)
        except Exception as e:
            send_to_telegram(f"⚠️ خطا در ربات: {e}")
            time.sleep(60)

def main():
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()

    # اجرای سیگنال‌ها در پس‌زمینه
    import threading
    t = threading.Thread(target=run_signals, args=(updater,))
    t.start()

    updater.idle()

if __name__ == '__main__':
    main()
