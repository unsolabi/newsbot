import os
import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------- 기본 설정 ----------------
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ---------------- 뉴스 RSS ----------------
RSS_FEEDS = {
    "kr_economy": "https://www.mk.co.kr/rss/30100041/",
    "kr_general": "https://rss.donga.com/total.xml",
    "us_economy": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
}

# ---------------- 기사 본문 가져오기 ----------------
def get_article_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5])
        return text[:1000]
    except:
        return ""

# ---------------- 뉴스 수집 ----------------
def fetch_news():
    articles = []
    for feed_url in RSS_FEEDS.values():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                title = entry.title
                link = entry.link
                content = get_article_text(link)
                articles.append((title, link, content))
        except:
            continue
    return articles[:5]

# ---------------- 요약 (거짓말 방지: 기사 내용만) ----------------
def summarize_article(title, content):
    if not content:
        return f"📰 {title}\n(본문 요약 불가)"
    return f"📰 {title}\n요약: {content[:200]}..."

# ---------------- /news 명령 ----------------
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("뉴스를 수집하는 중입니다...")
    articles = fetch_news()

    if not articles:
        await update.message.reply_text("오늘 주요 뉴스를 가져오지 못했습니다.")
        return

    for title, link, content in articles:
        summary = summarize_article(title, content)
        await update.message.reply_text(f"{summary}\n🔗 {link}")

# ---------------- 일반 대화 (개인비서 모드) ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 날짜/시간 질문
    if "오늘" in text and "날짜" in text:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        await update.message.reply_text(f"오늘 날짜는 {today} 입니다.")
        return

    # 주가 같은 실시간 데이터는 정직하게 불가 안내
    if "주가" in text or "환율" in text:
        await update.message.reply_text(
            "실시간 금융 데이터는 제공할 수 없습니다. 대신 최신 경제 뉴스를 요약해 드릴까요? /news 입력해 주세요."
        )
        return

    # 기본 응답
    await update.message.reply_text("무엇을 도와드릴까요? 뉴스는 /news 입력")

# ---------------- 시작 메시지 ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "안녕하세요 📡 뉴스 브리핑 + 개인비서 봇입니다!\n/news 입력하면 최신 뉴스 요약 제공"
    )

# ---------------- 봇 실행 ----------------
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler(None, chat))  # 모든 일반 대화 처리

print("Bot running...")
app.run_polling()

