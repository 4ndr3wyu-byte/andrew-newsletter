import os
import json
import time
import requests
from collections import defaultdict

TOKEN   = os.environ[‘NEWSLETTER_TOKEN’]
CHAT_ID = os.environ[‘NEWSLETTER_CHAT_ID’]

SOURCE_ICONS = {
‘Reuters’:         ‘Reuters’,
‘Bloomberg’:       ‘Bloomberg’,
‘Financial Times’: ‘Financial Times’,
‘The Verge’:       ‘The Verge’,
‘TechCrunch’:      ‘TechCrunch’,
‘Ars Technica’:    ‘Ars Technica’,
‘Electrek’:        ‘Electrek’,
‘Teslarati’:       ‘Teslarati’,
‘MacRumors’:       ‘MacRumors’,
‘9to5Mac’:         ‘9to5Mac’
}

def send(text):
url  = ‘https://api.telegram.org/bot’ + TOKEN + ‘/sendMessage’
data = {
‘chat_id’:                  CHAT_ID,
‘text’:                     text,
‘parse_mode’:               ‘HTML’,
‘disable_web_page_preview’: True
}
try:
resp = requests.post(url, json=data, timeout=30)
resp.raise_for_status()
except Exception as e:
print(’send failed: ’ + str(e))
time.sleep(1.5)

def main():
print(’=’ * 50)
print(‘Andrew Newsletter – telegram send’)
print(’=’ * 50)

```
with open('andrew-newsletter-news.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']
date     = data['date']
total    = data['total']

send(
    '<b>Andrew Newsletter</b>\n'
    '------------------------\n'
    + date + '\n'
    + '총 ' + str(total) + '개 기사 | 10개 소스\n'
    '------------------------'
)

grouped = defaultdict(list)
for a in articles:
    grouped[a['source']].append(a)

for source in SOURCE_ICONS:
    items = grouped.get(source, [])
    if not items:
        continue

    msg = '<b>[' + source + ']</b>\n\n'

    for i, a in enumerate(items, 1):
        msg += '<b>' + str(i) + '. ' + a['title'] + '</b>\n'
        msg += a['summary_ko'] + '\n'
        msg += '<a href="' + a['link'] + '">원문 보기</a>\n\n'

    send(msg)
    print('sent: ' + source)

print('all done')
print('=' * 50)
```

if **name** == ‘**main**’:
main()