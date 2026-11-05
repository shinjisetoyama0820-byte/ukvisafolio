
"""UK VISA FOLIO AIエージェントのワークフロー（初期版）。"""

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from .config import (
        AI_ENABLED,
        MONTHLY_BUDGET_JPY,
        QUALITY_CHECKS,
        can_publish,
    )
except ImportError:
    from config import (
        AI_ENABLED,
        MONTHLY_BUDGET_JPY,
        QUALITY_CHECKS,
        can_publish,
    )


def run_workflow(topic):
    """APIを使わず、各エージェントの作業計画を作成する。"""
    if not topic or not topic.strip():
        raise ValueError("記事のテーマが必要です")

    tasks = {
        "research": {
            "status": "PENDING",
            "task": "GOV.UKの一次情報を確認する",
        },
        "seo_geo": {
            "status": "PENDING",
            "task": "検索意図・競合・AI検索対策を分析する",
        },
        "writer": {
            "status": "PENDING",
            "task": "わかりやすく専門性のある記事を作成する",
        },
        "localization": {
            "status": "PENDING",
            "task": "対象国の制度と現地書類を確認する",
        },
        "quality": {
            "status": "BLOCKED",
            "checks": {name: "BLOCKED" for name in QUALITY_CHECKS},
        },
    }

    return {
        "project": "UK VISA FOLIO",
        "topic": topic.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "LIVE" if AI_ENABLED else "DRY_RUN",
        "monthly_budget_jpy": MONTHLY_BUDGET_JPY,
        "tasks": tasks,
        "publish_allowed": False,
    }


if __name__ == "__main__":
    result = run_workflow("英国配偶者ビザの必要書類")
    print(json.dumps(result, ensure_ascii=False, indent=2))
