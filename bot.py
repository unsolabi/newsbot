import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

# ---------------- 명령어 ----------------
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 뉴스봇입니다 🤖")

async def news(update, context: ContextTypes.DEFAULT_TYPE):
    news = get_news()
    await update.message.reply_text(news)

# ---------------- 봇 실행 ----------------
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

print("Bot started...")
app.run_polling()




