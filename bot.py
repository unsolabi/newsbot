import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= 환경변수 =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ================= 뉴스 가져오기 =================
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        articles = data.get("articles", [])[:5]

        if not articles:
            return "오늘 뉴스가 없습니다."

        news_text = "\n\n".join([f"📰 {a['title']}" for a in articles])
        return news_text
    except Exception as e:
        return f"뉴스 오류: {e}"

# ================= 뉴스 요약 =================
def summarize(text):
    # 나중에 Claude API 붙일 자리
    return text

# ================= 아침 뉴스 자동 전송 =================
async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    summary = summarize(news)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"☀️ 아침 뉴스입니다!\n\n{summary}")

# ================= 텔레그램 명령어 =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 뉴스봇입니다 🤖")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    summary = summarize(news)
    await update.message.reply_text(summary)

# ================= 봇 실행 =================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

# ⏰ 매일 아침 8시 뉴스 전송 (한국시간)
app.job_queue.run_daily(
    morning_news,
    time={"hour": 8, "minute": 0, "second": 0},
    name="morning_news_job"
)

print("Bot started...")
app.run_polling()





