"""Select existing Japanese drafts for review; never publish."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    "英国配偶者ビザ": "family",
    "英国婚約者ビザ": "family",
    "英国未婚パートナービザ": "family",
    "英国技能労働者ビザ": "skilled_worker",
    "英国ヘルスケアワークビザ": "health_and_care_worker",
    "英国学生ビザ": "student",
}

def select():
    policy = json.loads((ROOT / "editorial/automation-policy.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "editorial/article-ledger-190.json").read_text(encoding="utf-8"))
    candidates = []
    seen = set()
    for item in ledger["articles"]:
        group = GROUPS.get(item.get("category"))
        if group not in policy["priority"] or item.get("cms_status") != "saved_draft":
            continue
        path = (ROOT / item["path"]).resolve()
        if not path.is_relative_to(ROOT / "content/articles") or not path.is_file() or path in seen:
            continue
        seen.add(path)
        parts = path.read_text(encoding="utf-8-sig").split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            continue
        meta = yaml.safe_load(parts[1])
        if not isinstance(meta, dict) or meta.get("status") != "draft" or meta.get("lang", "ja") != policy["language"]:
            continue
        qa = item.get("qa") or {}
        blocked = [key for key in policy["required_qa"] if qa.get(key) != "PASS"]
        candidates.append((policy["priority"].index(group), item["id"], {
            "id": item["id"], "title": meta.get("title"), "path": item["path"],
            "group": group, "blocked_checks": blocked,
            "manual_review_complete": policy.get("manual_review_complete") is True,
            "publication_allowed": False
        }))
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in candidates[:policy["daily_limit"]]]

if __name__ == "__main__":
    print(json.dumps({"mode": "review_only", "selected": select()}, ensure_ascii=False, indent=2))
