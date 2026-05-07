import requests
import re
import time
import os
from datetime import datetime, timedelta

# ==================== 설정 ====================
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def summarize_3lines(text):
    if not text:
        return "요약 정보가 없습니다."
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    summary = sentences[:3]
    return ".\n".join(summary) + "." if summary else text[:280]

def get_translate_link(url):
    """Google Translate + DeepL fallback"""
    if not url:
        return url
    # Google Translate (가장 안정적)
    google_link = f"https://translate.google.com/translate?sl=en&tl=ko&u={requests.utils.quote(url)}"
    return google_link

def send_news(news, index):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    translate_link = get_translate_link(news['url'])
    
    message = f"📨 **Andrew Daily Newsletter**\n"
    message += f"**{date_str}** — 글로벌 테크 브리핑\n\n"
    message += f"**{index}. {news['title']}**\n\n"
    message += f"🔑 {news['source']['name']}\n\n"
    
    summary = summarize_3lines(news.get('description') or news.get('content', ''))
    message += f"{summary}\n\n"
    message += f"🔗 [한국어로 번역해서 읽기]({translate_link})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"   ✅ {index}번 전송 완료")
    else:
        print(f"   ❌ {index}번 전송 실패")


# ==================== 메인 ====================
if __name__ == "__main__":
    print("🚀 Andrew Global Tech Newsletter 시작\n")
    
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "AI OR Tesla OR Apple OR iPhone OR Mac OR OpenAI OR Artificial Intelligence",
        "language": "en",
        "sortBy": "popularity",
        "from": from_date,
        "pageSize": 12,
        "apiKey": NEWSAPI_KEY
    }
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        
        if data.get("status") != "ok":
            print(f"API 오류: {data.get('message')}")
            exit(1)
        
        articles = data.get("articles", [])[:12]
        
        print(f"\n📤 Telegram 전송 시작... (총 {len(articles)}개)")
        
        for i, article in enumerate(articles, 1):
            send_news(article, i)
            time.sleep(1.3)
            
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print(f"\n🎉 완료!")