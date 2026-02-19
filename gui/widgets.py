"""Reusable GUI widgets for the application."""

import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk


class PasswordEntry(ctk.CTkFrame):
    """Label + masked entry + Show/Hide toggle."""

    def __init__(self, master, label_text: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._label = ctk.CTkLabel(self, text=label_text, anchor="w")
        self._label.pack(fill="x", pady=(0, 2))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(row, textvariable=self._var, show="*", width=350)
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self._showing = False
        self._toggle_btn = ctk.CTkButton(
            row, text="Show", width=60, command=self._toggle
        )
        self._toggle_btn.pack(side="right")

    def _toggle(self):
        self._showing = not self._showing
        self._entry.configure(show="" if self._showing else "*")
        self._toggle_btn.configure(text="Hide" if self._showing else "Show")

    def get(self) -> str:
        return self._var.get().strip()

    def set(self, value: str):
        self._var.set(value)


class FilePickerRow(ctk.CTkFrame):
    """Label + entry + Browse button for file or directory selection."""

    def __init__(
        self,
        master,
        label_text: str,
        mode: str = "file",
        filetypes: list | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._mode = mode
        self._filetypes = filetypes or []

        self._label = ctk.CTkLabel(self, text=label_text, anchor="w")
        self._label.pack(fill="x", pady=(0, 2))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(row, textvariable=self._var, width=350)
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self._browse_btn = ctk.CTkButton(
            row, text="Browse", width=70, command=self._browse
        )
        self._browse_btn.pack(side="right")

    def _browse(self):
        if self._mode == "directory":
            path = filedialog.askdirectory(title="Select Directory")
        else:
            path = filedialog.askopenfilename(
                title="Select File",
                filetypes=self._filetypes or [("All files", "*.*")],
            )
        if path:
            self._var.set(path)

    def get(self) -> str:
        return self._var.get().strip()

    def set(self, value: str):
        self._var.set(value)


class StatusLog(ctk.CTkFrame):
    """Read-only scrollable text log with append() and clear() methods."""

    def __init__(self, master, height: int = 200, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._textbox = ctk.CTkTextbox(self, height=height, state="disabled")
        self._textbox.pack(fill="both", expand=True)

    def append(self, message: str):
        """Append a line to the log."""
        self._textbox.configure(state="normal")
        self._textbox.insert("end", message + "\n")
        self._textbox.see("end")
        self._textbox.configure(state="disabled")

    def clear(self):
        """Clear all log content."""
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
