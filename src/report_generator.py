from collections.abc import Mapping, Sequence


def _format_list(items: Sequence[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None detected."


def generate_report(
    original_text: str,
    category: str | None = None,
    estimated_probability: float | None = None,
    summary: str = "",
    dates: Sequence[Mapping[str, object]] = (),
    entities: Sequence[Mapping[str, str]] = (),
    action_items: Sequence[str] = (),
) -> str:
    """Build a Markdown report from extracted results without adding facts."""
    category_text = category if category else "Not classified"
    probability_text = (
        f"{estimated_probability:.1%} (model estimate)"
        if estimated_probability is not None
        else "Not available"
    )

    date_lines = []
    for date in dates:
        description = str(date.get("text", "Date not specified"))
        normalized = date.get("normalized_date")
        if normalized:
            description += f" ({normalized})"
        if date.get("is_ambiguous"):
            description += " (ambiguous; not interpreted)"
        if date.get("is_deadline"):
            description += " [possible deadline]"
        date_lines.append(f"- {description}")

    entity_lines = [
        f"- {entity.get('text', '')} ({entity.get('label', 'entity')})"
        for entity in entities
    ]
    original_lines = "\n".join(f"> {line}" for line in original_text.splitlines())

    return "\n".join(
        [
            "# Notice Analysis Report",
            "",
            f"- Predicted category: {category_text}",
            f"- Category score: {probability_text}",
            "",
            "## Summary",
            summary or "No summary available.",
            "",
            "## Dates and deadlines",
            "\n".join(date_lines) if date_lines else "- None detected.",
            "",
            "## Named entities",
            "\n".join(entity_lines) if entity_lines else "- None detected.",
            "",
            "## Action items",
            _format_list(action_items),
            "",
            "## Original notice",
            original_lines or "> No notice text provided.",
            "",
        ]
    )