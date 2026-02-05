import os
import requests
from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================= 환경변수 =================
TELEGRAM_TOKEN = os.getenv("8565522116:AAEBRSHfxYs1YwdFHuT8Bd6ocs5QGjKihsg")
CHAT_ID = os.getenv("8579497868")
NEWS_API_KEY = os.getenv("d21c1d0926df4c6e95808b667a2795a7")

# ================= 뉴스 가져오기 =================
def get_news():
    if not NEWS_API_KEY:
        return "❌ NEWS_API_KEY가 설정되지 않았습니다."

    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={d21c1d0926df4c6e95808b667a2795a7}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        # API 자체 오류 체크
        if data.get("status") != "ok":
            return f"뉴스 API 오류: {data}"

        articles = data.get("articles", [])[:5]

        if not articles:
            return "오늘 뉴스가 없습니다."

        news_text = "\n\n".join([f"📰 {a['title']}" for a in articles])
        return news_text

    except Exception as e:
        return f"뉴스 가져오기 오류: {e}"

# ================= 아침 자동 뉴스 =================
async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"☀️ 아침 뉴스입니다!\n\n{news}"
    )

# ================= 텔레그램 명령어 =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 뉴스봇입니다 🤖")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    await update.message.reply_text(news)

# ================= 봇 실행 =================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

# ⏰ 매일 오전 8시 자동 뉴스 (한국시간)
app.job_queue.run_daily(
    morning_news,
    time=time(hour=8, minute=0),
    name="morning_news"
)

print("Bot started...")
app.run_polling()



