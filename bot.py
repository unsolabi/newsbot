
import os
import requests
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

def summarize_news(text):
    if not OPENAI_API_KEY:
        return text
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "다음 뉴스를 한국어로 한 줄로 요약해줘."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 80
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=20)
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return text

def get_economy_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&category=business&apiKey={NEWS_API_KEY}"
    r = requests.get(url, timeout=10)
    data = r.json()

    if data.get("status") != "ok":
        return "뉴스를 가져오지 못했습니다."

    articles = data.get("articles", [])[:5]
    if not articles:
        return "오늘 경제 뉴스가 없습니다."

    result = []
    for a in articles:
        title = a["title"]
        source = a["source"]["name"]
        summary = summarize_news(title)
        result.append(f"📰 {title}\n✏️ 요약: {summary}\n🔗 {source}")

    return "\n\n".join(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요 🇰🇷 경제 뉴스 요약 봇입니다!\n/news 를 입력해보세요.")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_economy_news())

async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        await context.bot.send_message(chat_id=CHAT_ID, text="☀️ 오늘의 한국 경제 뉴스\n\n" + get_economy_news())

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

if CHAT_ID:
    app.job_queue.run_daily(morning_news, time=time(hour=8, minute=0))

print("🇰🇷 경제 뉴스 봇 실행 중")
app.run_polling()




