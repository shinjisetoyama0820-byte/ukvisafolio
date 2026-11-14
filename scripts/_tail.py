import json

LANGS = {
    'ja': {
        'nav_label': 'メインナビゲーション',
        'nav_home': 'トップ',
        'nav_guides': '解説記事',
        'crumb': '現在位置',
        'published': '公開日',
        'source_label': '一次情報：',
        'source_link': '英国政府公式ページ',
        'source_missing': '公式情報へのリンクは未設定です。公開前に一次情報を確認してください。',
        'change_notice': 'ビザ制度は変更される場合があります。申請前に英国政府の最新情報を確認してください。',
        'footer': 'UK VISA FOLIO. 英国ビザ申請に役立つ情報を分かりやすく。',
        'disclaimer': 'Stratovisa は書類整理ツールであり、移民アドバイザーではありません。申請資格の判断や移民に関する助言は行いません。書類の要件はすべて GOV.UK の公開ガイダンスに基づいています。',
        'kind_news': '制度変更・最新情報',
        'kind_guide': '申請ガイド',
        'read': '記事を読む →',
        'empty': '現在、記事を準備しています。',
        'news_panel': '英国政府の公式情報を確認し、制度の発表日・施行日・対象者を区別してお伝えします。',
        'guide_panel': '申請条件や必要書類は個人の状況によって異なります。申請前に GOV.UK の最新情報を確認してください。',
        'panel_title': '情報の確認について',
        'gov_link': '英国政府の公式情報を見る',
        'not_gov': 'UK VISA FOLIOは英国政府の公式サイトではありません。',
        'guide_heading': '英国ビザの解説記事',
        'guide_intro': '英国ビザの書類や手続きを分かりやすく説明します。',
        'news_heading': '英国ビザNEWS',
        'news_intro': '英国ビザ制度の変更情報を掲載します。',
        'new_label': '新着記事',
        'md_source': '出典',
        'md_canonical': '正規記事',
        'md_date': '公開日',
        'md_desc': '記事の説明',
        'fx': '為替換算はHTML版の記事をご利用ください。',
        'md_gov': '英国政府公式情報',
        'md_html': 'HTML版',
        'md_change': '英国ビザ制度は変更される場合があります。申請前に英国政府の最新情報を確認してください。',
    },
    'en': {
        'nav_label': 'Main',
        'nav_home': 'Home',
        'nav_guides': 'Guides',
        'crumb': 'Current page',
        'published': 'Published',
        'source_label': 'Primary source: ',
        'source_link': 'UK government page',
        'source_missing': 'A link to the official page has not been added yet.',
        'change_notice': 'Visa rules can change. Check the latest UK government information before you apply.',
        'footer': 'UK VISA FOLIO. Plain-language information for preparing a UK visa application.',
        'disclaimer': 'Stratovisa is a document-organisation tool and is not an immigration adviser. It does not decide whether you qualify, and it does not give immigration advice. Document requirements follow published GOV.UK guidance.',
        'kind_news': 'Rule changes and updates',
        'kind_guide': 'Application guide',
        'read': 'Read the article →',
        'empty': 'English articles are being prepared.',
        'news_panel': 'We separate the announcement date, the start date and who the change covers, using the UK government pages.',
        'guide_panel': 'Conditions and documents depend on your situation. Check the latest GOV.UK information before you apply.',
        'panel_title': 'Checking the information',
        'gov_link': 'Read the UK government information',
        'not_gov': 'UK VISA FOLIO is not a UK government website.',
        'guide_heading': 'UK visa guides',
        'guide_intro': 'Plain-language explanations of UK visa documents and steps.',
        'news_heading': 'UK visa news',
        'news_intro': 'Changes to UK visa rules.',
        'new_label': 'New article',
        'md_source': 'Source',
        'md_canonical': 'Article',
        'md_date': 'Published',
        'md_desc': 'Description',
        'fx': 'Use the HTML version of this article for the currency conversion.',
        'md_gov': 'UK government information',
        'md_html': 'HTML version',
        'md_change': 'Visa rules can change. Check the latest UK government information before you apply.',
    },
    'hi': {
        'nav_label': 'मुख्य',
        'nav_home': 'होम',
        'nav_guides': 'गाइड',
        'crumb': 'यह पृष्ठ',
        'published': 'प्रकाशन',
        'source_label': 'प्राथमिक स्रोत: ',
        'source_link': 'यूके सरकार का पृष्ठ',
        'source_missing': 'आधिकारिक पृष्ठ की लिंक अभी नहीं जोड़ी गई है।',
        'change_notice': 'वीज़ा के नियम बदल सकते हैं। आवेदन से पहले यूके सरकार की ताज़ा जानकारी देखें।',
        'footer': 'UK VISA FOLIO. यूके वीज़ा की तैयारी के लिए सरल जानकारी।',
        'disclaimer': 'Stratovisa दस्तावेज़ व्यवस्थित करने का टूल है। यह आप्रवासन सलाहकार नहीं है। यह पात्रता तय नहीं करता और आप्रवासन सलाह नहीं देता। दस्तावेज़ों की शर्तें GOV.UK की सार्वजनिक गाइड पर आधारित हैं।',
        'kind_news': 'नियमों में बदलाव',
        'kind_guide': 'आवेदन गाइड',
        'read': 'लेख पढ़ें →',
        'empty': 'हिन्दी लेख तैयार हो रहे हैं।',
        'news_panel': 'यूके सरकार के पृष्ठों के आधार पर हम घोषणा की तारीख, शुरू होने की तारीख और किस पर असर पड़ता है, इसे अलग रखते हैं।',
        'guide_panel': 'शर्तें और दस्तावेज़ आपकी स्थिति पर निर्भर करते हैं। आवेदन से पहले GOV.UK की ताज़ा जानकारी देखें।',
        'panel_title': 'जानकारी की जाँच',
        'gov_link': 'यूके सरकार की जानकारी पढ़ें',
        'not_gov': 'UK VISA FOLIO यूके सरकार की वेबसाइट नहीं है।',
        'guide_heading': 'यूके वीज़ा गाइड',
        'guide_intro': 'यूके वीज़ा के दस्तावेज़ और कदमों की सरल व्याख्या।',
        'news_heading': 'यूके वीज़ा समाचार',
        'news_intro': 'यूके वीज़ा के नियमों में बदलाव।',
        'new_label': 'नया लेख',
        'md_source': 'स्रोत',
        'md_canonical': 'लेख',
        'md_date': 'प्रकाशन',
        'md_desc': 'विवरण',
        'fx': 'मुद्रा बदलने के लिए इस लेख का HTML संस्करण खोलें।',
        'md_gov': 'यूके सरकार की जानकारी',
        'md_html': 'HTML संस्करण',
        'md_change': 'वीज़ा के नियम बदल सकते हैं। आवेदन से पहले यूके सरकार की ताज़ा जानकारी देखें।',
    },
}

