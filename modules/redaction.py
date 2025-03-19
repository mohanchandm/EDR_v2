def redact_text(text, entities):
    """Redact the text by replacing detected entities with [REDACTED]."""
    if not entities:
        return text

    # Sort entities by start position to avoid overlapping issues
    entities = sorted(entities, key=lambda x: x["start"])
    redacted_text = list(text)
    last_end = 0

    for entity in entities:
        start, end = entity["start"], entity["end"]
        # Ensure we don't overlap with previous redaction
        if start >= last_end:
            redacted_text[start:end] = "[REDACTED]" * (end - start)
            last_end = end

    return "".join(redacted_text)