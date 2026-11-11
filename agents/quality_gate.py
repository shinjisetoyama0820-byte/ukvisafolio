"""Conservative quality gate: never auto-approve unsupported claims."""
CHECKS = ('Native', 'Citation', 'Similarity', 'Compliance')

def evaluate(reviews, human_approved=False):
    reviews = reviews or {}
    checks = {key: ('PASS' if reviews.get(key) == 'PASS' else 'BLOCKED') for key in CHECKS}
    return {'checks': checks, 'human_approved': bool(human_approved),
            'publish_allowed': all(v == 'PASS' for v in checks.values()) and bool(human_approved)}