SWITCH = '<div class="lang-switch" data-lang-switch><a href="/" data-lang="ja">日本語</a><a href="/en/" data-lang="en">English</a><a href="/hi/" data-lang="hi">हिन्दी</a></div>'

def href(lang, leaf):
    if lang == 'ja':
        return '/' + leaf if leaf else '/'
    return f'/{lang}/' + leaf if leaf else f'/{lang}/'

def absolute(lang, leaf):
    return 'https://ukvisafolio.com' + href(lang, leaf)

def alt_links(pairs):
    links = ''.join(f'<link rel="alternate" hreflang="{esc(code)}" href="{esc(url)}">' for code, url in pairs)
    default = next((url for code, url in pairs if code == 'ja'), pairs[0][1] if pairs else '')
    if default:
        links += f'<link rel="alternate" hreflang="x-default" href="{esc(default)}">'
    return links

def layout(lang, title, desc, body, canonical, page_class, alt_html, crumb):
    ui = LANGS[lang]
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UK VISA FOLIO</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canonical)}">{alt_html}<script src="/assets/site.js?v=20261115" defer></script><style>{SITE_STYLE}</style>{NEW_ASSETS}</head><body><header class="site-header"><div class="site-header-inner"><a class="brand" href="{href(lang, '')}">UK VISA FOLIO</a><nav class="site-nav" aria-label="{esc(ui['nav_label'])}"><a href="{href(lang, '')}">{esc(ui['nav_home'])}</a><a href="{href(lang, 'visa-news.html')}">NEWS</a><a href="{href(lang, 'articles.html')}">{esc(ui['nav_guides'])}</a></nav>{SWITCH}</div></header><div class="page-wrap"><main class="page-surface {esc(page_class)}"><nav class="breadcrumb" aria-label="{esc(ui['crumb'])}">{crumb}</nav>{body}</main></div><footer class="site-footer">{esc(ui['footer'])}<br>{esc(ui['disclaimer'])}</footer></body></html>'''

