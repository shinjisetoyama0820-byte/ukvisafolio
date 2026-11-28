"""Publish one reviewed topic a day, and catch up reviewed language editions."""

import argparse
import re
from datetime import datetime

from publish_daily_articles import COLLECTION, JST, PRIORITY, article_files, official


QA_FIELDS = ("qa_native", "qa_citation", "qa_similarity", "qa_compliance")


def ready(metadata):
    return (metadata.get("status") == "draft"
            and all(str(metadata.get(field, "")).strip().upper() == "PASS" for field in QA_FIELDS)
            and bool(metadata.get("title") and metadata.get("description") and metadata.get("last_verified_at"))
            and official(str(metadata.get("source_url", "")), uk_only=True))


def choose(records, today, retry_only):
    published = [(path, meta) for path, meta, _ in records if meta.get("status") == "published"]
    already_published = {
        (path.stem, meta.get("lang", "ja")) for path, meta in published
    }
    existing_ids = {
        (str(meta["editorial_id"]), meta.get("lang", "ja"))
        for _, meta in published if meta.get("editorial_id") is not None
    }
    active = {path.stem for path, meta in published if meta.get("free_publish_topic_date")}
    drafts = []
    for path, meta, _ in records:
        language = meta.get("lang", "ja")
        if (ready(meta) and (path.stem, language) not in already_published
                and (str(meta.get("editorial_id", "")), language) not in existing_ids):
            drafts.append((path, meta))
    catch_up = [(path, meta) for path, meta in drafts if path.stem in active]
    if retry_only:
        return catch_up
    if any(str(meta.get("free_publish_topic_date")) == today for _, meta in published):
        return catch_up
    for route in PRIORITY:
        for path, _ in drafts:
            if path.stem not in active and re.match(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{route}-", path.stem):
                return catch_up + [entry for entry in drafts if entry[0].stem == path.stem]
    return catch_up


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--retry-only", action="store_true")
    args = parser.parse_args()
    today = datetime.now(JST).date().isoformat()
    records = list(article_files())
    topic_dates = {path.stem: str(meta["free_publish_topic_date"]) for path, meta, _ in records
                   if meta.get("status") == "published" and meta.get("free_publish_topic_date")}
    selected = choose(records, today, args.retry_only)
    if not selected:
        print("No reviewed editions ready to publish.")
        return
    for path, _ in selected:
        print(f"{'Would publish' if args.preview else 'Publishing'} {path.relative_to(COLLECTION)}")
        if args.preview:
            continue
        front, body = path.read_text(encoding="utf-8").split("\n---\n", 1)
        front, status_count = re.subn(r"(?m)^status:[^\n]*$", "status: published", front)
        front, date_count = re.subn(r"(?m)^date:[^\n]*$", f'date: "{today}"', front)
        if status_count != 1 or date_count != 1:
            raise ValueError(f"Expected one status and date in {path.name}")
        front += f'\nfree_publish_topic_date: "{topic_dates.get(path.stem, today)}"'
        path.write_text(front + "\n---\n" + body, encoding="utf-8")


if __name__ == "__main__":
    main()
