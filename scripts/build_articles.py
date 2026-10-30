from pathlib import Path
import re, html, datetime
from urllib.parse import urlparse
import yaml, mistune

ROOT = Path(__file__).resolve().parents[1]
CONT = ROOT / 'content' / 'articles'
OUT = ROOT / 'articles'
OUT.mkdir(exist_ok=True)

# Remove generated HTML from previous builds to prevent withdrawn posts remaining public.
for old in OUT.glob('*.html'):
    old.unlink()

entries = []

def esc(s):
    return html.escape(str(s or ''), quote=True)

def safe_url(s):
    u = urlparse(str(s or ''))
    return str(s) if u.scheme == 'https' and u.netloc.lower() in ('www.gov.uk', 'gov.uk') else ''

# Calculate NEW visibility in the visitor's browser, so it disappears automatically
# even when Cloudflare Pages has not performed another build.
NEW_ASSETS = r'''<style>
.new-badge{display:none;color:#c62828;font-size:.72em;font-weight:800;letter-spacing:.04em;margin-left:.35em}
.new-badge.is-new{display:inline-block;animation:new-pulse 1.3s ease-in-out infinite}
@keyframes new-pulse{50%{opacity:.15}}
@media(prefers-reduced-motion:reduce){.new-badge.is-new{animation:none}}
</style>
<script>
document.addEventListener('DOMContentLoaded',function(){
 const now=Date.now(),week=7*24*60*60*1000;
 document.querySelectorAll('[data-new-since]').forEach(function(el){
  const ts=Date.parse(el.getAttribute('data-new-since'));
  if(Number.isFinite(ts)&&ts<=now&&now-ts<week)el.classList.add('is-new');
 });
});
</script>''' 

# CMS date-only values have no time. Interpret them as midnight Japan time.
def iso_date(value):
    raw=str(value or '').strip()
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',raw): return ''
    try: datetime.date.fromisoformat(raw)
    except ValueError: return ''
    return raw

def badge_time(meta):
    published=iso_date(meta.get('date'))
    if not published: return ''
    base=published+'T00:00:00+09:00'
    update=str(meta.get('significant_update_at') or '').strip()
    # Explicit significant updates only; never treat ordinary edits as new.
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',update):
        update=iso_date(update)+'T00:00:00+09:00' if iso_date(update) else ''
    if update:
        try:
            dt=datetime.datetime.fromisoformat(update.replace('Z','+00:00'))
            if dt.tzinfo and dt.timestamp()>=datetime.datetime.fromisoformat(base).timestamp():return dt.isoformat()
        except ValueError: pass
    return base

