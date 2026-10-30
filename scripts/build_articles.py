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

def layout(title, desc, body, canonical):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UK VISA FOLIO</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canonical)}"><style>:root{{color-scheme:light}}body{{margin:0;font:16px/1.9 system-ui,-apple-system,sans-serif;background:#f4f7fa;color:#203447}}main{{max-width:820px;margin:36px auto;padding:32px;background:white;border-radius:14px;box-shadow:0 2px 16px #0000000a}}h1{{line-height:1.35}}a{{color:#086d79}}.muted{{color:#586777}}.notice{{background:#eff7f7;padding:14px;border-left:3px solid #086d79}}ul{{padding-left:1.5em}}li{{margin:16px 0}}@media(max-width:680px){{main{{margin:0;padding:22px;border-radius:0}}}}</style>{NEW_ASSETS}</head><body><main><nav><a href="/">トップ</a> / <a href="/articles.html">英国ビザ記事一覧</a></nav>{body}</main></body></html>'''

for f in sorted(CONT.glob('*.md')):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', f.stem):
        continue
    raw = f.read_text(encoding='utf-8')
    if not raw.startswith('---\n'):
        continue
    try:
        front, body = raw[4:].split('\n---\n', 1)
        meta = yaml.safe_load(front) or {}
