
"""UK VISA FOLIO AIエージェント共通設定。"""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

# 初期段階では外部AI APIを呼び出さない
AI_ENABLED = False

# 月間API予算（日本円）
MONTHLY_BUDGET_JPY = 3000

# 記事の保存先
ARTICLES_DIR = ROOT / "content" / "articles"

# AIが作成する記事は必ず下書き
DEFAULT_STATUS = "draft"

# 公開前に必要な品質チェック
QUALITY_CHECKS = (
    "Native",
    "Citation",
    "Similarity",
    "Compliance",
)

# 4項目がすべてPASSになるまで公開禁止
def can_publish(results):
    return all(
        results.get(check) == "PASS"
        for check in QUALITY_CHECKS
    )

# APIキーはGitHubのコードに直接記載しない
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
