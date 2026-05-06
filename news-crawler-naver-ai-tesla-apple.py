import requests
import json
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

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}

def get_full_content(naver_url):
    """네이버 뉴스 본문 전체 크롤링"""
    try:
        resp = requests.get(naver_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }, timeout=10)
        
        if resp.status_code != 200:
            return "본문 로드 실패"

        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 본문 영역 찾기 (2026년 기준 주요 선택자)
        content = soup.select_one("article.go_trans._article_content") or \
                  soup.select_one("div#dic_area") or \
                  soup.select_one("div.article_body")
        
        if not content:
            return "본문 추출 실패"

        # 불필요한 요소 제거
        for unwanted in content.select("script, style, iframe, .end_ad, .reporter_area, .byline, .ads, .ad_area"):
            unwanted.decompose()
        
        text = content.get_text(separator="\n", strip=True)
        
        # 해시태그 제거 (#단어)
        import re
        text = re.sub(r'#\S+', '', text)
        
        # 광고성 문구 제거 (필요시 더 추가 가능)
        ad_phrases = ["▶", "☞", "무단전재", "재배포 금지", "기사제보", "구독", "링크"]
        for phrase in ad_phrases:
            text = text.replace(phrase, "")
        
        return text.strip()
        
    except Exception as e:
        return f"본문 크롤링 오류: {str(e)}"


def create_markdown(news_list):
    """뉴스레터용 Markdown 생성"""
    date = datetime.now().strftime("%Y년 %m월 %d일")
    
    md = f"# 📧 Andrew Newsletter - {date}\n\n"
    md += f"**오늘의 주요 키워드**: AI • 테슬라 • 애플\n\n"
    md += "---\n\n"
    
    for news in news_list:
        md += f"## {news['title']}\n\n"
        md += f"**키워드**: {news['keyword']} | **출처**: {news.get('press', '네이버뉴스')}\n\n"
        md += f"{news['content'][:1500]}...\n\n"  # 너무 길면 1500자 제한
        md += f"[원문 읽기]({news['naver_link']})\n\n"
        md += "---\n\n"
    
    return md


def send_to_telegram(markdown_text):
    """텔레그램으로 전송"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ 텔레그램 토큰 또는 CHAT_ID가 설정되지 않았습니다.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 너무 길면 분할 전송 (Telegram 제한 4096자)
    if len(markdown_text) > 3800:
        parts = [markdown_text[i:i+3800] for i in range(0, len(markdown_text), 3800)]
        for i, part in enumerate(parts, 1):
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": part, "parse_mode": "Markdown"}
            requests.post(url, json=data)
            time.sleep(1)
    else:
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": markdown_text, "parse_mode": "Markdown"}
        requests.post(url, json=data)
    
    print("✅ 텔레그램으로 전송 완료")
    return True


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
            resp = requests.get(url, headers=HEADERS, timeout=10)
            items = resp.json().get("items", [])
            
            for item in items:
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                naver_link = item['link']
                
                full_content = get_full_content(naver_link)
                
                all_news.append({
                    "keyword": kw,
                    "title": title,
                    "naver_link": naver_link,
                    "content": full_content,
                    "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                print(f"✓ {kw} | {title[:70]}...")
                time.sleep(1.5)  # 본문 크롤링 매너
                
        except Exception as e:
            print(f"   오류: {e}")
    
    # Markdown 생성 및 저장
    markdown_text = create_markdown(all_news)
    with open("andrew_newsletter.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    # 텔레그램 전송
    send_to_telegram(markdown_text)
    
    print(f"\n🎉 작업 완료! 총 {len(all_news)}개 기사")