def clean_output(path):
    path.mkdir(parents=True, exist_ok=True)
    for pattern in ('*.html', '*.md'):
        for old in path.glob(pattern):
            old.unlink()

for code in ('ja', 'en', 'hi'):
    clean_output(ROOT / 'articles' if code == 'ja' else ROOT / code / 'articles')

def source_files():
    yield from ((path, None) for path in sorted(CONT.glob('*.md')))
    for code in ('en', 'hi'):
        folder = CONT / code
        if folder.is_dir():
            yield from ((path, code) for path in sorted(folder.glob('*.md')))

items = []
seen = set()
for path, forced in source_files():
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', path.stem):
        continue
    raw = path.read_text(encoding='utf-8')
    if not raw.startswith('---\n'):
        continue
    try:
        front, body = raw[4:].split('\n---\n', 1)
        meta = load_meta(front)
    except (ValueError, yaml.YAMLError if yaml else ValueError):
        continue
    if not isinstance(meta, dict) or meta.get('status') != 'published':
        continue
    title = str(meta.get('title') or '').strip()
    if not title:
        continue
    raw_lang = str(meta.get('lang') or '').strip().lower()
    lang = forced or (raw_lang if raw_lang in LANGS else 'ja')
    if (lang, path.stem) in seen:
        continue
    seen.add((lang, path.stem))
    items.append({
        'lang': lang,
        'slug': path.stem,
        'title': title,
        'date': str(meta.get('date') or ''),
        'category': 'news' if meta.get('category') == 'news' else 'guide',
        'timestamp': badge_time(meta),
        'description': str(meta.get('description') or ''),
        'source': safe_url(meta.get('source_url')),
        'body': body,
    })

by_slug = {}
for item in items:
    by_slug.setdefault(item['slug'], {})[item['lang']] = item

for item in items:
    lang = item['lang']
    ui = LANGS[lang]
    versions = [(code, absolute(code, f'articles/{item["slug"]}.html')) for code in LANGS if code in by_slug.get(item['slug'], {})]
    canonical = absolute(lang, f'articles/{item["slug"]}.html')
    safe_body = add_currency_converter(mistune.html(html.escape(item['body'])), lang)
    if item['source']:
        citation = f'<p><strong>{esc(ui["source_label"])}</strong><a rel="noopener noreferrer" href="{esc(item["source"])}">{esc(ui["source_link"])}</a></p>'
    else:
        citation = f'<p class="notice">{esc(ui["source_missing"])}</p>'
    crumb = f'<a href="{href(lang, "")}">{esc(ui["nav_home"])}</a> / <a href="{href(lang, "articles.html")}">{esc(ui["nav_guides"])}</a>'
    article_html = f'<p class="muted">{esc(ui["published"])}：{esc(item["date"])} {new_badge(item["timestamp"], ui["new_label"])}</p><h1>{esc(item["title"])}</h1>{safe_body}{citation}<p class="notice">{esc(ui["change_notice"])}</p>'
    page = layout(lang, item['title'], item['description'], article_html, canonical, 'article-detail', alt_links(versions), crumb)
    page = page.replace('</head>', f'<link rel="alternate" type="text/markdown" href="{href(lang, "articles/" + item["slug"] + ".md")}"></head>', 1)
    out_dir = ROOT / 'articles' if lang == 'ja' else ROOT / lang / 'articles'
    (out_dir / f'{item["slug"]}.html').write_text(page, encoding='utf-8')
    md_header = (f'# {item["title"]}\n\n'
                 f'> {ui["md_source"]}: UK VISA FOLIO | {ui["md_canonical"]}: {canonical}\n'
                 f'> {ui["md_date"]}: {item["date"]}\n'
                 f'> {ui["md_desc"]}: {item["description"]}\n\n')
    md_footer = f'\n\n---\n{ui["md_change"]}\n' + (f'{ui["md_gov"]}: {item["source"]}\n' if item['source'] else '') + f'{ui["md_html"]}: {canonical}\n'
    (out_dir / f'{item["slug"]}.md').write_text(md_header + item['body'].replace(GBP_JPY_SHORTCODE, ui['fx']).strip() + md_footer, encoding='utf-8')

