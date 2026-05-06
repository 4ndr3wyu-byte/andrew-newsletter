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
    """본문 정리 강화"""
    if not text or len(text) < 10:
        return "본문 추출 실패"
    
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'#\S+', '', text)                    # 해시태그 제거
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    ad_list = [
        "무단전재", "재배포", "기사제보", "저작권자", "Copyright", "All rights reserved",
        "▶", "☞", "■", "※", "포토=", "자료사진", "관련기사", "이 기사는", 
        "AP 뉴시스", "뉴시스", "연합뉴스", "구독", "클릭", "링크"
    ]
    
    for phrase in ad_list:
        text = text.replace(phrase, "")
    
    return text.strip()


def get_full_content(naver_url):
    try:
        resp = requests.get(naver_url, 
                          headers={"User-Agent": "Mozilla/5.0"}, 
                          timeout=12)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        content = (soup.select_one("article.go_trans._article_content") or 
                   soup.select_one("div#dic_area"))
        
        if content:
            return clean_content(content.get_text(separator="\n", strip=True))
        return "본문 추출 실패"
    except:
        return "본문 로드 실패"


def create_markdown(news_list):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    md = f"# 📨 Andrew Daily Newsletter\n"
    md += f"**{date_str}** — AI • 테슬라 • 애플\n\n"
    md += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, news in enumerate(news_list, 1):
        md += f"**{i}. {news['title']}**\n\n"
        md += f"🔑 키워드: {news['keyword']}\n\n"
        
        content = news['content'][:1050]
        if len(news['content']) > 1050:
            content += "\n\n⋯ (더 보기)"
        
        md += f"{content}\n\n"
        md += f"[🔗 원문 읽기]({news['naver_link']})\n\n"
        md += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    md += f"총 {len(news_list)}개 기사 • 매일 오전 7시 발송"
    return md


def send_to_telegram(md_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": md_text,
        "parse_mode": "Markdown",           # MarkdownV2 → 일반 Markdown으로 변경
        "disable_web_page_preview": True    # 섬네일 방지
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ 텔레그램 전송 완료")
    else:
        print(f"❌ 텔레그램 전송 실패: {response.text}")


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
                
                print(f"✓ {kw} | {title[:65]}...")
                time.sleep(1.7)
                
        except Exception as e:
            print(f"오류: {e}")
    
    markdown_text = create_markdown(all_news)
    
    with open("andrew_newsletter.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    send_to_telegram(markdown_text)
    
    print(f"\n🎉 완료! 총 {len(all_news)}개 기사")