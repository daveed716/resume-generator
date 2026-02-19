"""Experience editor tab — view and modify the structured experience JSON file."""

import json
import os

import customtkinter as ctk


# ---------------------------------------------------------------------------
# Leaf widgets
# ---------------------------------------------------------------------------

class _BulletCard(ctk.CTkFrame):
    """Single editable bullet: label, text (multiline), tags."""

    def __init__(self, master, data: dict, on_delete):
        super().__init__(master, border_width=1, corner_radius=4)

        # --- Row 1: label + delete button ---
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=6, pady=(6, 2))

        ctk.CTkLabel(top, text="Label:", width=45, anchor="w").pack(side="left")
        self._label_var = ctk.StringVar(value=data.get("label", ""))
        ctk.CTkEntry(top, textvariable=self._label_var, height=28).pack(
            side="left", fill="x", expand=True, padx=(4, 4))
        ctk.CTkButton(
            top, text="✕", width=28, height=28,
            fg_color="transparent", hover_color="#661111",
            command=lambda: (self.destroy(), on_delete and on_delete()),
        ).pack(side="right")

        # --- Row 2: bullet text (multiline) ---
        mid = ctk.CTkFrame(self, fg_color="transparent")
        mid.pack(fill="x", padx=6, pady=2)
        ctk.CTkLabel(mid, text="Text:", width=45, anchor="nw").pack(
            side="left", anchor="n", pady=3)
        self._text_box = ctk.CTkTextbox(mid, height=58, wrap="word")
        self._text_box.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self._text_box.insert("1.0", data.get("text", ""))

        # --- Row 3: tags (comma-separated) ---
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=6, pady=(2, 6))
        ctk.CTkLabel(bot, text="Tags:", width=45, anchor="w").pack(side="left")
        self._tags_var = ctk.StringVar(value=", ".join(data.get("tags", [])))
        ctk.CTkEntry(
            bot, textvariable=self._tags_var, height=28,
            placeholder_text="tag1, tag2, tag3, ...",
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def collect(self) -> dict:
        return {
            "label": self._label_var.get().strip(),
            "text": self._text_box.get("1.0", "end").strip(),
            "tags": [t.strip() for t in self._tags_var.get().split(",") if t.strip()],
        }


class _RoleBlock(ctk.CTkFrame):
    """Editable role: title + list of bullet cards."""

    def __init__(self, master, data: dict, on_delete):
        super().__init__(master, border_width=1, corner_radius=6)
        self._bullet_cards: list[_BulletCard] = []

        # --- Role header ---
        hdr = ctk.CTkFrame(self, fg_color="#1e3a2e", corner_radius=5)
        hdr.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(hdr, text="Role:", font=ctk.CTkFont(weight="bold"),
                     width=45).pack(side="left", padx=(8, 2))
        self._title_var = ctk.StringVar(value=data.get("title", ""))
        ctk.CTkEntry(hdr, textvariable=self._title_var, height=28).pack(
            side="left", fill="x", expand=True, padx=(4, 4))
        ctk.CTkButton(
            hdr, text="+ Bullet", width=80, height=28,
            command=self._add_bullet,
        ).pack(side="right", padx=4, pady=5)
        ctk.CTkButton(
            hdr, text="Delete Role", width=90, height=28,
            fg_color="gray40", hover_color="#553333",
            command=lambda: (self.destroy(), on_delete and on_delete()),
        ).pack(side="right", padx=(4, 2), pady=5)

        # --- Bullets container ---
        self._bullets_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._bullets_frame.pack(fill="x", padx=10, pady=(4, 8))

        for b in data.get("bullets", []):
            self._add_bullet(b)

    def _add_bullet(self, data: dict | None = None):
        data = data or {"label": "", "text": "", "tags": []}
        card = _BulletCard(self._bullets_frame, data, on_delete=None)
        card.pack(fill="x", pady=3)
        self._bullet_cards.append(card)

    def collect(self) -> dict:
        return {
            "title": self._title_var.get().strip(),
            "bullets": [
                c.collect() for c in self._bullet_cards if c.winfo_exists()
            ],
        }


class _CompanyBlock(ctk.CTkFrame):
    """Editable company: name, dates, and a list of role blocks."""

    def __init__(self, master, data: dict, on_delete):
        super().__init__(master, border_width=2, corner_radius=8)
        self._role_blocks: list[_RoleBlock] = []

        # --- Company header ---
        hdr = ctk.CTkFrame(self, fg_color="#1a2e4a", corner_radius=6)
        hdr.pack(fill="x", padx=2, pady=2)

        ctk.CTkLabel(
            hdr, text="Company:", font=ctk.CTkFont(size=12, weight="bold"),
            width=70,
        ).pack(side="left", padx=(8, 2))
        self._name_var = ctk.StringVar(value=data.get("company", ""))
        ctk.CTkEntry(hdr, textvariable=self._name_var, height=30, width=200).pack(
            side="left", padx=(4, 8))

        ctk.CTkLabel(hdr, text="Dates:").pack(side="left")
        self._dates_var = ctk.StringVar(value=data.get("dates", ""))
        ctk.CTkEntry(hdr, textvariable=self._dates_var, height=30, width=160).pack(
            side="left", padx=(4, 8))

        ctk.CTkButton(
            hdr, text="Delete Company", width=120, height=30,
            fg_color="#992222", hover_color="#771111",
            command=lambda: (self.destroy(), on_delete and on_delete()),
        ).pack(side="right", padx=8, pady=6)
        ctk.CTkButton(
            hdr, text="+ Role", width=70, height=30,
            command=self._add_role,
        ).pack(side="right", padx=4, pady=6)

        # --- Roles container ---
        self._roles_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._roles_frame.pack(fill="x", padx=12, pady=(6, 10))

        for role in data.get("roles", []):
            self._add_role(role)

    def _add_role(self, data: dict | None = None):
        data = data or {"title": "", "bullets": []}
        block = _RoleBlock(self._roles_frame, data, on_delete=None)
        block.pack(fill="x", pady=5)
        self._role_blocks.append(block)

    def collect(self) -> dict:
        return {
            "company": self._name_var.get().strip(),
            "dates": self._dates_var.get().strip(),
            "roles": [
                b.collect() for b in self._role_blocks if b.winfo_exists()
            ],
        }


# ---------------------------------------------------------------------------
# Section frames (one per sub-tab)
# ---------------------------------------------------------------------------

class _ProfileSection(ctk.CTkFrame):
    """Contact info, default headline, and default summary."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Contact
        ctk.CTkLabel(scroll, text="Contact Information",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 8))

        contact_frame = ctk.CTkFrame(scroll)
        contact_frame.pack(fill="x", pady=(0, 15))

        self._name_var = ctk.StringVar()
        self._address_var = ctk.StringVar()
        self._phone_var = ctk.StringVar()
        self._email_var = ctk.StringVar()

        fields = [
            ("Name:", self._name_var),
            ("Address:", self._address_var),
            ("Phone:", self._phone_var),
            ("Email:", self._email_var),
        ]
        for label_text, var in fields:
            row = ctk.CTkFrame(contact_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=label_text, width=70, anchor="w").pack(side="left")
            ctk.CTkEntry(row, textvariable=var).pack(side="left", fill="x", expand=True)

        # Headline
        ctk.CTkLabel(scroll, text="Default Headline",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 4))
        self._headline_var = ctk.StringVar()
        ctk.CTkEntry(scroll, textvariable=self._headline_var).pack(
            fill="x", pady=(0, 15))

        # Summary
        ctk.CTkLabel(scroll, text="Default Summary",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 4))
        self._summary_box = ctk.CTkTextbox(scroll, height=130, wrap="word")
        self._summary_box.pack(fill="x", pady=(0, 10))

    def load(self, data: dict):
        c = data.get("contact", {})
        self._name_var.set(c.get("name", ""))
        self._address_var.set(c.get("address", ""))
        self._phone_var.set(c.get("phone", ""))
        self._email_var.set(c.get("email", ""))
        self._headline_var.set(data.get("default_headline", ""))
        self._summary_box.delete("1.0", "end")
        self._summary_box.insert("1.0", data.get("default_summary", ""))

    def collect(self) -> dict:
        return {
            "contact": {
                "name": self._name_var.get().strip(),
                "address": self._address_var.get().strip(),
                "phone": self._phone_var.get().strip(),
                "email": self._email_var.get().strip(),
            },
            "default_headline": self._headline_var.get().strip(),
            "default_summary": self._summary_box.get("1.0", "end").strip(),
        }


class _ExperienceSection(ctk.CTkFrame):
    """Editable list of companies with roles and bullets."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._company_blocks: list[_CompanyBlock] = []

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=5, pady=(5, 2))
        ctk.CTkButton(
            toolbar, text="+ Add Company", width=140,
            command=self._add_company,
        ).pack(side="left")
        ctk.CTkLabel(
            toolbar, text="Changes saved when you click Save at the top.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=15)

        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def load(self, experience: list):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._company_blocks.clear()
        for company in experience:
            self._add_company(company)

    def _add_company(self, data: dict | None = None):
        data = data or {"company": "", "dates": "", "roles": []}
        block = _CompanyBlock(self._scroll, data, on_delete=None)
        block.pack(fill="x", pady=6, padx=5)
        self._company_blocks.append(block)

    def collect(self) -> list:
        return [b.collect() for b in self._company_blocks if b.winfo_exists()]


class _CategoryRow(ctk.CTkFrame):
    """One skill category: name + comma-separated skills."""

    def __init__(self, master, name: str, skills: list[str], on_delete):
        super().__init__(master, border_width=1, corner_radius=5)

        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(8, 3))
        ctk.CTkLabel(row1, text="Category:", width=70, anchor="w").pack(side="left")
        self._cat_var = ctk.StringVar(value=name)
        ctk.CTkEntry(row1, textvariable=self._cat_var, width=200, height=28).pack(
            side="left", padx=(4, 4))
        ctk.CTkButton(
            row1, text="Delete", width=65, height=28,
            fg_color="gray40", hover_color="#553333",
            command=lambda: (self.destroy(), on_delete and on_delete()),
        ).pack(side="right")

        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkLabel(row2, text="Skills:", width=70, anchor="w").pack(side="left")
        self._skills_var = ctk.StringVar(value=", ".join(skills))
        ctk.CTkEntry(
            row2, textvariable=self._skills_var, height=28,
            placeholder_text="Skill A, Skill B, Skill C, ...",
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def collect(self) -> tuple[str, list[str]]:
        cat = self._cat_var.get().strip()
        skills = [s.strip() for s in self._skills_var.get().split(",") if s.strip()]
        return cat, skills


class _SkillsSection(ctk.CTkFrame):
    """Dictionary of skill categories with editable skill lists."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._cat_rows: list[_CategoryRow] = []

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=5, pady=(5, 2))
        ctk.CTkButton(
            toolbar, text="+ Add Category", width=140, command=self._add_category
        ).pack(side="left")

        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def load(self, skills: dict):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._cat_rows.clear()
        for name, skill_list in skills.items():
            self._add_category(name, skill_list)

    def _add_category(self, name: str = "", skills: list | None = None):
        skills = skills or []
        row = _CategoryRow(self._scroll, name, skills, on_delete=None)
        row.pack(fill="x", pady=4, padx=5)
        self._cat_rows.append(row)

    def collect(self) -> dict:
        result = {}
        for row in self._cat_rows:
            if row.winfo_exists():
                cat, skills = row.collect()
                if cat:
                    result[cat] = skills
        return result


class _OtherSection(ctk.CTkFrame):
    """Education, certifications, volunteering, and cover letter example."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._cert_entries: list[tuple] = []
        self._vol_entries: list[tuple] = []

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Education ---
        ctk.CTkLabel(scroll, text="Education",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 6))

        edu = ctk.CTkFrame(scroll)
        edu.pack(fill="x", pady=(0, 15))

        self._degree_var = ctk.StringVar()
        self._school_var = ctk.StringVar()
        self._edu_date_var = ctk.StringVar()

        for lbl, var in [("Degree:", self._degree_var),
                         ("School:", self._school_var),
                         ("Date:", self._edu_date_var)]:
            r = ctk.CTkFrame(edu, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(r, text=lbl, width=65, anchor="w").pack(side="left")
            ctk.CTkEntry(r, textvariable=var).pack(side="left", fill="x", expand=True)

        # --- Certifications ---
        ctk.CTkLabel(scroll, text="Certifications",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 4))
        ctk.CTkButton(scroll, text="+ Add Certification", width=155,
                      command=self._add_cert).pack(anchor="w", pady=(0, 6))
        self._certs_frame = ctk.CTkFrame(scroll)
        self._certs_frame.pack(fill="x", pady=(0, 15))

        # --- Volunteering ---
        ctk.CTkLabel(scroll, text="Volunteering & Leadership",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 4))
        ctk.CTkButton(scroll, text="+ Add Entry", width=120,
                      command=self._add_vol).pack(anchor="w", pady=(0, 6))
        self._vol_frame = ctk.CTkFrame(scroll)
        self._vol_frame.pack(fill="x", pady=(0, 15))

        # --- Cover Letter Example ---
        ctk.CTkLabel(scroll, text="Cover Letter Example",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(
            fill="x", pady=(5, 4))
        ctk.CTkLabel(
            scroll,
            text="Used as style/tone reference only — not included verbatim in output.",
            text_color="gray", font=ctk.CTkFont(size=11), anchor="w",
        ).pack(fill="x", pady=(0, 4))
        self._cl_box = ctk.CTkTextbox(scroll, height=220, wrap="word")
        self._cl_box.pack(fill="x", pady=(0, 10))

    # -- Certification helpers --

    def _add_cert(self, data: dict | None = None):
        data = data or {"name": "", "issuer": ""}
        card = ctk.CTkFrame(self._certs_frame, border_width=1, corner_radius=5)
        card.pack(fill="x", pady=3, padx=5)

        name_var = ctk.StringVar(value=data.get("name", ""))
        issuer_var = ctk.StringVar(value=data.get("issuer", ""))

        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=8, pady=(8, 2))
        ctk.CTkLabel(r1, text="Name:", width=55, anchor="w").pack(side="left")
        ctk.CTkEntry(r1, textvariable=name_var, height=28).pack(
            side="left", fill="x", expand=True, padx=(4, 4))
        ctk.CTkButton(
            r1, text="✕", width=28, height=28,
            fg_color="transparent", hover_color="#661111",
            command=lambda: self._remove_card(card, self._cert_entries),
        ).pack(side="right")

        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=8, pady=(2, 8))
        ctk.CTkLabel(r2, text="Issuer:", width=55, anchor="w").pack(side="left")
        ctk.CTkEntry(r2, textvariable=issuer_var, height=28).pack(
            side="left", fill="x", expand=True)

        self._cert_entries.append((card, name_var, issuer_var))

    # -- Volunteering helpers --

    def _add_vol(self, data: dict | None = None):
        data = data or {"org": "", "dates": "", "role": "", "location": ""}
        card = ctk.CTkFrame(self._vol_frame, border_width=1, corner_radius=5)
        card.pack(fill="x", pady=3, padx=5)

        org_var = ctk.StringVar(value=data.get("org", ""))
        dates_var = ctk.StringVar(value=data.get("dates", ""))
        role_var = ctk.StringVar(value=data.get("role", ""))
        loc_var = ctk.StringVar(value=data.get("location", ""))

        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=8, pady=(8, 2))
        ctk.CTkLabel(r1, text="Org:", width=70, anchor="w").pack(side="left")
        ctk.CTkEntry(r1, textvariable=org_var, height=28).pack(
            side="left", fill="x", expand=True, padx=(4, 4))
        ctk.CTkButton(
            r1, text="✕", width=28, height=28,
            fg_color="transparent", hover_color="#661111",
            command=lambda: self._remove_card(card, self._vol_entries),
        ).pack(side="right")

        for lbl, var in [("Dates:", dates_var), ("Role:", role_var), ("Location:", loc_var)]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=lbl, width=70, anchor="w").pack(side="left")
            ctk.CTkEntry(row, textvariable=var, height=28).pack(
                side="left", fill="x", expand=True)

        ctk.CTkFrame(card, height=6, fg_color="transparent").pack()
        self._vol_entries.append((card, org_var, dates_var, role_var, loc_var))

    def _remove_card(self, card, entries_list):
        card.destroy()
        entries_list[:] = [e for e in entries_list if e[0].winfo_exists()]

    def load(self, data: dict):
        # Clear certs
        for w in self._certs_frame.winfo_children():
            w.destroy()
        self._cert_entries.clear()
        # Clear vol
        for w in self._vol_frame.winfo_children():
            w.destroy()
        self._vol_entries.clear()

        edu = data.get("education", {})
        self._degree_var.set(edu.get("degree", ""))
        self._school_var.set(edu.get("school", ""))
        self._edu_date_var.set(edu.get("date", ""))

        for cert in data.get("certifications", []):
            self._add_cert(cert)

        for vol in data.get("volunteering", []):
            self._add_vol(vol)

        self._cl_box.delete("1.0", "end")
        self._cl_box.insert("1.0", data.get("cover_letter_example", ""))

    def collect(self) -> dict:
        return {
            "education": {
                "degree": self._degree_var.get().strip(),
                "school": self._school_var.get().strip(),
                "date": self._edu_date_var.get().strip(),
            },
            "certifications": [
                {"name": nv.get().strip(), "issuer": iv.get().strip()}
                for (card, nv, iv) in self._cert_entries if card.winfo_exists()
            ],
            "volunteering": [
                {
                    "org": ov.get().strip(),
                    "dates": dv.get().strip(),
                    "role": rv.get().strip(),
                    "location": lv.get().strip(),
                }
                for (card, ov, dv, rv, lv) in self._vol_entries if card.winfo_exists()
            ],
            "cover_letter_example": self._cl_box.get("1.0", "end").strip(),
        }


