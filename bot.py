import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ---------------- 뉴스 가져오기 ----------------
def get_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        articles = data.get("articles", [])[:5]
        news_text = "\n\n".join([f"📰 {a['title']}" for a in articles])
        return news_text if news_text else "오늘 뉴스가 없습니다."
    except Exception as e:
        return f"뉴스 오류: {e}"

# ---------------- 텔레그램 명령어 ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 뉴스봇입니다 🤖")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_text = get_news()
    await update.message.reply_text(news_text)

# ---------------- 매일 아침 뉴스 자동 발송 (스케줄러 대체) ----------------
async def morning_news_loop(app):
    while True:
        now = asyncio.get_event_loop().time()

        # 24시간 = 86400초
        await asyncio.sleep(86400)

        try:
            news_text = get_news()
            await app.bot.send_message(chat_id=CHAT_ID, text=f"☀️ 아침 뉴스입니다!\n\n{news_text}")
            print("Morning news sent")
        except Exception as e:
            print("Morning news error:", e)

# ---------------- 봇 실행 ----------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))

    print("Bot started...")

    # 백그라운드 뉴스 루프 시작
    asyncio.create_task(morning_news_loop(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())


