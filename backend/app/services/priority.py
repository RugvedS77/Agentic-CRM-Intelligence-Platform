CRITICAL = [
    "urgent",
    "legal",
    "ransomware",
    "breach",
    "p0",
    "production down"
]


def calculate_priority(
    subject: str,
    body: str
):

    text = f"{subject} {body}".lower()

    score = 0

    for word in CRITICAL:
        if word in text:
            score += 20

    return min(score, 100)