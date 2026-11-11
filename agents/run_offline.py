"""Offline entrypoint. Does not call AI APIs, GitHub or Cloudflare."""
import argparse
import json
from pathlib import Path
try:
    from .draft_builder import create_draft
    from .quality_gate import evaluate
    from .seo_geo import plan
except ImportError:
    from draft_builder import create_draft
    from quality_gate import evaluate
    from seo_geo import plan

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--packet', required=True, help='local JSON source packet')
    p.add_argument('--out', default='output/drafts', help='local draft directory; not public site')
    args = p.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding='utf-8'))
    path = create_draft(packet, args.out)
    report = {'draft': str(path), 'seo_geo': plan(packet['topic'], packet['country'], packet['visa_type']),
              'quality': evaluate({}), 'api_calls': 0, 'api_cost_jpy': 0,
              'note': 'Template only. No automated research, AI writing or publication.'}
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
