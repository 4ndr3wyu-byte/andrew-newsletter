import requests
import json
import time
import urllib.parse
import os
from datetime import datetime

# ==================== GitHub Secrets에서 API 키 불러오기 ====================
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 설정되지 않았습니다!")
    print("GitHub Secrets를 확인해주세요.")
    exit(1)

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}

def search_naver_news_api(keyword, max_articles=5):
    articles = []
    enc_text = urllib.parse.quote(keyword)
    
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display={max_articles}&start=1&sort=date"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            
            print(f"   → API 호출 성공 ({len(items)}개 결과)")
            
            for item in items:
                title = item['title'].replace('&quot;', '"').replace('&apos;', "'").replace('<b>', '').replace('</b>', '')
                description = item.get('description', '').replace('&quot;', '"').replace('&apos;', "'").replace('<b>', '').replace('</b>', '')
                
                articles.append({
                    "keyword": keyword,
                    "title": title,
                    "naver_link": item['link'],
                    "original_link": item.get('originallink', ''),
                    "content": description,           # 네이버 API는 본문 요약 제공
                    "pub_date": item.get('pubDate', ''),
                    "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                print(f"✓ {keyword} | {title[:75]}...")
            
            return articles
            
        else:
            print(f"   ❌ API 오류 ({resp.status_code}): {resp.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ 예외 발생: {e}")
        return []


# ==================== 메인 ====================
if __name__ == "__main__":
    print("🚀 네이버 공식 API 뉴스 크롤러 시작\n")
    
    keywords = ["AI", "테슬라", "애플"]
    all_articles = []
    
    for kw in keywords:
        print(f"=== {kw} 뉴스 수집 중 ===")
        result = search_naver_news_api(kw, max_articles=5)
        all_articles.extend(result)
        time.sleep(0.6)   # API 호출 제한 대비
    
    filename = "naver_news_ai_tesla_apple.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 총 {len(all_articles)}개 기사 수집 완료 → {filename}")