# Opt-in currency converter: inserted only where the article contains the shortcode.
GBP_JPY_SHORTCODE = '[GBP_JPY_CONVERTER]'
GBP_JPY_WIDGET = r'''<section class="gbp-jpy-widget" aria-label="ポンド円換算ツール">
<style>
.gbp-jpy-widget{border:1px solid #cbdde3;border-radius:12px;padding:20px;margin:24px 0;background:#f6fafb}
.gbp-jpy-widget label{display:block;font-weight:700;margin-bottom:7px}
.gbp-jpy-widget input{box-sizing:border-box;width:100%;max-width:340px;padding:12px;border:1px solid #8b9ba6;border-radius:7px;font:inherit;background:#fff;color:#203447}
.gbp-jpy-widget output{display:block;font-size:1.45rem;font-weight:750;margin-top:12px;overflow-wrap:anywhere}
.gbp-jpy-widget .fx-meta{font-size:.85rem;color:#586777;margin-top:6px;line-height:1.6}
</style>
<label for="gbp-jpy-amount">換算したい金額（GBP・ポンド）</label>
<input id="gbp-jpy-amount" type="number" min="0" step="any" value="5169" inputmode="decimal">
<output id="gbp-jpy-result" aria-live="polite">為替レートを取得しています…</output>
<p id="gbp-jpy-meta" class="fx-meta">参考レートを取得中</p>
<p class="fx-meta">参考値です。為替レートは提供元の最新公表値を使用し、通常は営業日に更新されます。実際の支払額はカード会社等の為替レートや手数料で変わります。</p>
<script>
(function(){
  const input=document.getElementById('gbp-jpy-amount');
  const output=document.getElementById('gbp-jpy-result');
  const meta=document.getElementById('gbp-jpy-meta');
  if(!input||!output||!meta)return;
  let rate=null;
  function render(){
    const amount=Number(input.value);
    if(input.value.trim()===''||!Number.isFinite(amount)||amount<0){output.textContent='0以上の金額を入力してください';return;}
    if(rate===null){output.textContent='為替レートを取得しています…';return;}
    output.textContent='約 '+new Intl.NumberFormat('ja-JP',{style:'currency',currency:'JPY',maximumFractionDigits:0}).format(amount*rate);
  }
  input.addEventListener('input',render);
  // Frankfurter serves the latest published reference rate (business days).
  fetch('https://api.frankfurter.dev/v1/latest?base=GBP&symbols=JPY',{cache:'no-store'})
    .then(function(response){if(!response.ok)throw new Error('HTTP '+response.status);return response.json();})
    .then(function(data){
      const next=Number(data&&data.rates&&data.rates.JPY);
      if(!Number.isFinite(next)||next<=0||!/^\d{4}-\d{2}-\d{2}$/.test(data.date||''))throw new Error('Invalid rate');
      rate=next;
      meta.textContent='参考レート：1 GBP = '+next.toLocaleString('ja-JP',{maximumFractionDigits:4})+' JPY ／ レート公表日：'+data.date+'（Frankfurter）';
      render();
    })
    .catch(function(){output.textContent='現在、換算できません';meta.textContent='為替レートを取得できませんでした。時間をおいて再度お試しください。';});
  render();
})();
</script>
</section>'''

def add_currency_converter(markdown_html):
    # The Markdown content is escaped before conversion; only this exact shortcode is trusted.
    return markdown_html.replace('<p>'+GBP_JPY_SHORTCODE+'</p>', GBP_JPY_WIDGET)

def new_badge(timestamp):
    return f'<span class="new-badge" data-new-since="{esc(timestamp)}" aria-label="新着記事">NEW</span>' if timestamp else ''

