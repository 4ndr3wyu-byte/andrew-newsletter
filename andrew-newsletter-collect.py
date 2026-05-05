import os
import json
import re
import time
import requests
import feedparser
from datetime import datetime

# ── 환경 변수 ──────────────────────────────────────────

GEMINI_KEY = os.environ[“NEWSLETTER_GEMINI_KEY”]

# ── 10개 소스 RSS ──────────────────────────────────────

SOURCES = {
“Reuters”:        “https://feeds.reuters.com/reuters/topNews”,
“Bloomberg”:      “https://news.google.com/rss/search?q=bloomberg+markets+economy&hl=en-US&gl=US&ceid=US:en”,
“Financial Times”:“https://news.google.com/rss/search?q=financial+times+economy+markets&hl=en-US&gl=US&ceid=US:en”,
“The Verge”:      “https://www.theverge.com/rss/index.xml”,
“TechCrunch”:     “https://techcrunch.com/feed/”,
“Ars Technica”:   “https://feeds.arstechnica.com/arstechnica/index”,
“Electrek”:       “https://electrek.co/feed/”,
“Teslarati”:      “https://www.teslarati.com/feed/”,
“MacRumors”:      “https://feeds.macrumors.com/MacRumors-All”,
“9to5Mac”:        “https://9to5mac.com/feed/”
}

TOP_N = 5  # 소스별 수집 기사 수

def clean_html(text: str) -> str:
return re.sub(r”<[^>]+>”, “”, text or “”).strip()

# ── RSS 수집 ───────────────────────────────────────────

def fetch_articles() -> list:
all_articles = []
for source, url in SOURCES.items():
try:
feed = feedparser.parse(url, request_headers={“User-Agent”: “Mozilla/5.0”})
count = 0
for entry in feed.entries:
if count >= TOP_N:
break
title = clean_html(entry.get(“title”, “”))
link  = entry.get(“link”, “”)
desc  = clean_html(entry.get(“summary”, entry.get(“description”, “”)))
if not title or not link:
continue
all_articles.append({
“id”:          f”{source.lower().replace(’ ‘, ‘*’).replace(’.’, ‘’)}*{count}”,
“source”:      source,
“title”:       title,
“link”:        link,
“description”: desc[:600],
“summary_ko”:  “”
})
count += 1
print(f”✅ {source}: {count}개”)
except Exception as e:
print(f”❌ {source}: {e}”)
return all_articles

# ── Gemini REST 호출 ───────────────────────────────────

def call_gemini(prompt: str) -> str | None:
url = (
“https://generativelanguage.googleapis.com/v1beta/”
f”models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}”
)
body = {
“contents”: [{“parts”: [{“text”: prompt}]}],
“generationConfig”: {“temperature”: 0.3, “maxOutputTokens”: 300}
}
for attempt in range(3):
try:
resp = requests.post(url, json=body, timeout=30)
if resp.status_code == 429:
wait = 30 * (attempt + 1)
print(f”  Rate limit → {wait}초 대기…”)
time.sleep(wait)
continue
resp.raise_for_status()
return resp.json()[“candidates”][0][“content”][“parts”][0][“text”].strip()
except Exception as e:
print(f”  Gemini 오류: {e}”)
return None
return None

# ── 3줄 요약 생성 ──────────────────────────────────────

def generate_summary(article: dict) -> str:
prompt = f””“다음 영문 기사를 한국어 3줄로 요약해줘.

규칙:

- 정확히 3줄만 작성
- 각 줄은 핵심 내용 1가지
- 번호·기호 없이 줄바꿈으로만 구분
- 자연스러운 한국어

제목: {article[‘title’]}
내용: {article[‘description’]}”””

```
result = call_gemini(prompt)
return result if result else "요약을 생성할 수 없습니다."
```

# ── 메인 ───────────────────────────────────────────────

def main():
print(”=” * 50)
print(“📰 Andrew Newsletter — 수집 시작”)
print(”=” * 50)

```
articles = fetch_articles()
print(f"\n총 {len(articles)}개 수집")

print("\n🤖 한국어 요약 생성 중...")
for i, article in enumerate(articles):
    print(f"  [{i+1:2d}/{len(articles)}] {article['source']}: {article['title'][:45]}...")
    article["summary_ko"] = generate_summary(article)
    time.sleep(2)  # Rate limit 방지

data = {
    "generated_at": datetime.now().isoformat(),
    "date":         datetime.now().strftime("%Y년 %m월 %d일"),
    "total":        len(articles),
    "articles":     articles
}

output = "andrew-newsletter-news.json"
with open(output, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ {output} 저장 완료 ({len(articles)}개)")
print("=" * 50)
```

if **name** == “**main**”:
main()