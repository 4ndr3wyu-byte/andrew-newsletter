import requests
from bs4 import BeautifulSoup
import time
import random
import json
from fake_useragent import UserAgent

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Referer": "https://www.naver.com/",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    }

def search_naver_news(keyword, max_articles=5, max_retries=3):
    articles = []
    page = 1
    
    while len(articles) < max_articles and page <= 5:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}&start={((page-1)*10)+1}"
        
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=get_headers(), timeout=15)
                
                if resp.status_code == 403:
                    print(f"  403 차단됨 → {attempt+1}회 재시도")
                    time.sleep(random.uniform(5, 8))
                    continue
                    
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'lxml')
                
                news_items = soup.select("div.news_wrap.api_ani_send")
                
                for item in news_items:
                    if len(articles) >= max_articles:
                        break
                        
                    title_tag = item.select_one("a.news_tit")
                    if not title_tag:
                        continue
                        
                    title = title_tag.get_text(strip=True)
                    naver_link = title_tag['href']
                    
                    content = get_article_content(naver_link)
                    
                    articles.append({
                        "keyword": keyword,
                        "title": title,
                        "naver_link": naver_link,
                        "content": content[:3000] if content else "본문 추출 실패",
                        "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    print(f"✓ {keyword} | {title[:70]}...")
                    time.sleep(random.uniform(2, 4))  # 더 길게
                
                break  # 성공하면 다음 페이지
                
            except Exception as e:
                print(f"  오류 ({keyword} 페이지 {page}): {e}")
                time.sleep(random.uniform(3, 6))
        
        page += 1
        time.sleep(random.uniform(3, 6))
    
    return articles

def get_article_content(naver_url):
    try:
        resp = requests.get(naver_url, headers=get_headers(), timeout=12)
        if resp.status_code != 200:
            return f"본문 요청 실패 ({resp.status_code})"
        
        soup = BeautifulSoup(resp.text, 'lxml')
        
        content = (soup.select_one("article.go_trans._article_content") or 
                   soup.select_one("div#dic_area") or 
                   soup.select_one("div.article_body"))
        
        if content:
            for bad in content.select("script, style, iframe, .end_ad, .reporter_area, .byline"):
                bad.decompose()
            return content.get_text(strip=True, separator="\n")
        
        return "본문 선택자 실패"
        
    except Exception as e:
        return f"본문 오류: {str(e)}"

# ==================== 실행 ====================
if __name__ == "__main__":
    keywords = ["AI", "테슬라", "애플"]
    all_articles = []
    
    print("🚀 네이버 뉴스 크롤러 시작 (GitHub Actions용)\n")
    
    for kw in keywords:
        print(f"=== {kw} 뉴스 수집 시작 ===")
        result = search_naver_news(kw, max_articles=5)
        all_articles.extend(result)
        time.sleep(random.uniform(5, 10))
    
    filename = "naver_news_ai_tesla_apple.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 완료! 총 {len(all_articles)}개 기사 → {filename}")