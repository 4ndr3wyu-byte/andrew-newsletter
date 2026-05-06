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
    """간단하지만 자연스러운 3줄 요약"""
    if not text:
        return "요약을 가져올 수 없습니다."
    
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    summary = sentences[:3]
    return ".\n".join(summary) + "." if summary else text[:300]

def send_news(news, index):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    # Google Translate 링크 생성
    translate_link = f"https://translate.google.com/translate?sl=en&tl=ko&u={news['url']}"
    
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
    print("🚀 Andrew Global Tech Newsletter 크롤러 시작\n")
    
    # 지난 24시간
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    keywords = ["AI OR Tesla OR Apple OR iPhone OR Mac OR Artificial Intelligence"]
    
    all_news = []
    
    for keyword in keywords:
        print(f"🔍 {keyword} 검색 중...")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": keyword,
            "language": "en",
            "sortBy": "popularity",      # 인기순
            "from": from_date,
            "pageSize": 15,
            "apiKey": NEWSAPI_KEY
        }
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            
            if data.get("status") != "ok":
                print(f"   API 오류: {data.get('message')}")
                continue
            
            for article in data.get("articles", []):
                # 중복 제거
                if not any(a['url'] == article['url'] for a in all_news):
                    all_news.append(article)
                    print(f"✓ {article['source']['name']} | {article['title'][:70]}...")
                    
        except Exception as e:
            print(f"   오류: {e}")
    
    # 상위 12개만 사용 (너무 많지 않게)
    all_news = all_news[:12]
    
    print(f"\n📤 Telegram 전송 시작... (총 {len(all_news)}개)")
    
    for i, news in enumerate(all_news, 1):
        send_news(news, i)
        time.sleep(1.3)
    
    print(f"\n🎉 완료! 총 {len(all_news)}개 글로벌 주요 기사 전송")