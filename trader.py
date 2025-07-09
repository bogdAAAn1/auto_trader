import pandas as pd
import csv
import os
from datetime import datetime
import requests
from binance.client import Client
from config import API_KEY, API_SECRET, SYMBOL, INTERVAL, BASE_URL, QUANTITY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from ta.trend import EMAIndicator

client = Client(API_KEY, API_SECRET, tld='com')
client.API_URL = BASE_URL

LOG_FILE = "logs/trades.csv"

# 🔔 Telegram уведомления
def send_telegram(text):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print("❌ Telegram error:", e)

# 📋 Логирование сделок
def ensure_log_file():
    os.makedirs("logs", exist_ok=True)
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "side", "price", "quantity", "atr", "stop_loss", "take_profit"])

def log_trade(side, price, quantity, atr, stop_loss, take_profit):
    ensure_log_file()
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            side,
            f"{price:.2f}",
            quantity,
            f"{atr:.4f}" if atr else "",
            f"{stop_loss:.2f}" if stop_loss else "",
            f"{take_profit:.2f}" if take_profit else ""
        ])

# 📈 Получение исторических данных
def get_historical_data(limit=100):
    try:
        klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=limit)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        return df
    except Exception as e:
        print("❌ Ошибка получения данных:", e)
        send_telegram(f"❌ Ошибка получения данных: {e}")
        return pd.DataFrame()

# 📊 Анализ старшего таймфрейма (1D)
def get_multitimeframe_trend():
    try:
        klines = client.get_klines(symbol=SYMBOL, interval="1d", limit=200)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = df["close"].astype(float)

        ema50 = EMAIndicator(close=df["close"], window=50).ema_indicator().iloc[-1]
        ema200 = EMAIndicator(close=df["close"], window=200).ema_indicator().iloc[-1]

        return ema50 > ema200
    except Exception as e:
        print("❌ Ошибка получения тренда на 1D:", e)
        send_telegram(f"❌ Ошибка тренда 1D: {e}")
        return False

# 📤 Размещение ордера
def place_order(side, quantity, atr=None):
    try:
        order = client.create_order(
            symbol=SYMBOL,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        price = float(order['fills'][0]['price'])
        stop, tp = None, None

        if atr:
            if side == "BUY":
                stop = price - 2 * atr
                tp = price + 3 * atr
            else:
                stop = price + 2 * atr
                tp = price - 3 * atr

        log_trade(side, price, quantity, atr, stop, tp)

        msg = f"✅ Сделка: {side}\nЦена: {price:.2f}\nОбъём: {quantity}\nStop: {stop:.2f if stop else '-'} | TP: {tp:.2f if tp else '-'}"
        print(msg)
        send_telegram(msg)

        return order
    except Exception as e:
        print("❌ Ошибка ордера:", e)
        send_telegram(f"❌ Ошибка ордера: {e}")
