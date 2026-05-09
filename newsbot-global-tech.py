import requests
import re
import time
import os
from datetime import datetime, timedelta

# ==================== 설정 ====================
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def groq_summary(text):
    """Groq LLM을 사용한 자연스러운 3줄 요약"""
    if not text or len(text) < 50:
        return clean_text(text)[:280]
    
    prompt = f"""
아래 뉴스 기사를 한국어로 자연스럽고 읽기 쉽게 **정확히 3줄**로 요약해줘.
기술적 용어는 적절히 유지하고, 불필요한 수식어는 빼줘.

기사: {text[:1500]}
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",        # 빠르고 품질 좋은 모델
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            return summary
        else:
            print(f"Groq API 오류: {response.status_code}")
            return clean_text(text)[:280]
    except:
        return clean_text(text)[:280]

def get_translate_link(url):
    if not url:
        return ""
    return f"https://translate.google.com/translate?sl=en&tl=ko&u={requests.utils.quote(url)}"

def send_news(news, index):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    translate_link = get_translate_link(news['url'])
    
    message = f"📨 **Andrew Daily Newsletter**\n"
    message += f"**{date_str}** — 글로벌 테크 브리핑\n\n"
    message += f"**{index}. {news['title']}**\n\n"
    message += f"🔑 {news['source']['name']}\n\n"
    
    # Groq으로 고품질 요약
    summary = groq_summary(news.get('description') or news.get('content', ''))
    message += f"{summary}\n\n"
    message += f"🔗 [Google Translate로 한국어로 읽기]({translate_link})"
    
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
    print("🚀 Andrew Daily Newsletter (Groq LLM) 시작\n")
    
    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "AI OR Tesla OR Apple OR OpenAI OR iPhone OR Mac",
        "language": "en",
        "sortBy": "popularity",
        "from": from_date,
        "pageSize": 12,
        "apiKey": NEWSAPI_KEY
    }
    
    try:
        resp = requests.get(url, params=params, timeout=20)
        data = resp.json()
        
        if data.get("status") != "ok":
            print(f"NewsAPI 오류: {data.get('message')}")
            exit(1)
        
        articles = data.get("articles", [])[:12]
        
        print(f"\n📤 Telegram 전송 시작... (총 {len(articles)}개)")
        
        for i, article in enumerate(articles, 1):
            send_news(article, i)
            time.sleep(2.0)  # Groq 호출 간격
            
    except Exception as e:
        print(f"오류 발생: {e}")
    
    print(f"\n🎉 Groq LLM 버전 완료!")