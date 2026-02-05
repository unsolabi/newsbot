import feedparser
import requests
from bs4 import BeautifulSoup
import anthropic
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
import os

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def get_news():
    url = "https://news.google.com/rss/search?q=반도체&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries[:5]:
        try:
            res = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            text = " ".join(p.get_text() for p in soup.find_all("p"))

            articles.append({
                "title": entry.title,
                "link": entry.link,
                "text": text[:2000]
            })
        except:
            continue

    return articles

def summarize_with_claude(article):
    prompt = f"""
    너는 산업 및 투자 분석 비서다.
    아래 뉴스 내용을 읽고 정리해라.

    1. 한 줄 요약
    2. 산업/기술 시사점
    3. 투자 시사점

    기사:
    {article}
    """

    msg = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return msg.content[0].text

def send_to_telegram(text):
    bot.send_message(chat_id=CHAT_ID, text=text[:4000])

def morning_news_job():
    news_list = get_news()

    for article in news_list:
        summary = summarize_with_claude(article["text"])
        message = f"📰 {article['title']}\n{article['link']}\n\n{summary}"
        send_to_telegram(message)

scheduler = BlockingScheduler()
scheduler.add_job(morning_news_job, 'cron', hour=8, minute=0)

print("뉴스봇 실행 중...")
scheduler.start()
