"""History tab: scrollable list of past generations with View/Re-Run."""

import os

import customtkinter as ctk

from core.history_manager import load_history
from core.models import HistoryEntry
from gui.dialogs import HistoryDetailDialog


class HistoryTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self._app = app

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Generation History",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Refresh", width=80, command=self.refresh
        ).pack(side="right")

        # Column headers
        col_header = ctk.CTkFrame(self, fg_color="transparent")
        col_header.pack(fill="x", padx=15, pady=(5, 0))

        ctk.CTkLabel(col_header, text="Date", width=160, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(col_header, text="Job Title", width=200, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(col_header, text="Company", width=150, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(col_header, text="Files", width=50, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(col_header, text="Actions", width=140, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left")

        # Scrollable list
        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self._entries: list[HistoryEntry] = []

    def refresh(self):
        """Reload history from disk and rebuild the list."""
        # Clear existing rows
        for widget in self._scroll.winfo_children():
            widget.destroy()

        self._entries = load_history()

        if not self._entries:
            ctk.CTkLabel(
                self._scroll,
                text="No generation history yet.",
                text_color="gray",
            ).pack(pady=20)
            return

        for entry in self._entries:
            self._add_row(entry)

    def _add_row(self, entry: HistoryEntry):
        row = ctk.CTkFrame(self._scroll)
        row.pack(fill="x", pady=2)

        # Date (truncate to readable format)
        date_str = entry.timestamp[:16].replace("T", " ")
        ctk.CTkLabel(row, text=date_str, width=160, anchor="w").pack(side="left", padx=5)

        # Job title
        title = entry.job_title[:30] + ("..." if len(entry.job_title) > 30 else "")
        ctk.CTkLabel(row, text=title, width=200, anchor="w").pack(side="left")

        # Company
        company = entry.company[:20] + ("..." if len(entry.company) > 20 else "")
        ctk.CTkLabel(row, text=company, width=150, anchor="w").pack(side="left")

        # File count
        file_count = len(entry.files)
        ctk.CTkLabel(row, text=str(file_count), width=50, anchor="w").pack(side="left")

        # Actions
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="View",
            width=60,
            height=28,
            command=lambda e=entry: self._view(e),
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Re-Run",
            width=70,
            height=28,
            command=lambda e=entry: self._rerun(e),
        ).pack(side="left")

    def _view(self, entry: HistoryEntry):
        HistoryDetailDialog(
            self._app, entry, on_rerun=lambda e: self._rerun(e)
        )

    def _rerun(self, entry: HistoryEntry):
        self._app.load_for_rerun(entry)
