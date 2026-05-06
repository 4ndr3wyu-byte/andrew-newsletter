mport requests
import re
import time
import os
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# ==================== 설정 ====================
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def clean_text(text):
    """텍스트 정리"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def summarize_to_3lines(text):
    """간단한 3줄 요약 (LLM 없이)"""
    if not text or len(text) < 30:
        return text[:150] + "..." if text else "요약 실패"
    
    sentences = re.split(r'[。.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    summary = []
    for sent in sentences[:3]:
        if len("".join(summary)) < 280:
            summary.append(sent)
    
    return ".\n".join(summary) + "." if summary else text[:280] + "..."

def get_full_content(url):
    """본문 가져오기"""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        content = (soup.select_one("article.go_trans._article_content") or 
                   soup.select_one("div#dic_area") or 
                   soup.select_one("div.article_view"))
        
        if content:
            return clean_text(content.get_text())
        return ""
    except:
        return ""

def send_to_telegram(news, index):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    message = f"📨 **Andrew Daily Newsletter**\n"
    message += f"**{date_str}** | AI • 테슬라 • 애플\n\n"
    message += f"**{index}. {news['title']}**\n\n"
    message += f"🔑 {news['keyword']}\n\n"
    
    # 3줄 요약
    summary = summarize_to_3lines(news['content'] or news['description'])
    message += f"{summary}\n\n"
    
    message += f"🔗 [원문 읽기]({news['link']})"
    
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
        print(f"   ❌ {index}번 전송 실패: {response.text}")


# ==================== 메인 ====================
if __name__ == "__main__":
    print("🚀 Andrew Daily Newsletter 크롤러 시작\n")
    
    keywords = ["AI", "테슬라", "애플"]
    all_news = []
    index = 1
    
    for kw in keywords:
        print(f"=== {kw} 뉴스 수집 중 ===")
        enc_query = urllib.parse.quote(kw)
        
        api_url = f"https://openapi.naver.com/v1/search/news.json?query={enc_query}&display=5&sort=date"
        
        try:
            resp = requests.get(api_url, headers={
                "X-Naver-Client-Id": CLIENT_ID,
                "X-Naver-Client-Secret": CLIENT_SECRET
            }, timeout=10)
            
            items = resp.json().get("items", [])
            
            for item in items:
                title = clean_text(item['title'])
                description = clean_text(item.get('description', ''))
                link = item['link']
                
                # 본문 보강
                full_content = get_full_content(link)
                
                news_item = {
                    "keyword": kw,
                    "title": title,
                    "description": description,
                    "content": full_content,
                    "link": link
                }
                
                all_news.append(news_item)
                print(f"✓ {kw} | {title[:60]}...")
                
                time.sleep(1.5)
                
        except Exception as e:
            print(f"   오류 발생: {e}")
    
    # Telegram 전송
    print("\n📤 Telegram 전송 시작...")
    for i, news in enumerate(all_news, 1):
        send_to_telegram(news, i)
        time.sleep(1.3)  # Telegram rate limit 방지
    
    print(f"\n🎉 총 {len(all_news)}개 기사 처리 완료!")