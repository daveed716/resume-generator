"""Generate tab: job description input, options, progress, and generation."""

import os
import threading

import customtkinter as ctk

from core.generator import generate_application, load_experience_data
from core.history_manager import add_history_entry, create_history_entry
from core.linkedin import fetch_linkedin_job, format_for_textbox
from core.models import GenerationOptions
from gui.widgets import StatusLog


class GenerateTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self._app = app
        self._generating = False
        self._fetching = False

        # --- LinkedIn URL row ---
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.pack(fill="x", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            url_frame,
            text="LinkedIn URL:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left", padx=(0, 8))

        self._url_var = ctk.StringVar()
        self._url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self._url_var,
            placeholder_text="https://www.linkedin.com/jobs/view/...",
        )
        self._url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._fetch_btn = ctk.CTkButton(
            url_frame,
            text="Fetch",
            width=70,
            command=self._on_fetch,
        )
        self._fetch_btn.pack(side="left", padx=(0, 8))

        self._fetch_status = ctk.CTkLabel(
            url_frame, text="", text_color="gray", width=220, anchor="w"
        )
        self._fetch_status.pack(side="left")

        # Subtle divider
        ctk.CTkFrame(self, height=1, fg_color="#444").pack(
            fill="x", padx=15, pady=(6, 0)
        )

        # --- Job Description ---
        ctk.CTkLabel(
            self,
            text="Job Description",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=15, pady=(8, 4))

        self._jd_textbox = ctk.CTkTextbox(self, height=180)
        self._jd_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # --- Options row ---
        opts_frame = ctk.CTkFrame(self, fg_color="transparent")
        opts_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(opts_frame, text="Documents:").pack(side="left", padx=(0, 5))
        self._resume_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Resume", variable=self._resume_var
        ).pack(side="left", padx=(0, 10))

        self._cover_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opts_frame, text="Cover Letter", variable=self._cover_var
        ).pack(side="left", padx=(0, 20))

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

    # --- Public ---

    def set_job_description(self, text: str):
        """Load a job description (e.g. from history re-run)."""
        self._jd_textbox.delete("1.0", "end")
        self._jd_textbox.insert("1.0", text)

    # --- LinkedIn fetch ---

    def _on_fetch(self):
        if self._fetching or self._generating:
            return

        url = self._url_var.get().strip()
        if not url:
            self._set_fetch_status("Enter a LinkedIn job URL first.", "orange")
            return

        self._fetching = True
        self._fetch_btn.configure(state="disabled")
        self._generate_btn.configure(state="disabled")
        self._set_fetch_status("Fetching...", "gray")

        threading.Thread(
            target=self._run_fetch,
            args=(url,),
            daemon=True,
        ).start()

    def _run_fetch(self, url: str):
        try:
            job_data = fetch_linkedin_job(url, on_status=self._fetch_status_threadsafe)
            text = format_for_textbox(job_data)

            title = job_data.get("job_title", "")
            company = job_data.get("company", "")
            label = f"{title} at {company}" if title and company else (title or company or "done")

            self.after(0, lambda: self._on_fetch_success(text, label))
        except Exception as e:
            msg = str(e)
            self.after(0, lambda: self._on_fetch_error(msg))

    def _fetch_status_threadsafe(self, msg: str):
        self.after(0, lambda: self._set_fetch_status(msg, "gray"))

    def _on_fetch_success(self, text: str, label: str):
        self.set_job_description(text)
        self._set_fetch_status(f"Fetched: {label}", "green")
        self._fetch_done()

    def _on_fetch_error(self, msg: str):
        # Show first line in the status label; full detail in the log
        first_line = msg.splitlines()[0]
        self._set_fetch_status(f"Error: {first_line}", "#ee4444")
        self._log.append(f"LinkedIn fetch error: {msg}")
        self._fetch_done()

    def _fetch_done(self):
        self._fetching = False
        self._fetch_btn.configure(state="normal")
        self._generate_btn.configure(state="normal")

    def _set_fetch_status(self, msg: str, color: str):
        self._fetch_status.configure(text=msg, text_color=color)

    # --- Options ---

    def _get_options(self) -> GenerationOptions:
        return GenerationOptions(
            generate_resume=self._resume_var.get(),
            generate_cover_letter=self._cover_var.get(),
            format_docx=self._docx_var.get(),
            format_pdf=self._pdf_var.get(),
            format_txt=self._txt_var.get(),
        )

    # --- Validation ---

    def _validate(self) -> str | None:
        jd = self._jd_textbox.get("1.0", "end").strip()
        if not jd:
            return "Please paste a job description or fetch one from a LinkedIn URL."

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

    # --- Generation ---

    def _on_generate(self):
        if self._generating or self._fetching:
            return

        error = self._validate()
        if error:
            self._app.show_error("Validation Error", error)
            return

        self._generating = True
        self._generate_btn.configure(state="disabled")
        self._fetch_btn.configure(state="disabled")
        self._log.clear()
        self._progress.pack(side="left", fill="x", expand=True, padx=(15, 0))
        self._progress.start()

        config = self._app.get_config()
        jd = self._jd_textbox.get("1.0", "end").strip()
        options = self._get_options()

        threading.Thread(
            target=self._run_generation,
            args=(jd, options, config),
            daemon=True,
        ).start()

    def _status(self, msg: str):
        """Thread-safe status update to the log."""
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
        self._fetch_btn.configure(state="normal")
        self._progress.stop()
        self._progress.pack_forget()
