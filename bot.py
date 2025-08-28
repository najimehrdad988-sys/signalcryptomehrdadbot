import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("8458321601:AAHwxoNqSQIN_WSQZyC_8IDVFOkZ0c-pEho")
CHAT_ID = os.getenv("8458321601")

SYMBOLS = {
    "BTCUSDT": {"support": 24150, "resistance": 24500},
    "ETHUSDT": {"support": 1750, "resistance": 1800},
    "ADAUSDT": {"support": 0.50, "resistance": 0.55},
    "SOLUSDT": {"support": 35, "resistance": 38},
    "DOGEUSDT": {"support": 0.08, "resistance": 0.085}
}

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url).json()
    return float(response['price'])

def get_klines(symbol, interval="1m", limit=50):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    closes = [float(item[4]) for item in data]  # قیمت بسته شدن
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

        # سیگنال خرید
        if price <= levels["support"] and ema_short > ema_long and rsi < 30:
            send_to_telegram("📊 خرید " + message + " 🚀")
        # سیگنال فروش
        elif price >= levels["resistance"] and ema_short < ema_long and rsi > 70:
            send_to_telegram("📉 فروش " + message + " 🔻")
        # هشدار نوسان شدید
        elif abs(price - closes[-2])/closes[-2] > 0.01:  # تغییر >1%
            send_to_telegram("⚠️ نوسان شدید " + message)

if __name__ == "__main__":
    while True:
        try:
            check_signals()
            time.sleep(60)
        except Exception as e:
            send_to_telegram(f"⚠️ خطا در ربات: {e}")
            time.sleep(60)
