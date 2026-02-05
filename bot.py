
import os
import requests
import feedparser
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import anthropic

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# 🔹 한국 경제 RSS
RSS_URL = "https://www.mk.co.kr/rss/30000001/"

def get_economy_news():
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:5]
    if not entries:
        return "오늘 경제 뉴스가 없습니다."

    news_list = [f"📰 {e.title}" for e in entries]
    return "\n\n".join(news_list)

def ai_reply(text):
    try:
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": text}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"AI 오류: {e}"

# 🔹 아침 자동 브리핑
async def morning_briefing(context: ContextTypes.DEFAULT_TYPE):
    news = get_economy_news()
    summary = ai_reply(f"다음 뉴스 핵심만 한국어로 요약:\n{news}")
    await context.bot.send_message(chat_id=CHAT_ID, text=f"📊 오늘의 경제 브리핑\n\n{summary}")

# 🔹 시작
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요 🇰🇷 경제 비서 봇입니다!\n무엇이든 물어보세요.")

# 🔹 뉴스 요청 키워드 감지
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if "뉴스" in user_text or "경제" in user_text:
        news = get_economy_news()
        summary = ai_reply(f"다음 뉴스 핵심만 요약:\n{news}")
        await update.message.reply_text(summary)
    else:
        answer = ai_reply(user_text)
        await update.message.reply_text(answer)

# 실행
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.job_queue.run_daily(morning_briefing, time=time(hour=8, minute=0))

print("AI 경제 비서 봇 실행 중...")
app.run_polling()




