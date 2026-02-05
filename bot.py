import os
import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- 설정 ----------------
logging.basicConfig(level=logging.INFO)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ---------------- RSS 뉴스 소스 ----------------
RSS_FEEDS = [
    "https://www.mk.co.kr/rss/30100041/",   # 한국 경제
    "https://rss.donga.com/total.xml",     # 한국 종합
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",  # 미국 경제
    "http://feeds.bbci.co.uk/news/world/rss.xml",     # 세계 뉴스
]

# ---------------- 기사 본문 일부 가져오기 ----------------
def get_article_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5])
        return text[:800]
    except:
        return ""

# ---------------- 뉴스 수집 ----------------
def fetch_news():
    articles = []
    for feed_url in RSS_FEEDS:
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

# ---------------- 뉴스 요약 ----------------
def summarize(title, content):
    if not content:
        return f"📰 {title}\n(본문 요약 불가)"
    return f"📰 {title}\n요약: {content[:200]}..."

# ---------------- /news ----------------
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("뉴스 수집 중...")
    articles = fetch_news()

    if not articles:
        await update.message.reply_text("오늘 주요 뉴스를 가져오지 못했습니다.")
        return

    for title, link, content in articles:
        summary = summarize(title, content)
        await update.message.reply_text(f"{summary}\n🔗 {link}")

# ---------------- 개인비서 대화 ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "날짜" in text:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        await update.message.reply_text(f"오늘 날짜는 {today} 입니다.")
        return

    if "주가" in text or "환율" in text:
        await update.message.reply_text(
            "실시간 금융 데이터는 제공할 수 없습니다. 대신 최신 경제 뉴스 요약은 /news 입력"
        )
        return

    await update.message.reply_text("도움이 필요하시면 /news 입력해 주세요.")

# ---------------- 시작 ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "안녕하세요 📡 뉴스 브리핑 + 개인비서 봇입니다!\n/news 입력하면 최신 뉴스 제공"
    )

# ---------------- 실행 ----------------
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", news))

# ✅ 일반 대화는 MessageHandler로 처리해야 함
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Bot running...")
app.run_polling()
