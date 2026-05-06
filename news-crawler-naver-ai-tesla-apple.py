import requests
import json
import time
import urllib.parse
from datetime import datetime

# ==================== 네이버 API 설정 ====================
# GitHub Secrets에 등록한 값 사용 (강력 추천)
CLIENT_ID = "YOUR_CLIENT_ID"          # ← GitHub Secrets에서 불러올 예정
CLIENT_SECRET = "YOUR_CLIENT_SECRET"  # ← GitHub Secrets에서 불러올 예정

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}

def search_naver_news_api(keyword, max_articles=5):
    """네이버 공식 뉴스 검색 API 사용"""
    articles = []
    enc_text = urllib.parse.quote(keyword)
    
    # sort=date : 최신순, sort=sim : 정확도순
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_text}&display={max_articles}&start=1&sort=date"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            
            for item in items:
                title = item['title'].replace('&quot;', '"').replace('&apos;', "'")
                content = item.get('description', '').replace('&quot;', '"').replace('&apos;', "'")
                
                articles.append({
                    "keyword": keyword,
                    "title": title,
                    "naver_link": item['link'],
                    "original_link": item.get('originallink', ''),
                    "content": content,
                    "pub_date": item.get('pubDate', ''),
                    "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                print(f"✓ {keyword} | {title[:80]}...")
            
            print(f"   → {len(articles)}개 수집 완료")
            return articles
            
        else:
            print(f"   API 오류 ({resp.status_code}): {resp.text}")
            return []
            
    except Exception as e:
        print(f"   예외 발생: {e}")
        return []


# ==================== 메인 실행 ====================
if __name__ == "__main__":
    print("🚀 네이버 공식 API 뉴스 크롤러 시작\n")
    
    keywords = ["AI", "테슬라", "애플"]
    all_articles = []
    
    for kw in keywords:
        print(f"=== {kw} 뉴스 수집 중 ===")
        result = search_naver_news_api(kw, max_articles=5)
        all_articles.extend(result)
        time.sleep(0.5)  # API 호출 간격
    
    # JSON 저장
    filename = "naver_news_ai_tesla_apple.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 총 {len(all_articles)}개 기사 수집 완료 → {filename}")