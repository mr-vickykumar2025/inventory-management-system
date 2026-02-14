# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

from .. import database


class LoginMixin:
    def login_screen(self):
        self.clear_screen()
        if not database.has_any_user():
            self.first_run_setup_screen()
            return

        colors = self._theme()
        frame = tk.Frame(self.root, bg=colors["field_bg"], padx=40, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="User Login", font=("Segoe UI", 20, "bold"),
                 bg=colors["field_bg"], fg=colors["text"]).pack(pady=20)

        tk.Label(frame, text="Username", bg=colors["field_bg"], fg=colors["text"]).pack()
        self.username = tk.Entry(
            frame,
            width=30,
            bg=colors["panel_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.username.pack()

        tk.Label(frame, text="Password", bg=colors["field_bg"], fg=colors["text"]).pack()
        self.password = tk.Entry(
            frame,
            show="*",
            width=30,
            bg=colors["panel_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.password.pack()

        tk.Button(
            frame,
            text="Login",
            bg=colors["accent"],
            fg=colors["accent_text"],
            activebackground=colors["accent_hover"],
            activeforeground=colors["accent_text"],
            width=20,
            takefocus=True,
            command=self.login
        ).pack(pady=20)

        def _clear_fields():
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
            self.username.focus_set()

        self._configure_keyboard(
            focus_widget=self.username,
            enter=self.login,
            esc=_clear_fields,
            ctrl_n=_clear_fields
        )

    def first_run_setup_screen(self):
        self.clear_screen()

        colors = self._theme()
        frame = tk.Frame(self.root, bg=colors["field_bg"], padx=40, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="First-Time Setup", font=("Segoe UI", 20, "bold"),
                 bg=colors["field_bg"], fg=colors["text"]).pack(pady=10)
        tk.Label(frame, text="Create the first admin account",
                 bg=colors["field_bg"], fg=colors["muted"]).pack(pady=(0, 15))

        tk.Label(frame, text="Admin Username", bg=colors["field_bg"], fg=colors["text"]).pack()
        self.setup_username = tk.Entry(
            frame,
            width=30,
            bg=colors["panel_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.setup_username.insert(0, "admin")
        self.setup_username.pack()

        tk.Label(frame, text="Password", bg=colors["field_bg"], fg=colors["text"]).pack()
        self.setup_password = tk.Entry(
            frame,
            show="*",
            width=30,
            bg=colors["panel_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.setup_password.pack()

        tk.Label(frame, text="Confirm Password", bg=colors["field_bg"], fg=colors["text"]).pack()
        self.setup_confirm = tk.Entry(
            frame,
            show="*",
            width=30,
            bg=colors["panel_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.setup_confirm.pack()

        def _create_admin():
            username = self.setup_username.get().strip() or "admin"
            password = self.setup_password.get()
            confirm = self.setup_confirm.get()

            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            if not password:
                messagebox.showerror("Error", "Password is required")
                return
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return

            if not database.create_user(username, password, "admin"):
                messagebox.showerror("Error", "User already exists")
                return

            messagebox.showinfo("Success", "Admin created. Please login.")
            self.login_screen()

        tk.Button(
            frame,
            text="Create Admin",
            bg=colors["accent"],
            fg=colors["accent_text"],
            activebackground=colors["accent_hover"],
            activeforeground=colors["accent_text"],
            width=20,
            takefocus=True,
            command=_create_admin
        ).pack(pady=20)

        def _clear_fields():
            self.setup_username.delete(0, tk.END)
            self.setup_username.insert(0, "admin")
            self.setup_password.delete(0, tk.END)
            self.setup_confirm.delete(0, tk.END)
            self.setup_username.focus_set()

        self._configure_keyboard(
            focus_widget=self.setup_username,
            enter=_create_admin,
            esc=_clear_fields,
            ctrl_n=_clear_fields
        )

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        role = database.validate_user(username, password)
        if role:
            self.current_user = username
            self.current_role = role
            self._log_action("LOGIN", f"role={role}")
            self.dashboard()
        else:
            messagebox.showerror("Error", "Invalid Login")
