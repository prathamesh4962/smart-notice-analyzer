import requests


class BackendAPIError(RuntimeError):
    """Raised when the configured analysis backend cannot return a valid result."""


def analyze_notice_via_api(
    notice_text: str,
    api_base_url: str,
    timeout: float = 120,
) -> dict[str, object]:
    """Send notice text to the backend API and return its analysis response."""
    url = f"{api_base_url.rstrip('/')}/api/analyze"
    try:
        response = requests.post(
            url,
            json={"text": notice_text},
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise BackendAPIError(
            f"Could not connect to the analysis API at {api_base_url}. "
            "Check that the backend is running and NOTICE_API_URL is correct."
        ) from error

    if not response.ok:
        try:
            error_body = response.json()
        except ValueError:
            error_body = {}
        detail = (
            error_body.get("detail", response.text)
            if isinstance(error_body, dict)
            else response.text
        )
        raise BackendAPIError(f"Analysis API returned HTTP {response.status_code}: {detail}")

    try:
        result = response.json()
    except ValueError as error:
        raise BackendAPIError("The analysis API returned an invalid JSON response.") from error

    if not isinstance(result, dict):
        raise BackendAPIError("The analysis API returned an unexpected response format.")
    required_fields = {
        "original_text",
        "category",
        "estimated_probability",
        "summary",
        "dates",
        "entities",
        "action_items",
        "report",
    }
    missing_fields = required_fields.difference(result)
    if missing_fields:
        raise BackendAPIError(
            "The analysis API response is missing fields: "
            + ", ".join(sorted(missing_fields))
        )
    return result
