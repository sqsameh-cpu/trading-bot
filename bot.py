import yfinance as yf
import requests
import time
import json
import os
from datetime import datetime

# =====================================
# 🔑 Telegram
# =====================================
TOKEN = "8246559774:AAGYTkmrQUx6vDfOUOqqAtbRBPhzMA04kPo"
CHAT_ID = "836106772"

def send(msg):
    url = f"https://api.telegram.org/bot8246559774:AAGYTkmrQUx6vDfOUOqqAtbRBPhzMA04kPo/sendMessage"
    try:
        requests.post(url, data={"chat_id": 836106772, "text": msg}, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

# =====================================
# 🧠 Memory
# =====================================
MEMORY_FILE = "stock_memory.json"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        stock_memory = json.load(f)
else:
    stock_memory = {}

# =====================================
# 🟢 50 سهم (بدون تغيير)
# =====================================
symbols = {
    "2222.SR": "أرامكو",
    "2010.SR": "سابك",
    "2310.SR": "سبكيم",
    "2380.SR": "بترو رابغ",
    "2350.SR": "كيان",
    "2330.SR": "المتقدمة",
    "2320.SR": "البابطين",
    "2110.SR": "الكابلات",
    "4142.SR": "معادن",
    "7010.SR": "STC",
    "7020.SR": "إس تي سي حلول",
    "7203.SR": "علم",
    "4030.SR": "البحري",
    "4040.SR": "سابتكو",
    "4260.SR": "بدجت",
    "1301.SR": "أسمنت السعودية",
    "3020.SR": "أسمنت اليمامة",
    "3030.SR": "أسمنت الشرقية",
    "3091.SR": "أسمنت الجوف",
    "2200.SR": "أنابيب",
    "1320.SR": "أنابيب السعودية",
    "2180.SR": "فيبكو",
    "2150.SR": "زجاج",
    "2060.SR": "التصنيع",
    "4190.SR": "جرير",
    "4002.SR": "المواساة",
    "4191.SR": "المراكز العربية",
    "4192.SR": "الدريس",
    "9521.SR": "إنماء الروابي",
    "9522.SR": "رواسي",
    "9523.SR": "أكوا باور",
    "1182.SR": "أملاك"
}

# =====================================
# 🧠 Liquidity Filter
# =====================================
def liquidity_filter(vr, vt, ch):
    score = 0
    if vr > 2: score += 2
    if vt > 1.1: score += 2
    if abs(ch) < 2.5: score += 2
    if vr > 6: score -= 3
    return score

# =====================================
# 🧠 Market Session
# =====================================
def get_market_session():
    now = datetime.now()
    t = now.hour * 60 + now.minute

    if 570 <= t <= 630:
        return "open_power"
    elif 840 <= t <= 900:
        return "explosion_zone"
    else:
        return "normal"

# =====================================
# 🧠 Analyze Core
# =====================================
def analyze(symbol, name, session):

    df = yf.download(symbol, period="120d", interval="1d", progress=False)

    if df is None or df.empty or len(df) < 60:
        return None

    price = float(df["Close"].iloc[-1])
    volume = float(df["Volume"].iloc[-1])

    avg20 = float(df["Volume"].tail(20).mean())
    avg50 = float(df["Volume"].tail(50).mean())

    vr = volume / avg20
    vt = avg20 / avg50

    old = float(df["Close"].iloc[-5])
    ch = ((price - old) / old) * 100

    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    compression = df["Volume"].tail(20).mean() < df["Volume"].tail(50).mean()
    trend_up = ma20 > ma50

    score = liquidity_filter(vr, vt, ch)

    if session == "open_power":
        if vr > 2: score += 2
        if abs(ch) < 3: score += 1

    elif session == "explosion_zone":
        if vr > 2.5 and vt > 1.2:
            score += 3
        if abs(ch) < 1.5:
            score += 2

    if price > ma20: score += 2
    if price > ma50: score += 2
    if vr > 2.5: score += 2

    # =====================================
    # 🚨 Explosion Logic
    # =====================================
    explosion = False
    early = ""
    timing = 0

    if compression and trend_up and vr > 1.8 and vt > 1.05:
        explosion = True
        early = "💣 انفجار محتمل خلال 1–3 أيام"
        timing = 4

    elif session == "explosion_zone" and vr > 2.2 and vt > 1.2:
        explosion = True
        early = "🚨 انفجار قريب (24–72 ساعة)"
        timing = 3

    elif session == "open_power" and vr > 2:
        early = "🟡 تجميع مبكر"
        timing = 2

    if score < 8:
        return None

    weight = stock_memory.get(symbol, 1.0)
    score = score * weight

    entry = price
    sl = min(ma20, price * 0.97)
    tp1 = price * 1.05
    tp2 = price * 1.12

    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "score": score,
        "vr": vr,
        "vt": vt,
        "ch": ch,
        "ma20": ma20,
        "ma50": ma50,
        "early": early,
        "timing": timing,
        "explosion": explosion,
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2
    }

# =====================================
# 🚀 Scan
# =====================================
def run_scan():

    session = get_market_session()
    results = []

    for s, name in symbols.items():
        try:
            r = analyze(s, name, session)
            if r:
                results.append(r)
        except:
            pass

    results = sorted(results, key=lambda x: x["score"] + x["timing"], reverse=True)
    top3 = results[:3]

    if not top3:
        return

    explosion = top3[0]
    for r in top3:
        if r["explosion"]:
            explosion = r
            break

    for r in top3:
        key = r["symbol"]

        if r.get("explosion"):
            stock_memory[key] = stock_memory.get(key, 1.0) + 0.05
        else:
            stock_memory[key] = stock_memory.get(key, 1.0) - 0.02

        stock_memory[key] = max(0.5, min(stock_memory[key], 2.0))

    with open(MEMORY_FILE, "w") as f:
        json.dump(stock_memory, f)

    msg = "💣 SMART MONEY AI (CLEAN TRADING BOT)\n\n"

    for r in top3:

        mark = "🟡 عادي"
        if r == explosion:
            mark = "⭐ انفجار محتمل"
        elif r["timing"] >= 3:
            mark = "🚨 انفجار قريب"

        msg += f"""
🏢 {r['name']}
💰 {round(r['price'],2)}

📊 السيولة: {round(r['vr'],2)}x
📈 التسارع: {round(r['vt'],2)}x
🔥 القوة: {round(r['score'],2)}

⚡ {r['early']}
{mark}

🎯 دخول: {round(r['entry'],2)}
🛑 وقف: {round(r['sl'],2)}
🚀 TP1: {round(r['tp1'],2)}
💣 TP2: {round(r['tp2'],2)}

-------------------
"""

    send(msg)

# =====================================
# 🔥 تشغيل
# =====================================
send("🟢 Trading Bot Started (NO NEWS MODULE)")

while True:

    now = datetime.now()
    t = now.hour * 60 + now.minute

    if 570 <= t <= 900:
        run_scan()

    time.sleep(300)
