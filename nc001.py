import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent

ua = UserAgent()

def crawl_naver_news(keyword, max_pages=3):
    results = []
    
    for page in range(1, max_pages + 1):
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}&start={((page-1)*10)+1}"
        
        headers = {
            "User-Agent": ua.random,
            "Referer": "https://www.naver.com/"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'lxml')
            
            # 뉴스 항목들
            news_items = soup.select("div.news_wrap.api_ani_send")
            
            for item in news_items:
                title_tag = item.select_one("a.news_tit")
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                press = item.select_one("a.info.press").get_text(strip=True) if item.select_one("a.info.press") else "알 수 없음"
                
                results.append({
                    "title": title,
                    "link": link,
                    "press": press
                })
            
            print(f"페이지 {page} 완료: {len(news_items)}개 수집")
            
            # 매너 지키기 (중요!)
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"오류: {e}")
            break
    
    return results

# 사용 예시
if __name__ == "__main__":
    news = crawl_naver_news("인공지능", max_pages=2)
    for item in news[:5]:
        print(item)