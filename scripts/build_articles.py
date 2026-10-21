from pathlib import Path
import re, html, json, datetime
from urllib.parse import urlparse
import yaml, mistune
ROOT=Path(__file__).resolve().parents[1]
CONT=ROOT/'content'/'articles'
OUT=ROOT/'articles'
OUT.mkdir(exist_ok=True)
# Remove generated HTML from previous builds to prevent withdrawn posts remaining public.
for old in OUT.glob('*.html'): old.unlink()
entries=[]
def esc(s): return html.escape(str(s or ''),quote=True)
def safe_url(s):
    u=urlparse(str(s or ''))
    return str(s) if u.scheme=='https' and u.netloc.lower() in ('www.gov.uk','gov.uk') else ''
def layout(title,desc,body,canonical):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UK VISA FOLIO</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canonical)}"><style>:root{{color-scheme:light}}body{{margin:0;font:16px/1.9 system-ui,-apple-system,sans-serif;background:#f4f7fa;color:#203447}}main{{max-width:820px;margin:36px auto;padding:32px;background:white;border-radius:14px;box-shadow:0 2px 16px #0000000a}}h1{{line-height:1.35}}a{{color:#086d79}}.muted{{color:#586777}}.notice{{background:#eff7f7;padding:14px;border-left:3px solid #086d79}}ul{{padding-left:1.5em}}li{{margin:16px 0}}@media(max-width:680px){{main{{margin:0;padding:22px;border-radius:0}}}}</style></head><body><main><nav><a href="/">トップ</a> / <a href="/articles.html">英国ビザ記事一覧</a></nav>{body}</main></body></html>'''
for f in sorted(CONT.glob('*.md')):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',f.stem): continue
    raw=f.read_text(encoding='utf-8')
    if not raw.startswith('---\n'):continue
    try:
        front,body=raw[4:].split('\n---\n',1)
        meta=yaml.safe_load(front) or {}
    except (ValueError,yaml.YAMLError):continue
    if meta.get('status')!='published':continue
    title=str(meta.get('title') or '').strip()
    if not title: continue
    date=str(meta.get('date') or '')
    desc=str(meta.get('description') or '')
    source=safe_url(meta.get('source_url'))
    # Markdown HTML is escaped before conversion; embedded raw HTML and script cannot execute.
    safe_body=mistune.html(html.escape(body))
    citation=f'<p><strong>一次情報：</strong><a rel="noopener noreferrer" href="{esc(source)}">英国政府公式ページ</a></p>' if source else '<p class="notice">公式情報へのリンクは未設定です。公開前に一次情報を確認してください。</p>'
    page=layout(title,desc,f'<p class="muted">公開日：{esc(date)}</p><h1>{esc(title)}</h1>{safe_body}{citation}<p class="notice">ビザ制度は変更される場合があります。申請前に英国政府の最新情報を確認してください。</p>',f'https://ukvisafolio.com/articles/{f.stem}.html')
    (OUT/(f.stem+'.html')).write_text(page,encoding='utf-8')
    entries.append({'date':date,'title':title,'description':desc,'slug':f.stem})
entries.sort(key=lambda x:(x['date'],x['slug']),reverse=True)
items=''.join(f'<li><a href="/articles/{esc(x["slug"])}.html"><strong>{esc(x["title"])}</strong></a><div class="muted">{esc(x["date"])} — {esc(x["description"])}</div></li>' for x in entries)
body='<h1>英国ビザの記事一覧</h1><p>必要な書類や手続き、制度変更を分かりやすく説明します。</p><ul>'+(items or '<li>記事を準備しています。</li>')+'</ul>'
(ROOT/'articles.html').write_text(layout('英国ビザの記事一覧','英国ビザ申請の解説と最新情報',body,'https://ukvisafolio.com/articles.html'),encoding='utf-8')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>https://ukvisafolio.com/{esc(p)}</loc></url>\n' for p in ['','articles.html']+[f'articles/{x["slug"]}.html' for x in entries])+'</urlset>\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://ukvisafolio.com/sitemap.xml\n',encoding='utf-8')
print(f'Generated {len(entries)} published articles; drafts excluded.')
