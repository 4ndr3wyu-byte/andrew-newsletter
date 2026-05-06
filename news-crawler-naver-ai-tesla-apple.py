import requests
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

def clean_content(text):
    if not text or len(text) < 10:
        return "본문 추출 실패"
    
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    ad_list = ["무단전재", "재배포", "기사제보", "저작권자", "Copyright", "All rights reserved",
               "▶", "☞", "■", "※", "포토=", "자료사진", "관련기사", "이 기사는", 
               "AP 뉴시스", "뉴시스", "연합뉴스", "구독", "클릭"]
    
    for phrase in ad_list:
        text = text.replace(phrase, "")
    
    return text.strip()


def get_full_content(naver_url):
    try:
        resp = requests.get(naver_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        soup = BeautifulSoup(resp.text, 'lxml')
        content = (soup.select_one("article.go_trans._article_content") or 
                   soup.select_one("div#dic_area"))
        if content:
            return clean_content(content.get_text(separator="\n", strip=True))
        return "본문 추출 실패"
    except:
        return "본문 로드 실패"


def send_single_news(news, index):
    """기사 하나를 하나의 메시지로 전송"""
    date_str = datetime.now().strftime("%Y.%m.%d")
    
    message = f"📨 **Andrew Daily Newsletter** - {date_str}\n\n"
    message += f"**{index}. {news['title']}**\n\n"
    message += f"🔑 키워드: {news['keyword']}\n\n"
    
    # 본문 길이 제한 (Telegram 안전하게)
    content = news['content'][:1800]
    if len(news['content']) > 1800:
        content += "\n\n⋯ (원문에서 계속)"
    
    message += f"{content}\n\n"
    message += f"🔗 [원문 읽기]({news['naver_link']})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"   ✅ {index}번 기사 전송 완료")
        return True
    else:
        print(f"   ❌ {index}번 기사 전송 실패: {response.text}")
        # 길이 초과 시 2번으로 나누어 재시도
        if "too long" in response.text:
            send_split_message(message, index)
        return False


def send_split_message(full_message, index):
    """너무 긴 메시지는 2개로 분할"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    mid = len(full_message) // 2
    part1 = full_message[:mid] + "\n\n⋯ (1/2)"
    part2 = "⋯ (2/2)\n\n" + full_message[mid:]
    
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": part1, "parse_mode": "Markdown", "disable_web_page_preview": True})
    time.sleep(1)
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": part2, "parse_mode": "Markdown", "disable_web_page_preview": True})
    print(f"   ✅ {index}번 기사 분할 전송 완료")


# ==================== 메인 ====================
if __name__ == "__main__":
    print("🚀 Andrew Newsletter 크롤러 시작\n")
    
    keywords = ["AI", "테슬라", "애플"]
    all_news = []
    
    for kw in keywords:
        print(f"=== {kw} 수집 중 ===")
        enc_text = urllib.parse.quote(kw)
        url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display=5&start=1&sort=date"
        
        try:
            resp = requests.get(url, headers={
                "X-Naver-Client-Id": CLIENT_ID,
                "X-Naver-Client-Secret": CLIENT_SECRET
            }, timeout=10)
            
            for item in resp.json().get("items", []):
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                naver_link = item['link']
                full_content = get_full_content(naver_link)
                
                all_news.append({
                    "keyword": kw,
                    "title": title,
                    "naver_link": naver_link,
                    "content": full_content
                })
                
                print(f"✓ {kw} | {title[:60]}...")
                time.sleep(1.6)
                
        except Exception as e:
            print(f"오류: {e}")
    
    # 기사 하나씩 Telegram 전송
    print("\n📤 Telegram 전송 시작...")
    for i, news in enumerate(all_news, 1):
        send_single_news(news, i)
        time.sleep(1.2)   # Telegram rate limit 방지
    
    print(f"\n🎉 완료! 총 {len(all_news)}개 기사 처리")