"""Root application window with tabbed interface."""

import customtkinter as ctk

from core.config_manager import load_config, save_config
from core.models import AppConfig
from gui.dialogs import ErrorDialog
from gui.experience_tab import ExperienceTab
from gui.generate_tab import GenerateTab
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Resume & Cover Letter Generator")
        self.geometry("1100x750")
        self.minsize(900, 640)

        # Load persisted config
        self._config = load_config()

        # Tab view — command fires on every tab switch
        self._tabview = ctk.CTkTabview(self, command=self._on_tab_change)
        self._tabview.pack(fill="both", expand=True, padx=10, pady=10)

        for name in ("Generate", "History", "Experience", "Settings"):
            self._tabview.add(name)

        # Create tabs
        self._generate_tab = GenerateTab(self._tabview.tab("Generate"), self)
        self._generate_tab.pack(fill="both", expand=True)

        self._history_tab = HistoryTab(self._tabview.tab("History"), self)
        self._history_tab.pack(fill="both", expand=True)

        self._experience_tab = ExperienceTab(self._tabview.tab("Experience"), self)
        self._experience_tab.pack(fill="both", expand=True)

        self._settings_tab = SettingsTab(self._tabview.tab("Settings"), self)
        self._settings_tab.pack(fill="both", expand=True)

        # Populate settings form and initial loads
        self._settings_tab.load_config(self._config)
        self._history_tab.refresh()
        # Load experience data if file is already configured
        if self._config.experience_file:
            self._experience_tab.load()

    # --- Tab switch handler ---

    def _on_tab_change(self):
        tab = self._tabview.get()
        if tab == "History":
            self._history_tab.refresh()
        elif tab == "Experience":
            self._experience_tab.load()

    # --- Controller methods used by tabs ---

    def get_config(self) -> AppConfig:
        return self._config

    def save_config(self, config: AppConfig):
        self._config = config
        save_config(config)

    def show_error(self, title: str, message: str):
        ErrorDialog(self, title, message)

    def refresh_history(self):
        self._history_tab.refresh()

    def load_for_rerun(self, entry):
        """Load a history entry's job description into Generate tab and switch to it."""
        self._generate_tab.set_job_description(entry.job_description)
        self._tabview.set("Generate")
