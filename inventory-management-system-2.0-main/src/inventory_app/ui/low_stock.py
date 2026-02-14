# -*- coding: utf-8 -*-
import tkinter as tk

from .. import database


class LowStockMixin:
    def low_stock_screen(self, search_query=""):
        self.clear_main()

        colors = self._theme()
        tk.Label(self.main,text="Low Stock",font=("Segoe UI",20,"bold"),
                 bg=colors["panel_bg"],fg=colors["text"]).pack(pady=20)

        limit = getattr(database, "LOW_STOCK_LIMIT", 10)
        if search_query:
            products = [p for p in database.search_products(search_query) if p[5] <= limit]
        else:
            products = database.get_low_stock_products()

        search_bar = tk.Frame(self.main, bg=colors["panel_bg"])
        search_bar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(search_bar, text="Search", bg=colors["panel_bg"], fg=colors["text"]).pack(side="left")
        self.low_stock_search = tk.Entry(
            search_bar,
            width=35,
            bg=colors["field_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.low_stock_search.pack(side="left", padx=(8, 6), fill="x", expand=True)
        if search_query:
            self.low_stock_search.insert(0, search_query)

        tk.Button(
            search_bar,
            text="Clear",
            bg=colors["card_bg"],
            fg=colors["text"],
            width=8,
            command=lambda: self.low_stock_screen(search_query="")
        ).pack(side="right")

        self.low_stock_search.bind(
            "<KeyRelease>",
            lambda event: self.low_stock_screen(search_query=self.low_stock_search.get())
        )

        if not products:
            empty_text = "No Low Stock Products" if not search_query else "No low stock items match this search"
            tk.Label(self.main,text=empty_text,
                     bg=colors["panel_bg"],fg=colors["link"]).pack(pady=20)
            self._configure_keyboard(
                focus_widget=self.low_stock_search,
                esc=self._go_home,
                ctrl_n=self._new_product
            )
            return

        tk.Label(self.main,text=f"Threshold: <= {limit}",
                 bg=colors["panel_bg"],fg=colors["muted"]).pack(pady=5)

        for p in products:
            tk.Label(self.main,text=f"{p[1]} | Qty: {p[5]} {p[3]}",
                     bg=colors["panel_bg"],fg=colors["danger"]).pack(pady=5)

        self._configure_keyboard(
            focus_widget=self.low_stock_search,
            esc=self._go_home,
            ctrl_n=self._new_product
        )
