"""Dialog windows for the application."""

import os

import customtkinter as ctk


class ErrorDialog(ctk.CTkToplevel):
    """Modal error popup with title, message, and OK button."""

    def __init__(self, master, title: str, message: str):
        super().__init__(master)
        self.title(title)
        self.geometry("420x180")
        self.resizable(False, False)
        self.grab_set()
        self.transient(master)

        ctk.CTkLabel(
            self, text=message, wraplength=380, justify="left"
        ).pack(padx=20, pady=(20, 10), fill="x")

        ctk.CTkButton(self, text="OK", width=80, command=self.destroy).pack(
            pady=(0, 20)
        )

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 420) // 2
        y = master.winfo_y() + (master.winfo_height() - 180) // 2
        self.geometry(f"+{x}+{y}")


class HistoryDetailDialog(ctk.CTkToplevel):
    """Shows full details of a history entry."""

    def __init__(self, master, entry, on_rerun=None):
        super().__init__(master)
        self.title("Generation Details")
        self.geometry("650x550")
        self.resizable(True, True)
        self.grab_set()
        self.transient(master)

        # Header info
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            info_frame,
            text=f"{entry.job_title} at {entry.company}",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            info_frame, text=f"Generated: {entry.timestamp}", anchor="w"
        ).pack(fill="x", padx=10, pady=(0, 10))

        # Job description
        ctk.CTkLabel(self, text="Job Description:", anchor="w").pack(
            fill="x", padx=15, pady=(10, 2)
        )
        jd_box = ctk.CTkTextbox(self, height=150)
        jd_box.pack(fill="both", expand=True, padx=15, pady=(0, 5))
        jd_box.insert("1.0", entry.job_description)
        jd_box.configure(state="disabled")

        # Files
        ctk.CTkLabel(self, text="Generated Files:", anchor="w").pack(
            fill="x", padx=15, pady=(10, 2)
        )
        files_frame = ctk.CTkFrame(self)
        files_frame.pack(fill="x", padx=15, pady=(0, 10))

        for f in entry.files:
            if isinstance(f, dict):
                path = f.get("path", "")
                ftype = f.get("file_type", "")
                fmt = f.get("format", "")
                exists = os.path.isfile(path)
            else:
                path = f.path
                ftype = f.file_type
                fmt = f.format
                exists = os.path.isfile(path)

            icon = "  " if exists else "  "
            label_text = f"{icon} [{ftype}/{fmt}] {os.path.basename(path)}"
            ctk.CTkLabel(files_frame, text=label_text, anchor="w").pack(
                fill="x", padx=10, pady=1
            )

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        if on_rerun:
            ctk.CTkButton(
                btn_frame,
                text="Re-Run",
                width=100,
                command=lambda: self._do_rerun(on_rerun, entry),
            ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Close", width=80, command=self.destroy
        ).pack(side="right")

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 650) // 2
        y = master.winfo_y() + (master.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")

    def _do_rerun(self, callback, entry):
        self.destroy()
        callback(entry)
