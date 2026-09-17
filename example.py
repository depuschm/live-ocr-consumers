"""
example.py - the smallest consumer that follows the reply format.

Reports how many regions in a snapshot have text. Copy it to start a new one.
"""


def handle(event):
    if event.get("type") != "snapshot":
        return None
    regions = event.get("regions", {})
    filled = sorted(name for name, text in regions.items() if text.strip())
    return {
        "v": 1,
        "consumer": "example",
        "in_reply_to": event.get("ts"),
        "message": f"{len(filled)} of {len(regions)} regions have text",
        "decision": {"action": "none"},
        "reason": "The example consumer only counts regions with text.",
        "algorithm": {"name": "count-non-empty", "version": 1},
        "inputs": {"regions_with_text": filled},
        "warnings": [],
    }
