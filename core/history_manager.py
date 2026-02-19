"""Manage generation history persistence."""

import json
import os
import uuid
from datetime import datetime, timezone

from core.config_manager import get_data_dir
from core.models import GeneratedFile, GenerationOptions, HistoryEntry


def _get_history_path() -> str:
    return os.path.join(get_data_dir(), "history.json")


def load_history() -> list[HistoryEntry]:
    """Load history from disk, newest first. Recomputes file existence."""
    path = _get_history_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    entries = []
    for item in data:
        entry = HistoryEntry.from_dict(item)
        # Recompute file existence
        for file_info in entry.files:
            if isinstance(file_info, dict):
                file_info["exists"] = os.path.isfile(file_info.get("path", ""))
        entries.append(entry)

    # Newest first
    entries.sort(key=lambda e: e.timestamp, reverse=True)
    return entries


def save_history(entries: list[HistoryEntry]) -> None:
    """Write full history list to disk."""
    path = _get_history_path()
    data = [e.to_dict() for e in entries]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_history_entry(
    job_title: str,
    company: str,
    job_description: str,
    options: GenerationOptions,
    files: list[GeneratedFile],
) -> HistoryEntry:
    """Create a new HistoryEntry with a fresh UUID and current timestamp."""
    return HistoryEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        job_title=job_title,
        company=company,
        job_description=job_description,
        options={
            "generate_resume": options.generate_resume,
            "generate_cover_letter": options.generate_cover_letter,
            "format_docx": options.format_docx,
            "format_pdf": options.format_pdf,
            "format_txt": options.format_txt,
        },
        files=[
            {"file_type": f.file_type, "format": f.format, "path": f.path}
            for f in files
        ],
    )


def add_history_entry(entry: HistoryEntry) -> None:
    """Append a new entry to history and save."""
    entries = load_history()
    entries.insert(0, entry)  # Newest first
    save_history(entries)
