"""Settings tab: API keys, file paths, naming template, conflict mode."""

import customtkinter as ctk

from core.models import AppConfig
from gui.widgets import PasswordEntry, FilePickerRow


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self._app = app

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- API Keys ---
        ctk.CTkLabel(
            scroll,
            text="API Keys",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))

        self._anthropic_key = PasswordEntry(scroll, "Anthropic API Key:")
        self._anthropic_key.pack(fill="x", pady=(0, 8))

        self._openai_key = PasswordEntry(scroll, "OpenAI API Key:")
        self._openai_key.pack(fill="x", pady=(0, 15))

        # --- File Paths ---
        ctk.CTkLabel(
            scroll,
            text="File Paths",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))

        self._experience_file = FilePickerRow(
            scroll,
            "Experience Data File:",
            mode="file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        self._experience_file.pack(fill="x", pady=(0, 8))

        self._output_dir = FilePickerRow(
            scroll, "Output Directory:", mode="directory"
        )
        self._output_dir.pack(fill="x", pady=(0, 15))

        # --- File Naming ---
        ctk.CTkLabel(
            scroll,
            text="File Naming",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))

        self._template_var = ctk.StringVar()
        ctk.CTkLabel(scroll, text="Naming Template:", anchor="w").pack(
            fill="x", pady=(0, 2)
        )
        ctk.CTkEntry(scroll, textvariable=self._template_var, width=350).pack(
            fill="x", pady=(0, 2)
        )
        ctk.CTkLabel(
            scroll,
            text="Variables: {job_title}, {company}, {date}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
        ).pack(fill="x", pady=(0, 15))

        # --- Conflict Resolution ---
        ctk.CTkLabel(
            scroll,
            text="Conflict Resolution",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))

        self._conflict_var = ctk.StringVar(value="rename")
        ctk.CTkRadioButton(
            scroll,
            text="Rename (append number)",
            variable=self._conflict_var,
            value="rename",
        ).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(
            scroll,
            text="Overwrite existing files",
            variable=self._conflict_var,
            value="overwrite",
        ).pack(anchor="w", pady=(2, 15))

        # --- Save ---
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(
            btn_row, text="Save Settings", width=140, command=self._save
        ).pack(side="left")

        self._feedback = ctk.CTkLabel(btn_row, text="", text_color="green")
        self._feedback.pack(side="left", padx=15)

    def load_config(self, config: AppConfig):
        """Populate fields from config."""
        self._anthropic_key.set(config.anthropic_api_key)
        self._openai_key.set(config.openai_api_key)
        self._experience_file.set(config.experience_file)
        self._output_dir.set(config.output_directory)
        self._template_var.set(config.naming_template)
        self._conflict_var.set(config.conflict_mode)

    def _save(self):
        config = self._app.get_config()
        config.anthropic_api_key = self._anthropic_key.get()
        config.openai_api_key = self._openai_key.get()
        config.experience_file = self._experience_file.get()
        config.output_directory = self._output_dir.get()
        config.naming_template = self._template_var.get() or "{job_title} at {company}"
        config.conflict_mode = self._conflict_var.get()
        self._app.save_config(config)
        self._feedback.configure(text="Settings saved!")
        self.after(3000, lambda: self._feedback.configure(text=""))
