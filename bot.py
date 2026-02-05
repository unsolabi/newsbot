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

SAFE_NEWS_PROMPT = """
당신은 뉴스 요약기입니다.
제공된 기사 내용 안에서만 요약하세요.
추측 금지. 정보 추가 금지.
"""

ASSISTANT_PROMPT = """
당신은 개인 비서입니다.
정확성이 가장 중요합니다.

규칙:
1. 모르면 "확인 필요"라고 말하세요
2. 추측하지 마세요
3. 수치를 말할 때는 불확실하면 단정하지 마세요
4. 뉴스 질문이 아닌 일반 질문도 답변하세요
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
        for entry in feed.entries[:2]:
            articles.append({"title": entry.title, "link": entry.link})
    return articles[:5]

def get_article_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        p


