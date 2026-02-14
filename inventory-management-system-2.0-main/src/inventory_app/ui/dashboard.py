# -*- coding: utf-8 -*-
import tkinter as tk


class DashboardMixin:
    def dashboard(self):
        self.clear_screen()

        colors = self._theme()
        sidebar = tk.Frame(self.root, bg=colors["sidebar_bg"], width=250)
        sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(self.root, bg=colors["panel_bg"])
        self.main.pack(side="right", fill="both", expand=True)

        btn = {
            "width": 20,
            "bg": colors["accent"],
            "fg": colors["accent_text"],
            "activebackground": colors["accent_hover"],
            "activeforeground": colors["accent_text"],
            "takefocus": True
        }

        tk.Label(sidebar, text="Inventory System",
                 font=("Segoe UI", 18, "bold"),
                 bg=colors["sidebar_bg"], fg=colors["text"]).pack(pady=20)

        if self.current_user and self.current_role:
            tk.Label(
                sidebar,
                text=f"{self.current_user} ({self.current_role.capitalize()})",
                font=("Segoe UI", 10),
                bg=colors["sidebar_bg"],
                fg=colors["muted"]
            ).pack(pady=5)

        role = self.current_role or "cashier"
        actions = []

        if role in ("admin", "manager"):
            actions.extend([
                ("Add Product", self.add_product_screen),
                ("Inventory", self.inventory_screen),
                ("Sales", self.sales_screen),
                ("Sales History", self.sales_history_screen),
                ("Low Stock", self.low_stock_screen),
                ("Audit Log", self.audit_log_screen),
            ])
            if role == "admin":
                actions.extend([
                    ("Backup Database", self.backup_database),
                    ("Restore Database", self.restore_database),
                ])
        else:
            actions.append(("Sales", self.sales_screen))

        self.sidebar_buttons = []
        for label, cmd in actions:
            button = tk.Button(sidebar, text=label, command=cmd, **btn)
            button.pack(pady=8)
            self.sidebar_buttons.append(button)

        logout_btn = tk.Button(sidebar, text="Logout", command=self.logout, **btn)
        logout_btn.pack(pady=30)
        self.sidebar_buttons.append(logout_btn)

        if role in ("admin", "manager"):
            self.inventory_screen()
        else:
            self.sales_screen()
