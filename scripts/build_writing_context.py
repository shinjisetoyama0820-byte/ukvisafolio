"""Build a writing context from explicitly approved native feedback."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build(language):
    store = ROOT / "editorial/native-feedback"
    approvals_path = ROOT / "editorial/native-feedback-approvals.json"
    approvals = json.loads(approvals_path.read_text(encoding="utf-8")) if approvals_path.exists() else {}
    rules = []
    reviewed = []
    for path in sorted(store.glob("*.json")):
        raw = path.read_bytes()
        record = json.loads(raw)
        if record.get("language") != language:
            continue
        approval = approvals.get(record.get("article_id"), {})
        if approval.get("sha256") != hashlib.sha256(raw).hexdigest() or not approval.get("approved_by"):
            continue
        reviewed.append(record["article_id"])
        for rule in record["proposed_rules"]:
            if rule not in rules:
                rules.append(rule)
    return {
        "language": language,
        "approved_review_count": len(reviewed),
        "reviewed_articles": reviewed,
        "calibration_minimum_met": len(reviewed) >= 5,
        "writing_rules": rules,
        "instruction": "Apply approved rules within their scope. Never override official sources or compliance requirements.",
        "formal_native_qa_granted": False,
        "automatic_publication_authorized": False
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="ja")
    args = parser.parse_args()
    print(json.dumps(build(args.language), ensure_ascii=False, indent=2))
