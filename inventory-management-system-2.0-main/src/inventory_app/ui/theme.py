# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

THEMES = {
    "dark": {
        "root_bg": "#1e1e1e",
        "panel_bg": "#1e1e1e",
        "sidebar_bg": "#252526",
        "card_bg": "#252526",
        "border": "#3c3c3c",
        "text": "#f5f5f5",
        "muted": "#cfcfcf",
        "field_bg": "#2b2b2b",
        "field_fg": "#ffffff",
        "accent": "#00b894",
        "accent_hover": "#00a884",
        "accent_text": "#ffffff",
        "danger": "#d63031",
        "danger_text": "#ffffff",
        "warning": "#fdcb6e",
        "warning_text": "#1f1f1f",
        "success": "#00ffcc",
        "banner_bg": "#3b1d1d",
        "banner_text": "#ff6666",
        "link": "#00ffcc",
    },
    "light": {
        "root_bg": "#f5f5f5",
        "panel_bg": "#ffffff",
        "sidebar_bg": "#f0f0f0",
        "card_bg": "#ffffff",
        "border": "#d6d6d6",
        "text": "#1f1f1f",
        "muted": "#5e5e5e",
        "field_bg": "#ffffff",
        "field_fg": "#1f1f1f",
        "accent": "#0a7d6c",
        "accent_hover": "#086f60",
        "accent_text": "#ffffff",
        "danger": "#d32f2f",
        "danger_text": "#ffffff",
        "warning": "#fbc02d",
        "warning_text": "#1f1f1f",
        "success": "#2e7d32",
        "banner_bg": "#fdecea",
        "banner_text": "#b71c1c",
        "link": "#0a7d6c",
    },
}


class ThemeMixin:
    def _theme(self):
        return THEMES.get(self.theme, THEMES["dark"])

    def _apply_root_theme(self):
        colors = self._theme()
        self.root.configure(bg=colors["root_bg"])
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TCombobox",
            fieldbackground=colors["field_bg"],
            background=colors["field_bg"],
            foreground=colors["field_fg"]
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", colors["field_bg"])],
            foreground=[("readonly", colors["field_fg"])]
        )

    def _set_theme(self, theme_name):
        if not isinstance(theme_name, str):
            return
        key = theme_name.lower()
        if key not in THEMES or key == self.theme:
            return
        self.theme = key
        self._apply_root_theme()
        if self.current_user:
            self.dashboard()
        else:
            self.login_screen()

    def _toggle_theme(self):
        next_theme = "light" if self.theme == "dark" else "dark"
        self._set_theme(next_theme)

    def _on_theme_change(self, event=None):
        if hasattr(self, "theme_var"):
            self._set_theme(self.theme_var.get())
