import yfinance as yf
import requests
import time

# =====================================
# 🔑 Telegram
# =====================================
TOKEN = "8246559774:AAGYTkmrQUx6vDfOUOqqAtbRBPhzMA04kPo"
CHAT_ID = "836106772"

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
# 🟢 الأسهم
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
# 🔍 فحص ذكي
# =====================================
def run_scan():

    best = None

    for s in symbols:

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

            df = df.dropna()

            price = float(df["Close"].iloc[-1])
            volume = float(df["Volume"].iloc[-1])

            old_price = float(df["Close"].iloc[-5])
            avg_volume = float(df["Volume"].mean())

            volume_ratio = volume / avg_volume
            change_5d = ((price - old_price) / old_price) * 100

            fair = fair_value(price)
            discount_value = ((price - fair) / fair) * 100

            score = 0

            # 📉 نزول قوي
            if change_5d < -7:
                score += 3

            # 📊 سيولة قوية
            if volume_ratio > 2:
                score += 3

            # 💰 خصم قوي
            if discount_value < -15:
                score += 3

            # ⚡ شرط إضافي
            if score >= 7:

                msg = f"""
🚀 فرصة قوية جدًا

🏢 السهم:
{symbols[s]}

💰 السعر:
{round(price,2)}

📊 القيمة العادلة:
{round(fair,2)}

📉 الخصم:
{round(discount_value,2)}%

📈 السيولة:
{round(volume_ratio,2)}x

⚡ الحركة:
{round(change_5d,2)}%

🔥 التقييم:
{score}/10
"""

                # اختيار أفضل سهم فقط
                if best is None or score > best["score"]:
                    best = {"msg": msg, "score": score}

        except Exception as e:
            print("خطأ:", s, e)

    # =====================================
    # 📲 إرسال أفضل فرصة فقط
    # =====================================
    if best:
        send(best["msg"])
    else:
        send("📉 لا توجد فرص قوية جدًا الآن")


# =====================================
# 🚀 تشغيل مرة واحدة (مناسب لـ Railway)
# =====================================
print("🔍 بدء الفحص الذكي...")
send("🟢 تم تشغيل البوت الذكي بنجاح")

run_scan()

print("✅ انتهى الفحص")
