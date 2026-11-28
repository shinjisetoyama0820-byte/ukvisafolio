from hashlib import sha256
from pathlib import Path
import re, html, datetime
from urllib.parse import urlparse
try:
    import yaml
except ImportError:
    yaml = None
import mistune

ROOT = Path(__file__).resolve().parents[1]
CONT = ROOT / 'content' / 'articles'
SITE_SCRIPT = ROOT / 'assets' / 'site.js'
SITE_SCRIPT_URL = '/assets/site.js'
if SITE_SCRIPT.is_file():
    SITE_SCRIPT_URL += '?v=' + sha256(SITE_SCRIPT.read_bytes()).hexdigest()[:12]
OUT = ROOT / 'articles'
OUT.mkdir(exist_ok=True)

# Remove generated HTML from previous builds to prevent withdrawn posts remaining public.
for pattern in ('*.html', '*.md'):
    for old in OUT.glob(pattern):
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

def load_meta(front):
    if yaml is not None:
        return yaml.safe_load(front) or {}
    data = {}
    for line in front.splitlines():
        if not line.strip() or line.lstrip().startswith('#') or ':' not in line:
            continue
        key, value = line.split(':', 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data

WIDGET_TEXT = {
    'en': [
        ('ポンド円換算ツール', 'Pound to yen converter'),
        ('換算したい金額（GBP・ポンド）', 'Amount to convert (GBP)'),
        ('為替レートを取得しています…', 'Loading the exchange rate...'),
        ('参考レートを取得中', 'Loading a reference rate'),
        ('参考値です。為替レート提供元の最新公表値を使用し、通常は営業日に更新されます。実際の支払額はカード会社等の為替レートや手数料で変わります。', 'This is a reference value. It uses the latest published rate and usually updates on business days. The amount you pay can differ because of your card provider rate and fees.'),
        ('0以上の金額を入力してください', 'Enter an amount of 0 or more'),
        ("toLocaleString('ja-JP'", "toLocaleString('en-GB'"),
        ('参考レート：', 'Reference rate: '),
        ('レート公表日：', 'Rate date: '),
        ('現在、換算できません', 'The conversion is unavailable right now'),
        ('為替レートを取得できませんでした。時間をおいて再度お試しください。', 'The rate could not be loaded. Please try again later.'),
    ],
    'hi': [
        ('ポンド円換算ツール', 'पाउंड से येन कैलकुलेटर'),
        ('換算したい金額（GBP・ポンド）', 'जितनी राशि बदलनी है (GBP)'),
        ('為替レートを取得しています…', 'विनिमय दर लोड हो रही है...'),
        ('参考レートを取得中', 'संदर्भ दर लोड हो रही है'),
        ('参考値です。為替レート提供元の最新公表値を使用し、通常は営業日に更新されます。実際の支払額はカード会社等の為替レートや手数料で変わります。', 'यह संदर्भ मूल्य है। इसमें नवीनतम प्रकाशित दर है और यह आमतौर पर कार्यदिवस पर बदलती है। भुगतान की राशि कार्ड प्रदाता की दर और शुल्क से अलग हो सकती है।'),
        ('0以上の金額を入力してください', '0 या उससे अधिक राशि लिखें'),
        ("toLocaleString('ja-JP'", "toLocaleString('hi-IN'"),
        ('参考レート：', 'संदर्भ दर: '),
        ('レート公表日：', 'दर की तारीख: '),
        ('現在、換算できません', 'अभी रूपांतरण उपलब्ध नहीं है'),
        ('為替レートを取得できませんでした。時間をおいて再度お試しください。', 'दर लोड नहीं हो सकी। कुछ देर बाद फिर कोशिश करें।'),
    ],
}

def add_currency_converter(markdown_html, lang='ja'):
    widget = GBP_JPY_WIDGET
    for src, dst in WIDGET_TEXT.get(lang, []):
        widget = widget.replace(src, dst)
    return markdown_html.replace('<p>'+GBP_JPY_SHORTCODE+'</p>', widget)

def new_badge(timestamp, label):
    return f'<span class="new-badge" data-new-since="{esc(timestamp)}" aria-label="{esc(label)}">NEW</span>' if timestamp else ''

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
.site-header .lang-select[data-lang-select]{appearance:none;-webkit-appearance:none;-moz-appearance:none;background-color:#fff;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 14 14'%3E%3Cg fill='none' stroke='%23102b47' stroke-width='1'%3E%3Ccircle cx='7' cy='7' r='6'/%3E%3Cellipse cx='7' cy='7' rx='2.6' ry='6'/%3E%3Cline x1='1' y1='7' x2='13' y2='7'/%3E%3C/g%3E%3C/svg%3E"),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath fill='none' stroke='%23102b47' stroke-width='1.5' d='M1 1l4 4 4-4'/%3E%3C/svg%3E");background-repeat:no-repeat,no-repeat;background-position:left 6px center,right 6px center;border:1px solid #d6dee7;border-radius:8px;padding:3px 20px 3px 24px;font-size:12px;font-weight:500;color:#102b47;cursor:pointer;font-family:inherit;line-height:1.4;flex-shrink:0}
.site-header .lang-select[data-lang-select] option{background-color:#fff;color:#102b47}
@media(max-width:640px){.site-header-inner{padding:16px 20px}.site-nav{gap:15px}.page-wrap{margin:20px auto 36px;padding:0 12px}.page-surface{border-radius:12px;padding:24px 18px}.article-card>a{padding:18px}.article-card h2{font-size:1.04rem}}
"""

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
    'zh-tw': {
        'nav_label': '主要選單',
        'nav_home': '首頁',
        'nav_guides': '解說文章',
        'crumb': '目前位置',
        'published': '公開日',
        'source_label': '一次來源：',
        'source_link': '英國政府頁面',
        'source_missing': '尚未加上官方頁面的連結。',
        'change_notice': '簽證規定可能改變。申請前請看英國政府的最新說明。',
        'footer': 'UK VISA FOLIO。用淺白的話說明英國簽證的準備。',
        'disclaimer': 'Stratovisa 是文件整理工具，不是移民顧問。不判斷申請資格，也不提供移民建議。文件要求全部依據 GOV.UK 公開指引。',
        'kind_news': '規定變更與最新消息',
        'kind_guide': '申請指南',
        'read': '閱讀文章 →',
        'empty': '繁體中文的文章正在準備。',
        'news_panel': '我們依照英國政府頁面，把公布日、生效日和適用對象分開說明。',
        'guide_panel': '條件和文件會因個人情況而不同。申請前請看 GOV.UK 的最新說明。',
        'panel_title': '關於資訊的確認',
        'gov_link': '看英國政府的說明',
        'not_gov': 'UK VISA FOLIO 不是英國政府的網站。',
        'guide_heading': '英國簽證解說',
        'guide_intro': '用淺白的話說明英國簽證的文件和步驟。',
        'news_heading': '英國簽證 NEWS',
        'news_intro': '英國簽證規定的變更。',
        'new_label': '新文章',
        'md_source': '出處',
        'md_canonical': '文章',
        'md_date': '公開日',
        'md_desc': '說明',
        'fx': '匯率換算請使用這篇文章的 HTML 版。',
        'md_gov': '英國政府說明',
        'md_html': 'HTML 版',
        'md_change': '簽證規定可能改變。申請前請看英國政府的最新說明。',
    },
    'ko': {
        'nav_label': '주 메뉴',
        'nav_home': '홈',
        'nav_guides': '비자 가이드',
        'crumb': '현재 위치',
        'published': '게시일',
        'source_label': '공식 출처:',
        'source_link': '영국 정부 웹사이트',
        'source_missing': '공식 페이지 링크를 준비 중입니다.',
        'change_notice': '비자 규정은 바뀔 수 있습니다. 신청 전에 GOV.UK의 최신 안내를 확인하세요.',
        'footer': 'UK VISA FOLIO는 영국 비자 신청 준비를 알기 쉽게 설명합니다.',
        'disclaimer': 'Stratovisa는 서류 정리 도구이며 이민 자문 서비스가 아닙니다. 신청 자격을 판단하거나 이민 관련 조언을 제공하지 않습니다. 서류 요건은 GOV.UK 공개 지침을 따릅니다.',
        'kind_news': '규정 변경 및 최신 소식',
        'kind_guide': '신청 가이드',
        'read': '기사 읽기 →',
        'empty': '한국어 기사를 준비 중입니다.',
        'news_panel': '영국 정부 자료를 바탕으로 발표일, 시행일, 적용 대상을 구분해 설명합니다.',
        'guide_panel': '상황에 따라 서류와 요건이 달라질 수 있습니다. 신청 전에 GOV.UK의 최신 안내를 확인하세요.',
        'panel_title': '공식 정보 확인',
        'gov_link': '영국 정부 안내 보기',
        'not_gov': 'UK VISA FOLIO는 영국 정부 공식 웹사이트가 아닙니다.',
        'guide_heading': '영국 비자 신청 가이드',
        'guide_intro': '영국 비자 신청에 필요한 서류와 절차를 쉽게 설명합니다.',
        'news_heading': '영국 비자 소식',
        'news_intro': '영국 비자 규정 변경 소식입니다.',
        'new_label': '새 기사',
        'md_source': '출처',
        'md_canonical': '기사',
        'md_date': '게시일',
        'md_desc': '요약',
        'fx': '환율을 계산하려면 이 기사의 HTML 버전을 이용하세요.',
        'md_gov': '영국 정부 안내',
        'md_html': 'HTML 버전',
        'md_change': '비자 규정은 바뀔 수 있습니다. 신청 전에 GOV.UK의 최신 안내를 확인하세요.',
    },
}

def href(lang, leaf):
    if lang == 'ja':
        return '/' + leaf if leaf else '/'
    return f'/{lang}/' + leaf if leaf else f'/{lang}/'

def absolute(lang, leaf):
    return 'https://ukvisafolio.com' + href(lang, leaf)

def alt_links(pairs):
    def hreflang(code):
        return 'zh-Hant' if code == 'zh-tw' else code
    links = ''.join(f'<link rel="alternate" hreflang="{esc(hreflang(code))}" href="{esc(url)}">' for code, url in pairs)
    default = next((url for code, url in pairs if code == 'ja'), pairs[0][1] if pairs else '')
    if default:
        links += f'<link rel="alternate" hreflang="x-default" href="{esc(default)}">'
    return links

def switch_markup(lang, canonical):
    path = canonical.split('ukvisafolio.com', 1)[-1].strip('/')
    prefix = '' if lang == 'ja' else lang
    if prefix and (path == prefix or path.startswith(prefix + '/')):
        path = path[len(prefix):].strip('/')
    if path.endswith('.html'):
        path = path[:-5]
    labels = (('ja', '日本語'), ('en', 'English'), ('hi', 'हिन्दी'), ('zh-tw', '繁體中文'), ('ko', '한국어'))
    options = []
    for code, label in labels:
        leaf = path
        if path.startswith('articles/') and '/' in path and code not in by_slug.get(path.split('/', 1)[1], {}):
            leaf = 'articles'
        selected = ' selected' if code == lang else ''
        if code == 'ko' and leaf in ('articles', 'visa-news'):
            leaf += '.html'
        options.append(f'<option value="{esc(href(code, leaf))}"{selected}>{label}</option>')
    return '<select class="lang-select" data-lang-select aria-label="Change language" onchange="if(this.value)location.href=this.value">' + ''.join(options) + '</select>'

def layout(lang, title, desc, body, canonical, page_class, alt_html, crumb):
    ui = LANGS[lang]
    html_lang = 'zh-Hant' if lang == 'zh-tw' else lang
    return f'''<!doctype html><html lang="{html_lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UK VISA FOLIO</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canonical)}">{alt_html}<script src="{SITE_SCRIPT_URL}" defer></script><style>{SITE_STYLE}</style>{NEW_ASSETS}</head><body><header class="site-header"><div class="site-header-inner"><a class="brand" href="{href(lang, '')}">UK VISA FOLIO</a><nav class="site-nav" aria-label="{esc(ui['nav_label'])}"><a href="{href(lang, '')}">{esc(ui['nav_home'])}</a><a href="{href(lang, 'visa-news.html')}">NEWS</a><a href="{href(lang, 'articles.html')}">{esc(ui['nav_guides'])}</a></nav>{switch_markup(lang, canonical)}</div></header><div class="page-wrap"><main class="page-surface {esc(page_class)}"><nav class="breadcrumb" aria-label="{esc(ui['crumb'])}">{crumb}</nav>{body}</main></div><footer class="site-footer">{esc(ui['footer'])}<br>{esc(ui['disclaimer'])}</footer></body></html>'''

def clean_output(path):
    path.mkdir(parents=True, exist_ok=True)
    for pattern in ('*.html', '*.md'):
        for old in path.glob(pattern):
            old.unlink()

for code in LANGS:
    clean_output(ROOT / 'articles' if code == 'ja' else ROOT / code / 'articles')

def source_files():
    yield from ((path, None) for path in sorted(CONT.glob('*.md')))
    for code in (code for code in LANGS if code != 'ja'):
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
def build_korean_home():
    template = ROOT / 'zh-tw' / 'index.html'
    if not template.is_file():
        return
    page = template.read_text(encoding='utf-8')
    translations = (
        ("Stratovisa 是文件整理工具，不是移民顧問。不判斷申請資格，也不提供移民建議。文件要求全部依據 GOV.UK 公開指引。", "Stratovisa는 서류 정리 도구이며 이민 자문 서비스가 아닙니다. 신청 자격을 판단하거나 이민 관련 조언을 제공하지 않습니다. 서류 요건은 GOV.UK 공개 지침을 따릅니다."),
        ("35% 折扣只適用於 Stratovisa 的服務費。英國政府的申請費另計。台灣目前沒有介紹代碼，代碼確定後才會放在這裡。", "영국 정부에 납부하는 비자 신청 수수료는 GOV.UK에서 확인할 수 있습니다."),
        ("這個網站不是英國政府的網站。它和 Stratovisa 有介紹上的商業關係。申請條件和費用請看", "이 사이트는 영국 정부의 공식 웹사이트가 아니며, Stratovisa와 상업적 제휴 관계가 있습니다. 신청 요건과 비용은 다음 링크에서 확인하세요."),
        ("Stratovisa 是協助準備英國簽證申請的民間服務。使用前先看簽證種類、功能和價格。", "Stratovisa에서 지원하는 비자 유형과 서류 정리 기능을 확인하세요."),
        ("從文件、費用、步驟，到適合自己的準備方式。這個網站用繁體中文整理英國簽證的資訊。", "영국 비자에 필요한 서류와 비용, 신청 절차를 살펴보고 상황에 맞게 준비하세요."),
        ("© 2026 UK VISA FOLIO ｜ 英國簽證申請準備的資訊站", "© 2026 UK VISA FOLIO ｜ 영국 비자 신청 준비 정보"),
        ("自己準備、使用工具，或找有資格的顧問。這一頁說明差別。", "직접 준비하거나 서류 정리 도구 또는 등록된 이민 자문 서비스를 이용할 수 있습니다."),
        ("用淺白的繁體中文說明英國簽證的文件、費用和申請步驟。", "영국 비자 신청에 필요한 서류, 비용, 절차를 한국어로 쉽게 설명합니다."),
        ("Skilled Worker 和其他相近路線的起點。", "숙련근로자 비자(Skilled Worker visa) 등 취업 비자의 준비 절차를 살펴보세요."),
        ("Stratovisa 幫忙整理文件和準備步驟。", "Stratovisa는 비자 신청 서류와 준비 절차를 정리하는 도구입니다."),
        ("這個網站會把人介紹到 Stratovisa。", "이 사이트는 Stratovisa 서비스를 소개합니다."),
        ("看 Student visa 要準備什麼。", "학생 비자 신청 전에 준비할 사항을 확인하세요."),
        ("情況比較複雜，或需要法律判斷的時候。", "상황이 복잡하거나 법률 판단이 필요한 경우 이용할 수 있습니다."),
        ("看 Stratovisa 做什麼 →", "Stratovisa 기능 보기 →"),
        ("英國簽證的文件、申請方式與準備指南", "영국 비자 서류 및 신청 준비 안내"),
        ("把大家會查的問題，一個一個看過。", "신청 전에 자주 확인하는 항목을 정리했습니다."),
        ("怎麼看官方說明，以及要注意什麼。", "정부 안내를 확인하는 방법과 유의할 점을 정리했습니다."),
        ("從想申請的簽證，進到相關說明。", "신청하려는 비자 유형의 안내를 확인하세요."),
        ("說明證明文件、翻譯和整理方式。", "증빙 서류, 번역 및 정리 방법을 안내합니다."),
        ("用比較安心的方式準備英國簽證。", "영국 비자 서류를 차근차근 준비하세요."),
        ("關於 Stratovisa →", "Stratovisa 알아보기 →"),
        ("申請前想先看的手續和費用。", "신청 전에 확인할 절차와 비용입니다."),
        ("依照官方說明，自己往下做。", "정부 안내를 따라 신청을 준비합니다."),
        ("配偶或家庭簽證的示意照片", "배우자·가족 비자 안내 이미지"),
        ("給伴侶或家人路線的說明。", "배우자나 가족을 위한 비자 준비 안내입니다."),
        ("使用幫忙整理文件的工具。", "도구로 신청 서류를 정리하는 방법입니다."),
        ("查看配偶簽證的準備 →", "배우자 비자 준비 안내 →"),
        ("想把準備放在同一個地方", "한곳에서 서류 준비하기"),
        ("步驟和費用的示意照片", "신청 절차와 비용 안내 이미지"),
        ("用工具準備的示意照片", "서류 정리 도구 안내 이미지"),
        ("和顧問談話的示意照片", "이민 상담 안내 이미지"),
        ("用更容易懂的方式。", "이해하기 쉽게."),
        ("工作簽證的示意照片", "취업 비자 안내 이미지"),
        ("學生簽證的示意照片", "학생 비자 안내 이미지"),
        ("準備時用得上的指南", "비자 신청 준비 가이드"),
        ("文件指南的示意照片", "서류 가이드 이미지"),
        ("常見問題的示意照片", "자주 묻는 질문 안내 이미지"),
        ("自己準備的示意照片", "직접 준비하기 안내 이미지"),
        ("簽證準備的示意照片", "비자 신청 준비 안내 이미지"),
        ("配偶與家庭簽證", "배우자·가족 비자"),
        ("準備英國簽證，", "영국 비자 준비,"),
        ("從簽證種類開始", "비자 유형별 가이드"),
        ("工作的示意照片", "취업 안내 이미지"),
        ("準備方式的比較", "준비 방법 비교"),
        ("看更多 →", "자세히 보기 →"),
        ("步驟和費用", "신청 절차와 비용"),
        ("用工具準備", "도구로 준비하기"),
        ("解說文章", "비자 가이드"),
        ("工作簽證", "취업 비자"),
        ("學生簽證", "학생 비자"),
        ("文件指南", "서류 가이드"),
        ("常見問題", "자주 묻는 질문"),
        ("自己準備", "직접 준비하기"),
        ("找顧問談", "이민 자문 알아보기"),
        ("複製代碼", "코드 복사"),
        ("看文件", "서류 가이드"),
        ("已複製", "복사했습니다"),
        ("首頁", "홈"),
        ("文件", "서류"),
    )
    for source, korean in translations:
        page = page.replace(source, korean)
    page = re.sub(r'(<html\s+lang=")[^"]+', r'\g<1>ko', page, count=1)
    page = re.sub(r'(<link rel="canonical" href=")[^"]+', r'\g<1>https://ukvisafolio.com/ko/', page)
    page = page.replace('<title>', '<link rel="alternate" hreflang="ko" href="https://ukvisafolio.com/ko/"><title>', 1)
    # Use the English information pages until their Korean editions are available.
    page = re.sub(
        r'(?<=href=")(family|documents|guides|methods|apps|stratovisa)\.html(?=[#"])',
        r'/en/\1.html',
        page,
    )
    (ROOT / 'ko' / 'index.html').write_text(page, encoding='utf-8')


build_korean_home()

# Static pages share the same script as the generated article pages.
for code in LANGS:
    directory = ROOT if code == 'ja' else ROOT / code
    for page in directory.glob('*.html'):
        original = page.read_bytes()
        refreshed = re.sub(
            rb'(?<=src=")/assets/site\.js(?:\?v=[^"]*)?(?=")',
            SITE_SCRIPT_URL.encode('ascii'),
            original,
        )
        if refreshed != original:
            page.write_bytes(refreshed)

locs = []
for code in LANGS:
    for leaf in (('', 'articles.html', 'visa-news.html') if code == 'ko' else static_leaves):
        locs.append(absolute(code, leaf))
    for item in items:
        if item['lang'] == code:
            locs.append(absolute(code, f'articles/{item["slug"]}.html'))
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{esc(loc)}</loc></url>\n' for loc in locs) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://ukvisafolio.com/sitemap.xml\n', encoding='utf-8')
print('Generated ' + ', '.join(f"{code}:{sum(item['lang']==code for item in items)}" for code in LANGS) + ' published articles; drafts excluded.')
