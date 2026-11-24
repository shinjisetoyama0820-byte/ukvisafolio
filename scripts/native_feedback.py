"""Record native edits without automatically certifying QA."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "editorial/native-feedback"

def record(article_id, original, revised, language, reviewer, rules):
    if not article_id or not all(c.isalnum() or c in "-_" for c in article_id):
        raise ValueError("Invalid article ID")
    if not reviewer.strip():
        raise ValueError("Reviewer required")
    before = Path(original).read_text(encoding="utf-8")
    after = Path(revised).read_text(encoding="utf-8")
    if not before.strip() or not after.strip():
        raise ValueError("Both article versions required")
    approved_rules = json.loads(Path(rules).read_text(encoding="utf-8"))
    if not isinstance(approved_rules, list) or any(
        not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip()
        for k in ("before", "after", "reason", "rule", "scope"))
        for r in approved_rules
    ):
        raise ValueError("Each rule requires before, after, reason, rule and scope")
    payload = {
        "article_id": article_id, "language": language, "reviewer": reviewer,
        "original": before, "revised": after,
        "original_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "revised_sha256": hashlib.sha256(after.encode()).hexdigest(),
        "diff": list(difflib.unified_diff(before.splitlines(), after.splitlines(),
                                        fromfile="AI", tofile="native", lineterm="")),
        "proposed_rules": approved_rules,
        "rules_approved": False,
        "formal_qa_changed": False
    }
    STORE.mkdir(parents=True, exist_ok=True)
    target = STORE / (article_id + ".json")
    with target.open("x", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return target

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for arg in ("article_id", "original", "revised", "language", "reviewer", "rules"):
        p.add_argument(arg)
    print(record(**vars(p.parse_args())))
