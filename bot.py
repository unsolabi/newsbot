import os
import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

# ---------------- 뉴스 가져오기 ----------------
def get_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"
    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])[:5]
        news_text = "\n\n".join([f"📰 {a['title']}" for a in articles])
        return news_text if news_text else "오늘 뉴스가 없습니다."
    except Exception as e:
        return f"뉴스 오류: {e}"

# ---------------- 뉴스 요약 (Claude API 사용 가능) ----------------
def summarize(text):
    # 지금은 단순 요약 대신 그대로 전달
    return text

# ---------------- 아침 뉴스 작업 ----------------
def morning_news_job():
    news = get_news()
    summary = summarize(news)
    bot.send_message(chat_id=CHAT_ID, text=f"☀️ 아침 뉴스입니다!\n\n{summary}")

# ---------------- 텔레그램 명령어 ----------------
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 뉴스봇입니다 🤖")

async def news(update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    summary = summarize(news)
    await update.message.reply_text(summary)

# ---------------- 스케줄러 설정 ----------------
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Seoul"))
scheduler.add_job(morning_news_job, "cron", hour=8, minute=0)
scheduler.start()

# ---------------- 봇 실행 ----------------
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

print("Bot started...")
app.run_polling()
