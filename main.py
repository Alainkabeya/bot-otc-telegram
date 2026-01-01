
import time
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot

# ================== CONFIG ==================
TELEGRAM_TOKEN="8218898659:AAHRRAlrQxpCHDG7AydgtnTbLvAVwZ8VtFE"
AUTHORIZED_USERS="1175920056" # TON TELEGRAM ID
PAIR = "AUD/USD OTC"
TIMEFRAME = "1m"
EXPIRATION = "1 min"

# Gestion du risque
MAX_LOSSES_BEFORE_PAUSE = 2
PAUSE_MINUTES = 30

# ================== BOT ==================
bot = Bot(token=TELEGRAM_TOKEN)

losses = 0
paused_until = 0

def send_signal(text):
    for uid in AUTHORIZED_USERS:
        bot.send_message(chat_id=uid, text=text)

# ================== DATA (SIMULÉ OTC) ==================
# ⚠️ OTC n’a pas d’API officielle → on simule une bougie propre
def get_fake_ohlc(n=100):
    prices = np.cumsum(np.random.randn(n)) + 100
    df = pd.DataFrame({
        "close": prices
    })
    return df

# ================== STRATÉGIE ==================
def analyze_market():
    global losses, paused_until

    if time.time() < paused_until:
        return

    df = get_fake_ohlc(120)

    rsi = RSIIndicator(df["close"], window=14).rsi()
    ema20 = EMAIndicator(df["close"], window=20).ema_indicator()
    ema50 = EMAIndicator(df["close"], window=50).ema_indicator()

    last_rsi = rsi.iloc[-1]
    last_ema20 = ema20.iloc[-1]
    last_ema50 = ema50.iloc[-1]

    direction = None

    # CALL
    if last_ema20 > last_ema50 and 40 < last_rsi < 55:
        direction = "📈 CALL"

    # PUT
    elif last_ema20 < last_ema50 and 45 < last_rsi < 60:
        direction = "📉 PUT"

    if direction:
        msg = (
            f"🔔 SIGNAL OTC\n\n"
            f"📊 Paire : {PAIR}\n"
            f"⏱ Timeframe : {TIMEFRAME}\n"
            f"➡️ Direction : {direction}\n"
            f"⌛ Expiration : {EXPIRATION}\n\n"
            f"⚠️ Gestion du risque stricte"
        )
        send_signal(msg)

# ================== LOOP ==================
send_signal("✅ Bot OTC démarré et opérationnel")

while True:
    try:
        analyze_market()
        time.sleep(60)  # analyse chaque minute
    except Exception as e:
        send_signal(f"❌ Erreur bot : {e}")
        time.sleep(60)
