
import os
import requests
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= 환경변수 =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")  # 자동 뉴스 보낼 대상 (선택)

# ================= 한국 뉴스 가져오기 =================
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&apiKey={NEWS_API_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") != "ok":
            return f"뉴스 API 오류: {data.get('message')}"

        articles = data.get("articles", [])[:5]

        if not articles:
            return "오늘 한국 뉴스가 없습니다."

        news_text = "\n\n".join(
            [f"📰 {a['title']} - {a['source']['name']}" for a in articles]
        )

        return news_text

    except Exception as e:
        return f"뉴스 가져오기 실패: {e}"

# ================= 자동 아침 뉴스 =================
async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    if CHAT_ID:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"☀️ 오늘의 한국 뉴스\n\n{news}")

# ================= 텔레그램 명령어 =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 🇰🇷 한국 뉴스봇입니다 🤖\n/news 를 입력해보세요!")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    await update.message.reply_text(news)

# ================= 봇 실행 =================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

# 매일 오전 8시 자동 뉴스 (CHAT_ID 있을 때만 동작)
if CHAT_ID:
    app.job_queue.run_daily(
        morning_news,
        time=time(hour=8, minute=0),
        name="morning_news"
    )

print("🇰🇷 Korean News Bot Started...")
app.run_polling()




