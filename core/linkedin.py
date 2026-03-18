"""Fetch job details from a LinkedIn job posting URL.

Uses LinkedIn's unauthenticated guest API endpoint, which returns an HTML
fragment with structured job data — no login or API key required.
"""

import re
from typing import Callable

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_job_id(url: str) -> str | None:
    """Extract a LinkedIn job ID from any common URL format.

    Handles:
      https://www.linkedin.com/jobs/view/4195069600/
      https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4195069600
      https://www.linkedin.com/jobs/search/?currentJobId=4195069600&...
    """
    # /jobs/view/<id>
    m = re.search(r"/jobs/view/(\d+)", url)
    if m:
        return m.group(1)
    # ?currentJobId=<id> or &currentJobId=<id>
    m = re.search(r"currentJobId=(\d+)", url)
    if m:
        return m.group(1)
    # bare numeric ID anywhere in the path (last resort)
    m = re.search(r"/(\d{8,})", url)
    if m:
        return m.group(1)
    return None


def _element_to_text(element) -> str:
    """Convert a BeautifulSoup element's HTML to clean plain text.

    Preserves paragraph breaks and converts <li> items to bullet points.
    """
    # Replace <li> elements with bullet-prefixed plain text before extraction
    for ul in element.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            text = li.get_text(strip=True)
            if text:
                li.replace_with(f"\n• {text}")

    for ol in element.find_all("ol"):
        for i, li in enumerate(ol.find_all("li", recursive=False), 1):
            text = li.get_text(strip=True)
            if text:
                li.replace_with(f"\n{i}. {text}")

    raw = element.get_text(separator="\n")

    # Collapse runs of blank lines to a single blank line
    lines = [ln.rstrip() for ln in raw.splitlines()]
    result: list[str] = []
    prev_blank = False
    for ln in lines:
        is_blank = ln == ""
        if is_blank and prev_blank:
            continue
        result.append(ln)
        prev_blank = is_blank

    return "\n".join(result).strip()


def fetch_linkedin_job(
    url: str,
    on_status: Callable[[str], None] = lambda _: None,
) -> dict:
    """Fetch job title, company, and description from a LinkedIn job URL.

    Returns a dict with keys: ``job_title``, ``company``, ``description``.
    Raises ``ValueError`` for bad URLs and ``requests.RequestException`` for
    network / HTTP errors.
    """
    job_id = extract_job_id(url.strip())
    if not job_id:
        raise ValueError(
            "Could not find a LinkedIn job ID in that URL.\n\n"
            "Expected format:\n"
            "  https://www.linkedin.com/jobs/view/1234567890/\n"
            "  or a URL containing  currentJobId=1234567890"
        )

    on_status(f"Fetching LinkedIn job {job_id}...")

    # LinkedIn's unauthenticated guest endpoint — works without login
    api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    resp = requests.get(api_url, headers=_HEADERS, timeout=20)

    if resp.status_code == 404:
        raise ValueError(
            f"LinkedIn returned 404 for job ID {job_id}.\n"
            "The posting may have been removed or the URL is incorrect."
        )
    if resp.status_code == 429:
        raise ValueError(
            "LinkedIn is rate-limiting requests right now (429).\n"
            "Wait a minute and try again, or paste the description manually."
        )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # --- Job title ---
    title_el = (
        soup.find("h2", class_=lambda c: c and "top-card-layout__title" in c)
        or soup.find("h2", class_=lambda c: c and "topcard__title" in c)
        or soup.find("h2")
    )
    job_title = title_el.get_text(strip=True) if title_el else ""

    # --- Company ---
    company_el = (
        soup.find("a", class_=lambda c: c and "topcard__org-name-link" in c)
        or soup.find(
            "span", class_=lambda c: c and "topcard__flavor" in c and
            "topcard__flavor--black-link" not in (c or "")
        )
        or soup.find("a", class_=lambda c: c and "topcard__org-name" in c)
    )
    company = company_el.get_text(strip=True) if company_el else ""

    # --- Description ---
    # Prefer the detailed markup div; fall back progressively
    desc_el = (
        soup.find("div", class_=lambda c: c and "show-more-less-html__markup" in c)
        or soup.find("div", class_=lambda c: c and "description__text" in c)
        or soup.find("section", class_=lambda c: c and "description" in c)
    )

    if desc_el:
        description = _element_to_text(desc_el)
    else:
        # Last resort: full page text (still often useful)
        description = soup.get_text(separator="\n", strip=True)

    if not description:
        raise ValueError(
            "Fetched the LinkedIn page but could not extract a description.\n"
            "The posting may require login. Try pasting the description manually."
        )

    on_status(f"Fetched: {job_title or 'job'} at {company or 'company'}")

    return {
        "job_title": job_title,
        "company": company,
        "description": description,
    }


def format_for_textbox(job_data: dict) -> str:
    """Format fetched job data into a single string for the description text box.

    Prepending the title and company ensures Claude can reliably extract them
    even if they don't appear elsewhere in the description body.
    """
    parts: list[str] = []
    if job_data.get("job_title"):
        parts.append(f"Job Title: {job_data['job_title']}")
    if job_data.get("company"):
        parts.append(f"Company: {job_data['company']}")
    if parts:
        parts.append("")  # blank separator line
    parts.append(job_data.get("description", ""))
    return "\n".join(parts)
