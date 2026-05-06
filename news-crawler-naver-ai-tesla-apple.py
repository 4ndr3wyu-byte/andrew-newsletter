import requests
import json
import time
import os
import re
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
    if not text:
        return "본문 추출 실패"
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 해시태그 제거
    text = re.sub(r'#\S+', '', text)
    
    # 광고/불필요 문구 대량 제거
    ad_phrases = [
        "무단전재", "재배포", "기사제보", "구독", "클릭", "링크", "▶", "☞", "■", "※", 
        "저작권자", "Copyright", "All rights reserved", "사진=", "포토=", "자료사진",
        "관련기사", "이 기사는", "뉴시스", "연합뉴스", "동아일보", "조선일보"
    ]
    
    for phrase in ad_phrases:
        text = text.replace(phrase, "")
    
    # 여러 개의 빈 줄 정리
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()


def get_full_content(naver_url):
    try:
        resp = requests.get(naver_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }, timeout=12)
        
        soup = BeautifulSoup(resp.text, 'lxml')
        content = (soup.select_one("article.go_trans._article_content") or 
                   soup.select_one("div#dic_area") or 
                   soup.select_one("div.article_body"))
        
        if content:
            text = content.get_text(separator="\n", strip=True)
            return clean_content(text)
        return "본문 추출 실패"
    except:
        return "본문 로드 실패"


def create_markdown(news_list):
    date_str = datetime.now().strftime("%Y년 %m월 %d일")
    
    md = f"# 📨 Andrew Daily Newsletter\n"
    md += f"**{date_str}** | AI • 테슬라 • 애플\n\n"
    md += "---\n\n"
    
    for i, news in enumerate(news_list, 1):
        md += f"### {i}. {news['title']}\n\n"
        md += f"**🔑 키워드**: {news['keyword']}  \n"
        md += f"**🕒 발행**: {news.get('pub_date', '최근')}\n\n"
        
        # 본문 1200자 정도로 제한 (텔레그램 가독성 위해)
        content = news['content'][:1200]
        if len(news['content']) > 1200:
            content += "\n\n... (계속)"
        
        md += f"{content}\n\n"
        md += f"[🔗 원문 보기]({news['naver_link']})\n\n"
        md += "---\n\n"
    
    md += f"\n**총 {len(news_list)}개 기사 요약**\n"
    md += "Andrew Newsletter • 매일 오전 7시 발송"
    
    return md


def send_to_telegram(md_text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ 텔레그램 설정 없음")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 4000자 이상이면 분할 전송
    max_length = 3800
    if len(md_text) > max_length:
        parts = [md_text[i:i+max_length] for i in range(0, len(md_text), max_length)]
        for idx, part in enumerate(parts, 1):
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": part,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data)
            time.sleep(1.5)
        print(f"✅ 텔레그램 분할 전송 완료 ({len(parts)}개)")
    else:
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": md_text, "parse_mode": "Markdown"}
        requests.post(url, json=data)
        print("✅ 텔레그램 전송 완료")


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
                    "content": full_content,
                    "pub_date": item.get('pubDate', '')
                })
                
                print(f"✓ {kw} | {title[:60]}...")
                time.sleep(1.8)
                
        except Exception as e:
            print(f"   오류: {e}")
    
    # Markdown 생성 & 저장
    markdown_text = create_markdown(all_news)
    with open("andrew_newsletter.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    # 텔레그램 전송
    send_to_telegram(markdown_text)
    
    print(f"\n🎉 작업 완료! 총 {len(all_news)}개 기사 처리")