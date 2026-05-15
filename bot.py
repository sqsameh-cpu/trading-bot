import yfinance as yf
import requests
import time

# =====================================
# 🔑 Telegram
# =====================================
TOKEN = "PUT_YOUR_TOKEN_HERE"
CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"

# =====================================
# 📲 إرسال رسالة
# =====================================
def send(msg):

    url = f"https://api.telegram.org/bot8246559774:AAGYTkmrQUx6vDfOUOqqAtbRBPhzMA04kPo/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": 836106772,
                "text": msg
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram Error:", e)


# =====================================
# 🟢 أسهم شرعية
# =====================================
symbols = {
    "2320.SR": "البابطين",
    "1120.SR": "الراجحي",
    "7010.SR": "STC",
    "1211.SR": "معادن",
    "2010.SR": "سابك"
}

# =====================================
# 💰 القيمة العادلة
# =====================================
def fair_value(price):

    growth = 0.08
    discount = 0.10
    years = 5

    future = price * ((1 + growth) ** years)

    fair = future / ((1 + discount) ** years)

    return fair

# =====================================
# 🔍 فحص السوق
# =====================================
def run_scan():

    results = []
    sent = set()

    for s in symbols:

        print("فحص:", s)

        try:

            df = yf.download(
                s,
                period="30d",
                interval="1d",
                progress=False,
                threads=True
            )

            if df is None or df.empty or len(df) < 20:
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]

            price = float(last["Close"])

            volume_ratio = (
                float(last["Volume"])
                / float(df["Volume"].mean())
            )

            old_price = float(df["Close"].iloc[-5])

            change_5d = (
                (price - old_price)
                / old_price
            ) * 100

            fair = fair_value(price)

            discount_value = (
                (price - fair)
                / fair
            ) * 100

            score = 0

            # 📉 نزول
            if change_5d < -5:
                score += 3

            # 📊 سيولة
            if volume_ratio > 1.5:
                score += 3

            # 💰 أقل من القيمة العادلة
            if discount_value < -10:
                score += 2

            if score >= 5 and s not in sent:

                msg = f"""
💎 فرصة شرعية

🏢 السهم:
{symbols[s]}

💰 السعر:
{round(price,2)}

📊 القيمة العادلة:
{round(fair,2)}

📉 الفرق:
{round(discount_value,2)}%

📈 السيولة:
{round(volume_ratio,2)}x

⭐ التقييم:
{score}/10
"""

                results.append(msg)
                sent.add(s)

        except Exception as e:

            print("خطأ:", s, e)

    # =====================================
    # 📲 إرسال النتائج
    # =====================================
    if results:

        final_msg = "📊 أفضل الفرص اليوم:\n\n"
        final_msg += "\n\n".join(results[:3])

        send(final_msg)

    else:

        send("📉 لا توجد فرص قوية اليوم")

# =====================================
# 🚀 تشغيل البوت
# =====================================
send("🟢 تم تشغيل البوت بنجاح")

while True:

    print("🔍 بدء الفحص...")

    run_scan()

    print("⏳ انتظار ساعة...")

    time.sleep(3600)