SITE_STYLE = r"""
:root{color-scheme:light;--navy:#102b47;--ink:#233448;--gold:#b18a4c;--line:#dce4ea;--muted:#5c6b7a}
*{box-sizing:border-box}body{margin:0;font:16px/1.85 system-ui,-apple-system,"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;background:#f5f7fa;color:var(--ink)}
a{color:#12617d;text-underline-offset:3px}a:hover{color:#0b4055}
.site-header{background:var(--navy);color:white;border-bottom:3px solid var(--gold)}
.site-header-inner{max-width:1040px;margin:auto;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.brand{color:white;text-decoration:none;font-weight:800;letter-spacing:.09em;font-size:1.05rem}.brand:hover{color:#fff}
.site-nav{display:flex;flex-wrap:wrap;gap:22px}.site-nav a{color:#eaf1f7;text-decoration:none;font-size:.92rem;font-weight:650}.site-nav a:hover{text-decoration:underline}
.page-wrap{max-width:1040px;margin:38px auto 64px;padding:0 20px}.page-surface{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 32px #102b470a;padding:clamp(24px,4.5vw,54px)}
.breadcrumb{font-size:.83rem;color:var(--muted);margin-bottom:24px}.breadcrumb a{color:var(--muted)}
h1{font-size:clamp(1.65rem,3.4vw,2.35rem);line-height:1.45;color:var(--navy);margin:10px 0 18px}h2{color:var(--navy);line-height:1.5;margin-top:2.2em;border-bottom:1px solid var(--line);padding-bottom:.35em}h3{color:var(--navy);line-height:1.5}
p,li{overflow-wrap:anywhere}ul,ol{padding-left:1.5em}li{margin:9px 0}.muted{color:var(--muted)}
.eyebrow{font-size:.75rem;letter-spacing:.16em;color:#8b6937;font-weight:800;text-transform:uppercase;margin:0 0 8px}
.lead{font-size:1.02rem;color:#4a5d70;max-width:750px;margin-bottom:26px}
.section-rule{width:54px;height:3px;background:var(--gold);margin:22px 0 28px}
.article-grid{list-style:none;padding:0;margin:0;display:grid;gap:14px}
.article-card{margin:0;border:1px solid var(--line);border-radius:12px;background:#fff;transition:border-color .2s,box-shadow .2s}
.article-card:hover{border-color:#b5c5d2;box-shadow:0 5px 20px #102b4712}
.article-card>a{display:block;padding:24px;text-decoration:none;color:inherit}
.article-meta{font-size:.8rem;color:var(--muted);display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:8px}
.article-kind{display:inline-block;background:#eaf0f5;color:#25425d;padding:2px 10px;border-radius:4px;font-weight:700}
.article-card h2{border:0;padding:0;margin:0 0 10px;font-size:1.12rem;line-height:1.6;color:var(--navy)}
.article-card p{font-size:.9rem;color:#526273;margin:0;line-height:1.75}
.article-more{display:inline-block;color:#14677a;font-size:.86rem;font-weight:750;margin-top:12px}
.info-panel{margin-top:32px;background:#f6f8fa;border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:7px;padding:20px 24px;font-size:.9rem}
.info-panel strong{color:var(--navy)}.info-panel p{margin:7px 0 0}
.empty-state{padding:40px 24px;border:1px dashed #becbd5;border-radius:12px;text-align:center;background:#fafbfd;color:var(--muted)}
.article-detail{max-width:820px;margin:auto}.article-detail h1{font-size:clamp(1.55rem,3vw,2.15rem)}
.article-detail p{margin:1.1em 0}.article-detail img{max-width:100%;height:auto}
.notice{background:#f2f7f8;padding:16px 20px;border-left:3px solid #28788a;border-radius:4px}
.site-footer{text-align:center;color:#667586;font-size:.8rem;padding:0 20px 36px}
@media(max-width:640px){.site-header-inner{padding:16px 20px}.site-nav{gap:15px}.page-wrap{margin:20px auto 36px;padding:0 12px}.page-surface{border-radius:12px;padding:24px 18px}.article-card>a{padding:18px}.article-card h2{font-size:1.04rem}}
"""

def layout(title, desc, body, canonical, page_class='article-detail'):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UK VISA FOLIO</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canonical)}"><style>{SITE_STYLE}</style>{NEW_ASSETS}</head><body><header class="site-header"><div class="site-header-inner"><a class="brand" href="/">UK VISA FOLIO</a><nav class="site-nav" aria-label="メインナビゲーション"><a href="/">トップ</a><a href="/visa-news.html">NEWS</a><a href="/articles.html">解説記事</a></nav></div></header><div class="page-wrap"><main class="page-surface {esc(page_class)}"><nav class="breadcrumb" aria-label="現在位置"><a href="/">トップ</a> / <a href="/articles.html">解説記事</a></nav>{body}</main></div><footer class="site-footer">UK VISA FOLIO — 英国ビザ申請に役立つ情報を分かりやすく。</footer></body></html>'''

for f in sorted(CONT.glob('*.md')):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', f.stem):
        continue
    raw = f.read_text(encoding='utf-8')
    if not raw.startswith('---\n'):
        continue
    try:
        front, body = raw[4:].split('\n---\n', 1)
        meta = yaml.safe_load(front) or {}
    except (ValueError, yaml.YAMLError):
        continue
    if meta.get('status') != 'published':
        continue
    title = str(meta.get('title') or '').strip()
    if not title:
        continue
    date = str(meta.get('date') or '')
    category = 'news' if meta.get('category') == 'news' else 'guide'
    timestamp = badge_time(meta)
    desc = str(meta.get('description') or '')
    source = safe_url(meta.get('source_url'))
    # Markdown HTML is escaped before conversion; embedded raw HTML and script cannot execute.
    safe_body = add_currency_converter(mistune.html(html.escape(body)))
    citation = f'<p><strong>一次情報：</strong><a rel="noopener noreferrer" href="{esc(source)}">英国政府公式ページ</a></p>' if source else '<p class="notice">公式情報へのリンクは未設定です。公開前に一次情報を確認してください。</p>'
    page = layout(title, desc, f'<p class="muted">公開日：{esc(date)} {new_badge(timestamp)}</p><h1>{esc(title)}</h1>{safe_body}{citation}<p class="notice">ビザ制度は変更される場合があります。申請前に英国政府の最新情報を確認してください。</p>', f'https://ukvisafolio.com/articles/{f.stem}.html')
    (OUT / (f.stem + '.html')).write_text(page, encoding='utf-8')
    entries.append({'date': date, 'title': title, 'description': desc, 'slug': f.stem, 'category':category, 'timestamp':timestamp})

