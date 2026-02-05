import os
import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
당신은 글로벌 뉴스 브리핑 전용 AI 비서입니다.

규칙:
1. 기사 내용 기반으로만 요약하세요.
2. 추측, 예측, 과장 금지.
3. 시장, 경제, 산업, 국제정세에 중요한 뉴스만 브리핑하세요.
4. 중요하지 않은 뉴스는 제외하세요.
5. 확실하지 않으면 모른다고 답하세요.
"""

# 🌍 글로벌 주요 뉴스 RSS
RSS_FEEDS = [
    "https://www.yna.co.kr/rss/economy.xml",       # 연합뉴스 경제
    "https://feeds.bbci.co.uk/news/world/rss.xml", # BBC World
    "http://rss.cnn.com/rss/edition_world.rss",    # CNN World
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"  # CNBC
]

KEYWORDS = [
    "economy", "market", "stock", "inflation", "interest", "federal",
    "china", "oil", "war", "trade", "semiconductor", "AI", "chip",
    "금리", "환율", "물가", "수출", "반도체", "증시"
]

def is_important(title):
    title_lower = title.lower()
    return any(k.lower() in title_lower for k in KEYWORDS)

def get_articles():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            if is_important(entry.title):
                articles.append({
                    "title": entry.title,
                    "link": entry.link
                })
    return articles[:6]

def get_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:3000]
    except:
        return ""

def summarize_briefing(articles_text):
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"다음 뉴스들을 종합해 오늘의 핵심 브리핑 작성:\n\n{articles_text}"}
            ]
        )
        return response.content[0].text
    except:
        return "브리핑 생성 중 오류가 발생했습니다."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 글로벌 뉴스 브리핑 AI 비서입니다.\n"
        "/brief 입력 → 오늘의 핵심 뉴스 브리핑"
    )

async def brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("오늘의 핵심 뉴스를 분석 중입니다...")

    articles = get_articles()
    if not articles:
        await update.message.reply_text("중요 뉴스가 없습니다.")
        return

    combined_text = ""
    for a in articles:
        content = get_article_text(a["link"])
        combined_text += f"\n제목: {a['title']}\n내용: {content}\n"

    briefing = summarize_briefing(combined_text)
    await update.message.reply_text("📊 오늘의 글로벌 핵심 브리핑\n\n" + briefing)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}]
    )
    await update.message.reply_text(response.content[0].text)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("brief", brief))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()




