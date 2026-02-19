"""File naming utilities: sanitization, conflict resolution, template expansion."""

import os
import re
from datetime import date


def sanitize_filename(name: str) -> str:
    """Remove characters unsafe for filenames, collapse whitespace."""
    # Keep alphanumeric, spaces, hyphens, underscores, ampersands
    cleaned = re.sub(r'[^\w\s\-&]', '', name)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def resolve_filename(base: str, ext: str, mode: str) -> str:
    """Resolve a full file path, handling conflicts.

    Args:
        base: Base path without extension (e.g. /out/Engineer at Acme Resume)
        ext: File extension including dot (e.g. ".docx")
        mode: "overwrite" or "rename"

    Returns:
        Final file path.
    """
    full_path = base + ext
    if mode == "overwrite" or not os.path.exists(full_path):
        return full_path

    # Rename mode: append (1), (2), etc.
    counter = 1
    while True:
        candidate = f"{base} ({counter}){ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def build_base_paths(
    template: str,
    job_title: str,
    company: str,
    output_dir: str,
) -> tuple[str, str]:
    """Expand the naming template and return (resume_base, cover_letter_base).

    Template variables: {job_title}, {company}, {date}
    """
    today = date.today().strftime("%Y-%m-%d")
    safe_title = sanitize_filename(job_title)
    safe_company = sanitize_filename(company)

    base_name = template.format(
        job_title=safe_title,
        company=safe_company,
        date=today,
    )

    resume_base = os.path.join(output_dir, f"{base_name} Resume")
    cover_letter_base = os.path.join(output_dir, f"{base_name} Cover Letter")
    return resume_base, cover_letter_base