entries.sort(key=lambda x: (x['date'], x['slug']), reverse=True)
def listing(group, heading, intro, canonical):
    subset = [x for x in entries if x['category'] == group]
    kind = '制度変更・最新情報' if group == 'news' else '申請ガイド'
    cards = ''.join(
        '<li class="article-card"><a href="/articles/' + esc(x['slug']) + '.html">'
        + '<div class="article-meta"><span class="article-kind">' + esc(kind) + '</span>'
        + '<time datetime="' + esc(x['date']) + '">' + esc(x['date']) + '</time>'
        + new_badge(x['timestamp']) + '</div>'
        + '<h2>' + esc(x['title']) + '</h2>'
        + '<p>' + esc(x['description']) + '</p><span class="article-more">記事を読む →</span>'
        + '</a></li>' for x in subset
    )
    content = '<ul class="article-grid">' + cards + '</ul>' if cards else '<div class="empty-state">現在、記事を準備しています。</div>'
    intro_panel = ('英国政府の公式情報を確認し、制度の発表日・施行日・対象者を区別してお伝えします。'
                   if group == 'news' else '申請条件や必要書類は個人の状況によって異なります。申請前に必ず最新の公式情報をご確認ください。')
    body = ('<p class="eyebrow">UK VISA FOLIO / ' + ('NEWS' if group == 'news' else 'GUIDES') + '</p>'
            + '<h1>' + esc(heading) + '</h1><p class="lead">' + esc(intro) + '</p>'
            + '<div class="section-rule" aria-hidden="true"></div>' + content
            + '<aside class="info-panel"><strong>情報の確認について</strong><p>' + esc(intro_panel)
            + ' <a href="https://www.gov.uk/browse/visas-immigration" rel="noopener noreferrer">英国政府の公式情報を見る</a></p>'
            + '<p>UK VISA FOLIOは英国政府の公式サイトではありません。</p></aside>')
    page = layout(heading, intro, body, canonical, 'article-listing')
    if group == 'news':
        page = page.replace('<nav class="breadcrumb" aria-label="現在位置"><a href="/">トップ</a> / <a href="/articles.html">解説記事</a></nav>', '<nav class="breadcrumb" aria-label="現在位置"><a href="/">トップ</a> / NEWS</nav>')
    (ROOT / ('visa-news.html' if group == 'news' else 'articles.html')).write_text(page, encoding='utf-8')

listing('guide','英国ビザの解説記事','英国ビザの書類や手続きを分かりやすく説明します。','https://ukvisafolio.com/articles.html')
listing('news','英国ビザNEWS','英国ビザ制度の変更情報を掲載します。','https://ukvisafolio.com/visa-news.html')
# Public metadata consumed by the homepage. No drafts are included.
import json
(ROOT / 'article-updates.json').write_text(json.dumps({
    'news':max((x['timestamp'] for x in entries if x['category']=='news' and x['timestamp']),default=''),
    'guide':max((x['timestamp'] for x in entries if x['category']=='guide' and x['timestamp']),default='')
},ensure_ascii=False),encoding='utf-8')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://ukvisafolio.com/{esc(p)}</loc></url>\n' for p in ['','articles.html','visa-news.html'] + [f'articles/{x["slug"]}.html' for x in entries]) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://ukvisafolio.com/sitemap.xml\n', encoding='utf-8')
print(f'Generated {len(entries)} published articles; drafts excluded.')
