import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from trader import get_historical_data, get_multitimeframe_trend, place_order
from config import QUANTITY

in_position = False

def run_strategy():
    global in_position
    df = get_historical_data()
    if df.empty or len(df) < 50:
        print("❌ Недостаточно данных для анализа.")
        return

    # === Индикаторы ===
    ema_fast = EMAIndicator(close=df["close"], window=9).ema_indicator()
    ema_slow = EMAIndicator(close=df["close"], window=21).ema_indicator()
    rsi = RSIIndicator(close=df["close"], window=14).rsi()
    macd = MACD(close=df["close"]).macd()
    macd_signal = MACD(close=df["close"]).macd_signal()
    volume_ma = df["volume"].rolling(window=20).mean()
    adx = ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14).adx()
    atr = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14).average_true_range()
    bb = BollingerBands(close=df["close"], window=20)

    df["ema_fast"] = ema_fast
    df["ema_slow"] = ema_slow
    df["rsi"] = rsi
    df["macd"] = macd
    df["macd_signal"] = macd_signal
    df["volume_ma"] = volume_ma
    df["adx"] = adx
    df["atr"] = atr
    df["bb_width"] = bb.bollinger_hband() - bb.bollinger_lband()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # === Мультитаймфреймовый тренд ===
    mtf_trend = get_multitimeframe_trend()  # True, если EMA50 > EMA200 на 1D

    # === Фильтрация флетов ===
    if last["adx"] < 20 or last["bb_width"] < df["bb_width"].rolling(20).mean().iloc[-1]:
        print("🔍 Флетовый рынок — сигналы пропущены")
        return

    # === Лонг сигнал ===
    long_signal = (
        last["ema_fast"] > last["ema_slow"] and
        prev["ema_fast"] < prev["ema_slow"] and
        last["rsi"] < 70 and
        last["macd"] > last["macd_signal"] and
        last["volume"] > last["volume_ma"] and
        mtf_trend
    )

    # === Шорт сигнал ===
    short_signal = (
        last["ema_fast"] < last["ema_slow"] and
        prev["ema_fast"] > prev["ema_slow"] and
        last["rsi"] > 30 and
        last["macd"] < last["macd_signal"] and
        last["volume"] > last["volume_ma"] and
        not mtf_trend
    )

    # === Торговля ===
    if long_signal and not in_position:
        print("📈 Покупка по стратегии EMA+RSI+MACD")
        place_order("BUY", QUANTITY, last["atr"])
        in_position = True

    elif short_signal and in_position:
        print("📉 Продажа по стратегии EMA+RSI+MACD")
        place_order("SELL", QUANTITY, last["atr"])
        in_position = False

    else:
        print("⏳ Нет сигнала. Ждём следующую свечу.")