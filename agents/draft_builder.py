"""Offline, evidence-first draft generator for Pages CMS."""
from datetime import date
from pathlib import Path
import json
import re

REQUIRED = ('title', 'topic', 'country', 'visa_type', 'official_sources')

def _yaml_quote(value):
    return json.dumps(str(value), ensure_ascii=False)

def _safe_slug(value):
    value = re.sub(r'[^a-z0-9-]+', '-', value.lower()).strip('-')
    if not value or len(value) > 80:
        raise ValueError('slug must be 1-80 ASCII letters, digits or hyphens')
    return value

def create_draft(packet, output_dir):
    for field in REQUIRED:
        if not packet.get(field):
            raise ValueError(f'missing required field: {field}')
    sources = packet['official_sources']
    if not isinstance(sources, list) or not sources:
        raise ValueError('official_sources must be a nonempty list')
    for s in sources:
        if not isinstance(s, dict) or not s.get('url', '').startswith('https://') or not s.get('verified_at'):
            raise ValueError('each source needs https URL and verified_at')
    slug = _safe_slug(packet.get('slug', ''))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f'{date.today().isoformat()}-{slug}.md'
    if target.exists():
        raise FileExistsError(f'will not overwrite existing draft: {target}')
    title = packet['title']
    description = packet.get('description', '一次情報を確認して作成する記事の下書きです。')
    lines = [
        '---', f'title: {_yaml_quote(title)}', f'date: {date.today().isoformat()}',
        'status: draft', 'category: guide', f'description: {_yaml_quote(description)}',
        f'source_url: {_yaml_quote(sources[0]["url"])}', '---', '',
        f'# {title}', '', '> 編集用下書き：一次情報の確認と品質審査が完了するまで公開しない。', '',
        '## 結論', '', '【要確認】公式情報に基づき、対象者と結論を記入する。', '',
        '## 対象者と必要な準備', '',
        f'対象国・地域：{packet["country"]}  ',
        f'ビザ種別：{packet["visa_type"]}', '',
        '【要確認】対象国の公的書類・取得方法を一次情報で確認する。', '',
        '## 手続きと注意点', '',
        '【要確認】手続きの順序、費用、条件、施行日を確認する。', '',
        '## よくある質問', '',
        '【要確認】実際の検索意図に基づく質問と回答を作成する。', '',
        '## 公式情報', ''
    ]
    for s in sources:
        lines.append(f'- {s["url"]}（確認日：{s["verified_at"]}）')
    lines += ['', '## 編集者向け確認事項', '',
              '- Native: BLOCKED', '- Citation: BLOCKED',
              '- Similarity: BLOCKED', '- Compliance: BLOCKED',
              '- 人間の最終承認: 未実施', '']
    target.write_text('\n'.join(lines), encoding='utf-8')
    return target
