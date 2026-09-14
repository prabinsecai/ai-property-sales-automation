"""Conservative grounding checks: responses may only assert facts in retrieved context."""
import re


def validate_response(response: str, context: str) -> tuple[str, bool]:
    if not response:
        return "I don't have enough verified information to answer that.", False
    if not context and any(re.search(pattern, response.lower()) for pattern in
                           (r"\$\s*\d", r"\b\d+\s*bedroom", r"\bavailable\b")):
        return "I don't have enough verified information to answer that.", False
    # Reject critical numeric claims not present in retrieved evidence (for example a
    # generated rent that differs from the property's verified rent).
    for value in re.findall(r"\$\s*[\d,]+(?:\.\d+)?", response):
        if value.replace(",", "") not in context.replace(",", ""):
            return "I don't have enough verified information to answer that.", False
    return response, True
