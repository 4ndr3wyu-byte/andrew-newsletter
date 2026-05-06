import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import json

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Referer": "https://search.naver.com/",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"
    }

def search_naver_news(keyword, max_articles=5):
    articles = []
    page = 1
    
    while len(articles) < max_articles:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}&start={((page-1)*10)+1}"
        
        try:
            resp = requests.get(url, headers=get_headers(), timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 뉴스 아이템 선택 (2026년 기준)
            news_items = soup.select("div.news_wrap.api_ani_send")
            
            for item in news_items:
                if len(articles) >= max_articles:
                    break
                    
                title_tag = item.select_one("a.news_tit")
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                naver_link = title_tag['href']  # n.news.naver.com 링크
                
                # 본문 크롤링
                content = get_article_content(naver_link)
                
                articles.append({
                    "keyword": keyword,
                    "title": title,
                    "naver_link": naver_link,
                    "content": content[:2000] if content else "본문 추출 실패",  # 너무 길면 앞 2000자만
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                print(f"✓ {keyword} - {title[:60]}...")
                
                time.sleep(random.uniform(1.5, 3.0))  # 매너
                
            page += 1
            if page > 5:  # 최대 5페이지까지만 검색
                break
                
        except Exception as e:
            print(f"검색 오류 ({keyword}): {e}")
            break
    
    return articles

def get_article_content(naver_url):
    """네이버 뉴스 본문 페이지에서 기사 본문 추출"""
    try:
        resp = requests.get(naver_url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 2026년 기준 본문 선택자 (가장 안정적인 방법)
        content = soup.select_one("article.go_trans._article_content")
        if content:
            # 불필요한 요소 제거 (광고, 스크립트 등)
            for unwanted in content.select("script, style, iframe, .end_ad, .reporter_area"):
                unwanted.decompose()
            return content.get_text(strip=True)
        
        # 대체 선택자
        content = soup.select_one("div#dic_area") or soup.select_one("div.article_body")
        if content:
            return content.get_text(strip=True)
        
        return "본문 추출 실패 (선택자 변경됨)"
        
    except Exception as e:
        return f"본문 크롤링 오류: {str(e)}"

# ==================== 실행 ====================
if __name__ == "__main__":
    keywords = ["AI", "테슬라", "애플"]
    all_articles = []
    
    for kw in keywords:
        print(f"\n=== {kw} 뉴스 수집 시작 ===")
        result = search_naver_news(kw, max_articles=5)
        all_articles.extend(result)
        time.sleep(random.uniform(2, 4))
    
    # JSON 파일로 저장
    with open("naver_news_ai_tesla_apple.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 총 {len(all_articles)}개 기사 수집 완료! (naver_news_ai_tesla_apple.json)")