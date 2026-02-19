"""Data models for the Resume/Cover Letter Generator application."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppConfig:
    """Persisted application configuration."""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    experience_file: str = ""
    output_directory: str = ""
    naming_template: str = "{job_title} at {company}"
    conflict_mode: str = "rename"  # "rename" or "overwrite"

    def to_dict(self) -> dict:
        return {
            "anthropic_api_key": self.anthropic_api_key,
            "openai_api_key": self.openai_api_key,
            "experience_file": self.experience_file,
            "output_directory": self.output_directory,
            "naming_template": self.naming_template,
            "conflict_mode": self.conflict_mode,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        return cls(
            anthropic_api_key=d.get("anthropic_api_key", ""),
            openai_api_key=d.get("openai_api_key", ""),
            experience_file=d.get("experience_file", ""),
            output_directory=d.get("output_directory", ""),
            naming_template=d.get("naming_template", "{job_title} at {company}"),
            conflict_mode=d.get("conflict_mode", "rename"),
        )


@dataclass
class GenerationOptions:
    """Per-generation toggles."""
    generate_resume: bool = True
    generate_cover_letter: bool = True
    format_docx: bool = True
    format_pdf: bool = True
    format_txt: bool = True


@dataclass
class GeneratedFile:
    """A single generated output file."""
    file_type: str  # "resume" or "cover_letter"
    format: str     # "txt", "docx", or "pdf"
    path: str
    exists: bool = True


@dataclass
class HistoryEntry:
    """A single generation history record."""
    id: str
    timestamp: str  # ISO 8601
    job_title: str
    company: str
    job_description: str
    options: dict = field(default_factory=dict)
    files: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "job_title": self.job_title,
            "company": self.company,
            "job_description": self.job_description,
            "options": self.options,
            "files": [
                {"file_type": f["file_type"], "format": f["format"], "path": f["path"]}
                if isinstance(f, dict) else
                {"file_type": f.file_type, "format": f.format, "path": f.path}
                for f in self.files
            ],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(
            id=d["id"],
            timestamp=d["timestamp"],
            job_title=d.get("job_title", ""),
            company=d.get("company", ""),
            job_description=d.get("job_description", ""),
            options=d.get("options", {}),
            files=d.get("files", []),
        )