# ---------------------------------------------------------------------------
# Main tab
# ---------------------------------------------------------------------------

class ExperienceTab(ctk.CTkFrame):
    """Tab for viewing and editing experience_data.json."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self._app = app
        self._data: dict = {}
        self._file_path: str = ""

        # --- Top bar ---
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            topbar, text="Experience Editor",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

        self._status_label = ctk.CTkLabel(topbar, text="", text_color="gray")
        self._status_label.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            topbar, text="Save", width=80, command=self._save,
        ).pack(side="right")
        ctk.CTkButton(
            topbar, text="Reload", width=80, command=self.load,
        ).pack(side="right", padx=(0, 6))

        # --- Sub-tabs ---
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for name in ("Profile", "Experience", "Skills", "Other"):
            self._tabs.add(name)

        self._profile = _ProfileSection(self._tabs.tab("Profile"))
        self._profile.pack(fill="both", expand=True)

        self._experience = _ExperienceSection(self._tabs.tab("Experience"))
        self._experience.pack(fill="both", expand=True)

        self._skills = _SkillsSection(self._tabs.tab("Skills"))
        self._skills.pack(fill="both", expand=True)

        self._other = _OtherSection(self._tabs.tab("Other"))
        self._other.pack(fill="both", expand=True)

    # --- Public ---

    def load(self):
        """Load (or reload) data from the configured experience file."""
        config = self._app.get_config()
        path = config.experience_file
        if not path or not os.path.isfile(path):
            self._set_status(
                "Experience file not configured. Set it in Settings.", "orange"
            )
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._data = data
            self._file_path = path
            self._profile.load(data)
            self._experience.load(data.get("experience", []))
            self._skills.load(data.get("skills", {}))
            self._other.load(data)
            self._set_status(f"Loaded: {os.path.basename(path)}", "green")
        except Exception as e:
            self._set_status(f"Error loading: {e}", "#ee4444")

    # --- Private ---

    def _save(self):
        if not self._file_path:
            self._set_status("No file loaded. Set experience file in Settings.", "orange")
            return
        try:
            # Merge all sections back into the original dict (preserves unknown keys)
            self._data.update(self._profile.collect())
            self._data["experience"] = self._experience.collect()
            self._data["skills"] = self._skills.collect()
            self._data.update(self._other.collect())

            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

            self._set_status("Saved successfully!", "green")
            self.after(4000, lambda: self._set_status("", "gray"))
        except Exception as e:
            self._set_status(f"Error saving: {e}", "#ee4444")

    def _set_status(self, msg: str, color: str = "gray"):
        self._status_label.configure(text=msg, text_color=color)
