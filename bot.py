import os
import requests
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= 환경변수 =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # AI 요약용 (선택)
CHAT_ID = os.getenv("CHAT_ID")

# ================= OpenAI 요약 =================
def summarize_news(text):
    if not OPENAI_API_KEY:
        return text  # 키 없으면 요약 없이 제목 그대로

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "다음 뉴스를 한국어로 짧게 요약해줘."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 120
        }

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )

        result = r.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"(요약 실패)\n{text}"

# ================= 한국 경제 뉴스 =================
def get_economy_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&category=business&apiKey={NEWS_API_KEY}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") != "ok":
            return f"뉴스 API 오류: {data.get('message')}"

        articles = data.get("articles", [])[:5]

        if not articles:
            return "오늘 경제 뉴스가 없습니다."

        news_list = []
        for a in articles:
            title = a["title"]
            source = a["source"]["name"]
            summary = summarize_news(title)

            news_list.append(
                f"📰 {title}\n"
                f"✏️ 요약: {summary}\n"
                f"🔗 출처: {source}"
            )

        return "\n\n".join(news_list)

    except Exception as e:
        return f"뉴스 가져오기 실패: {e}"

# ================= 자동 아침 뉴스 =================
async def morning_news(context: ContextTypes.DEFAULT_TYPE):
    if CHAT_ID:
        news = get_economy_news()
        await context.bot.send_message(chat_id=CHAT_ID, text=f"☀️ 오늘의 한국 경제 뉴스\n\n{news}")

# ================= 명령어 =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요 🇰🇷 경제 뉴스 요약 봇입니다!\n/news 를 입력해보세요.")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = get_economy_news()
    await update.





