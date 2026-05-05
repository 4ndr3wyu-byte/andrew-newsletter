import os
import json
import time
import requests
from collections import defaultdict

# ── 환경 변수 ──────────────────────────────────────────

TOKEN   = os.environ[“NEWSLETTER_TOKEN”]
CHAT_ID = os.environ[“NEWSLETTER_CHAT_ID”]

SOURCE_ICONS = {
“Reuters”:         “🔴”,
“Bloomberg”:       “🟣”,
“Financial Times”: “🟡”,
“The Verge”:       “🔵”,
“TechCrunch”:      “🟢”,
“Ars Technica”:    “🟠”,
“Electrek”:        “⚡”,
“Teslarati”:       “🚗”,
“MacRumors”:       “🍎”,
“9to5Mac”:         “📱”
}

# ── 텔레그램 전송 ──────────────────────────────────────

def send(text: str):
url  = f”https://api.telegram.org/bot{TOKEN}/sendMessage”
data = {
“chat_id”:               CHAT_ID,
“text”:                  text,
“parse_mode”:            “HTML”,
“disable_web_page_preview”: True
}
try:
resp = requests.post(url, json=data, timeout=30)
resp.raise_for_status()
except Exception as e:
print(f”  전송 실패: {e}”)
time.sleep(1.5)  # Telegram rate limit 방지

# ── 메인 ───────────────────────────────────────────────

def main():
print(”=” * 50)
print(“📬 Andrew Newsletter — 텔레그램 전송 시작”)
print(”=” * 50)

```
with open("andrew-newsletter-news.json", "r", encoding="utf-8") as f:
    data = json.load(f)

articles = data["articles"]
date     = data["date"]
total    = data["total"]

# ── 헤더 메시지 ────────────────────────────────────
send(
    f"📰 <b>오늘의 뉴스 다이제스트</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"📅 {date}\n"
    f"📊 총 {total}개 기사  |  10개 소스\n"
    f"━━━━━━━━━━━━━━━━━━━━"
)

# ── 소스별 그룹화 ──────────────────────────────────
grouped = defaultdict(list)
for a in articles:
    grouped[a["source"]].append(a)

# ── 소스별 메시지 전송 ─────────────────────────────
for source, items in grouped.items():
    icon = SOURCE_ICONS.get(source, "📰")
    msg  = f"{icon} <b>{source}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, a in enumerate(items, 1):
        msg += f"<b>{i}. {a['title']}</b>\n"
        msg += f"{a['summary_ko']}\n"
        msg += f"🔗 <a href='{a['link']}'>원문 보기</a>\n\n"

    send(msg)
    print(f"✅ {source} 전송 완료")

print("\n🎉 모든 전송 완료!")
print("=" * 50)
```

if **name** == “**main**”:
main()