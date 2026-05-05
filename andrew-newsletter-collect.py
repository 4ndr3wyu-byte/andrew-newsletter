import os
import json
import re
import time
import requests
import feedparser
from datetime import datetime

GEMINI_KEY = os.environ['NEWSLETTER_GEMINI_KEY']

SOURCES = {
    'Reuters':         'https://feeds.reuters.com/reuters/topNews',
    'Bloomberg':       'https://news.google.com/rss/search?q=bloomberg+markets+economy&hl=en-US&gl=US&ceid=US:en',
    'Financial Times': 'https://news.google.com/rss/search?q=financial+times+economy+markets&hl=en-US&gl=US&ceid=US:en',
    'The Verge':       'https://www.theverge.com/rss/index.xml',
    'TechCrunch':      'https://techcrunch.com/feed/',
    'Ars Technica':    'https://feeds.arstechnica.com/arstechnica/index',
    'Electrek':        'https://electrek.co/feed/',
    'Teslarati':       'https://www.teslarati.com/feed/',
    'MacRumors':       'https://feeds.macrumors.com/MacRumors-All',
    '9to5Mac':         'https://9to5mac.com/feed/'
}

TOP_N = 5

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

def fetch_articles():
    all_articles = []
    for source, url in SOURCES.items():
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
            count = 0
            for entry in feed.entries:
                if count >= TOP_N:
                    break
                title = clean_html(entry.get('title', ''))
                link  = entry.get('link', '')
                desc  = clean_html(entry.get('summary', entry.get('description', '')))
                if not title or not link:
                    continue
                all_articles.append({
                    'id':          source.lower().replace(' ', '_').replace('.', '') + '_' + str(count),
                    'source':      source,
                    'title':       title,
                    'link':        link,
                    'description': desc[:600],
                    'summary_ko':  ''
                })
                count += 1
            print('OK ' + source + ': ' + str(count) + 'articles')
        except Exception as e:
            print('FAIL ' + source + ': ' + str(e))
    return all_articles

def call_gemini(prompt):
    url = (
        'https://generativelanguage.googleapis.com/v1beta/'
        'models/gemini-2.0-flash:generateContent?key=' + GEMINI_KEY
    )
    body = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 300}
    }
    for attempt in range(3):
        try:
            resp = requests.post(url, json=body, timeout=30)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print('  Rate limit -> wait ' + str(wait) + 's')
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print('  Gemini error: ' + str(e))
            return None
    return None

def generate_summary(article):
    prompt = (
        '다음 영문 기사를 한국어 3줄로 요약해줘.\n\n'
        '규칙:\n'
        '- 정확히 3줄만 작성\n'
        '- 각 줄은 핵심 내용 1가지\n'
        '- 번호나 기호 없이 줄바꿈으로만 구분\n'
        '- 자연스러운 한국어\n\n'
        '제목: ' + article['title'] + '\n'
        '내용: ' + article['description']
    )
    result = call_gemini(prompt)
    return result if result else '요약을 생성할 수 없습니다.'

def main():
    print('=' * 50)
    print('Andrew Newsletter -- collect start')
    print('=' * 50)

    articles = fetch_articles()
    print('total: ' + str(len(articles)))

    print('generating summaries...')
    for i, article in enumerate(articles):
        print('  [' + str(i+1) + '/' + str(len(articles)) + '] ' + article['title'][:50])
        article['summary_ko'] = generate_summary(article)
        time.sleep(2)

    data = {
        'generated_at': datetime.now().isoformat(),
        'date':         datetime.now().strftime('%Y년 %m월 %d일'),
        'total':        len(articles),
        'articles':     articles
    }

    with open('andrew-newsletter-news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('done: ' + str(len(articles)) + ' articles saved')
    print('=' * 50)

if __name__ == '__main__':
    main()