"""Generate tab: job description input, options, progress, and generation."""

import os
import threading

import customtkinter as ctk

from core.generator import generate_application, load_experience_data
from core.history_manager import add_history_entry, create_history_entry
from core.models import GenerationOptions
from gui.widgets import StatusLog


class GenerateTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self._app = app
        self._generating = False

        # --- Job Description ---
        ctk.CTkLabel(
            self,
            text="Job Description",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 5))

        self._jd_textbox = ctk.CTkTextbox(self, height=180)
        self._jd_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # --- Options row ---
        opts_frame = ctk.CTkFrame(self, fg_color="transparent")
        opts_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Document types
        ctk.CTkLabel(opts_frame, text="Documents:").pack(side="left", padx=(0, 5))
        self._resume_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Resume", variable=self._resume_var
        ).pack(side="left", padx=(0, 10))

        self._cover_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Cover Letter", variable=self._cover_var
        ).pack(side="left", padx=(0, 20))

        # Formats
        ctk.CTkLabel(opts_frame, text="Formats:").pack(side="left", padx=(0, 5))
        self._docx_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="DOCX", variable=self._docx_var
        ).pack(side="left", padx=(0, 10))

        self._pdf_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="PDF", variable=self._pdf_var
        ).pack(side="left", padx=(0, 10))

        self._txt_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="TXT", variable=self._txt_var
        ).pack(side="left")

        # --- Generate button + progress ---
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=15, pady=(0, 5))

        self._generate_btn = ctk.CTkButton(
            ctrl_frame,
            text="Generate",
            width=140,
            command=self._on_generate,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_btn.pack(side="left")

        self._progress = ctk.CTkProgressBar(ctrl_frame, mode="indeterminate")
        # Hidden initially — packed when generation starts

        # --- Status log ---
        ctk.CTkLabel(
            self,
            text="Progress",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(5, 2))

        self._log = StatusLog(self, height=120)
        self._log.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def set_job_description(self, text: str):
        """Load a job description (e.g. from history re-run)."""
        self._jd_textbox.delete("1.0", "end")
        self._jd_textbox.insert("1.0", text)

    def _get_options(self) -> GenerationOptions:
        return GenerationOptions(
            generate_resume=self._resume_var.get(),
            generate_cover_letter=self._cover_var.get(),
            format_docx=self._docx_var.get(),
            format_pdf=self._pdf_var.get(),
            format_txt=self._txt_var.get(),
        )

    def _validate(self) -> str | None:
        """Return an error message string, or None if valid."""
        jd = self._jd_textbox.get("1.0", "end").strip()
        if not jd:
            return "Please paste a job description."

        opts = self._get_options()
        if not opts.generate_resume and not opts.generate_cover_letter:
            return "Select at least one document type (Resume or Cover Letter)."
        if not opts.format_docx and not opts.format_pdf and not opts.format_txt:
            return "Select at least one output format (DOCX, PDF, or TXT)."

        config = self._app.get_config()
        if not config.anthropic_api_key:
            return "Anthropic API key is not set. Go to Settings."
        if not config.openai_api_key:
            return "OpenAI API key is not set. Go to Settings."
        if not config.experience_file or not os.path.isfile(config.experience_file):
            return "Experience data file not found. Check Settings."
        if not config.output_directory:
            return "Output directory is not set. Check Settings."

        return None

    def _on_generate(self):
        if self._generating:
            return

        error = self._validate()
        if error:
            self._app.show_error("Validation Error", error)
            return

        self._generating = True
        self._generate_btn.configure(state="disabled")
        self._log.clear()
        self._progress.pack(side="left", fill="x", expand=True, padx=(15, 0))
        self._progress.start()

        config = self._app.get_config()
        jd = self._jd_textbox.get("1.0", "end").strip()
        options = self._get_options()

        thread = threading.Thread(
            target=self._run_generation,
            args=(jd, options, config),
            daemon=True,
        )
        thread.start()

    def _status(self, msg: str):
        """Thread-safe status update."""
        self.after(0, lambda: self._log.append(msg))

    def _run_generation(self, jd, options, config):
        try:
            exp_data = load_experience_data(config.experience_file)
            self._status(
                f"Loaded experience data: {len(exp_data['experience'])} companies"
            )

            data, files = generate_application(
                job_description=jd,
                exp_data=exp_data,
                options=options,
                anthropic_key=config.anthropic_api_key,
                openai_key=config.openai_api_key,
                output_dir=config.output_directory,
                naming_template=config.naming_template,
                conflict_mode=config.conflict_mode,
                on_status=self._status,
            )

            # Save to history
            entry = create_history_entry(
                job_title=data.get("job_title", "Role"),
                company=data.get("company", "Company"),
                job_description=jd,
                options=options,
                files=files,
            )
            add_history_entry(entry)
            self._status("History entry saved.")
            self.after(0, self._app.refresh_history)

        except Exception as e:
            self._status(f"ERROR: {e}")
            self.after(0, lambda: self._app.show_error("Generation Failed", str(e)))
        finally:
            self.after(0, self._generation_done)

    def _generation_done(self):
        self._generating = False
        self._generate_btn.configure(state="normal")
        self._progress.stop()
        self._progress.pack_forget()