def listing(lang, group):
    ui = LANGS[lang]
    subset = [item for item in items if item['lang'] == lang and item['category'] == group]
    subset.sort(key=lambda item: (item['date'], item['slug']), reverse=True)
    kind = ui['kind_news'] if group == 'news' else ui['kind_guide']
    cards = ''.join(
        '<li class="article-card"><a href="' + href(lang, 'articles/' + item['slug'] + '.html') + '">'
        + '<div class="article-meta"><span class="article-kind">' + esc(kind) + '</span>'
        + '<time datetime="' + esc(item['date']) + '">' + esc(item['date']) + '</time>'
        + new_badge(item['timestamp'], ui['new_label']) + '</div>'
        + '<h2>' + esc(item['title']) + '</h2>'
        + '<p>' + esc(item['description']) + '</p><span class="article-more">' + esc(ui['read']) + '</span>'
        + '</a></li>' for item in subset
    )
    content = '<ul class="article-grid">' + cards + '</ul>' if cards else '<div class="empty-state">' + esc(ui['empty']) + '</div>'
    heading = ui['news_heading'] if group == 'news' else ui['guide_heading']
    intro = ui['news_intro'] if group == 'news' else ui['guide_intro']
    panel = ui['news_panel'] if group == 'news' else ui['guide_panel']
    leaf = 'visa-news.html' if group == 'news' else 'articles.html'
    if group == 'news':
        crumb = f'<a href="{href(lang, "")}">{esc(ui["nav_home"])}</a> / NEWS'
    else:
        crumb = f'<a href="{href(lang, "")}">{esc(ui["nav_home"])}</a> / <a href="{href(lang, "articles.html")}">{esc(ui["nav_guides"])}</a>'
    body = ('<p class="eyebrow">UK VISA FOLIO / ' + ('NEWS' if group == 'news' else 'GUIDES') + '</p>'
            + '<h1>' + esc(heading) + '</h1><p class="lead">' + esc(intro) + '</p>'
            + '<div class="section-rule" aria-hidden="true"></div>' + content
            + '<aside class="info-panel"><strong>' + esc(ui['panel_title']) + '</strong><p>' + esc(panel)
            + ' <a href="https://www.gov.uk/browse/visas-immigration" rel="noopener noreferrer">' + esc(ui['gov_link']) + '</a></p>'
            + '<p>' + esc(ui['not_gov']) + '</p></aside>')
    versions = [(code, absolute(code, leaf)) for code in LANGS]
    page = layout(lang, heading, intro, body, absolute(lang, leaf), 'article-listing', alt_links(versions), crumb)
    dest = ROOT if lang == 'ja' else ROOT / lang
    dest.mkdir(parents=True, exist_ok=True)
    (dest / leaf).write_text(page, encoding='utf-8')

for code in LANGS:
    listing(code, 'guide')
    listing(code, 'news')

(ROOT / 'article-updates.json').write_text(json.dumps({
    'news': max((item['timestamp'] for item in items if item['category'] == 'news' and item['timestamp']), default=''),
    'guide': max((item['timestamp'] for item in items if item['category'] == 'guide' and item['timestamp']), default=''),
}, ensure_ascii=False), encoding='utf-8')

static_leaves = ['', 'family.html', 'documents.html', 'guides.html', 'methods.html', 'apps.html', 'stratovisa.html', 'articles.html', 'visa-news.html']
locs = []
for code in LANGS:
    for leaf in static_leaves:
        locs.append(absolute(code, leaf))
    for item in items:
        if item['lang'] == code:
            locs.append(absolute(code, f'articles/{item["slug"]}.html'))
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{esc(loc)}</loc></url>\n' for loc in locs) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://ukvisafolio.com/sitemap.xml\n', encoding='utf-8')
print('Generated ' + ', '.join(f"{code}:{sum(item['lang']==code for item in items)}" for code in LANGS) + ' published articles; drafts excluded.')
