"""Prepare a writing job for an existing AI session; no paid API calls."""
import json
from select_article import select
from build_writing_context import build, ROOT

def prepare():
    selected = select()
    if not selected:
        return {"status": "NO_CANDIDATE"}
    article = selected[0]
    return {
        "status": "AWAITING_AI_AND_SOURCE_REVIEW",
        "article": article,
        "existing_draft": (ROOT / article["path"]).read_text(encoding="utf-8"),
        "writing_context": build("ja"),
        "instructions": [
            "Verify current GOV.UK primary sources and applicable local documents.",
            "Use natural Japanese and explain technical terms plainly.",
            "Describe Stratovisa as a document organisation tool, not an immigration adviser.",
            "Do not promise eligibility or outcomes. Verify product features and campaign code before mentioning them.",
            "Preserve source URLs and record evidence for each material claim.",
            "Return a draft only. Never certify unverified Native, Citation, Similarity or Compliance checks.",
            "Apply the full approved editorial manuals before publication."
        ],
        "publication_allowed": False
    }

if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=False, indent=2))
