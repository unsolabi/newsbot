
import os
import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
당신은 뉴스 요약기입니다.

절대 규칙:
1. 제공된 기사 내용 안에서만 요약하세요.
2. 없는 정보 추가 금지
3. 추측 금지
4. 해석 금지
5. 다른 기사 내용과 섞지 마세요
6. 출처 없는 내용 생성 금지
"""

RSS_FEEDS = [
    "https://www.yna.co.kr/rss/economy.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"
]

def get_articles():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append({
                "title": entry.title,
                "link": entry.link
            })
    return articles[:5]

def get_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:2000]
    except:
        return ""

def summarize_article(text):
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"다음 기사




