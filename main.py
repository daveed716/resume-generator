#!/usr/bin/env python3
"""Entry point for the Resume & Cover Letter Generator GUI."""

import customtkinter as ctk

from gui.app import App


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
