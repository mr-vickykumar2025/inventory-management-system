# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import tkinter as tk

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
from tkinter import messagebox

from .. import database


class SalesMixin:
    def _invoice_dir(self):
        invoice_dir = os.path.join(self.base_dir, "invoices")
        os.makedirs(invoice_dir, exist_ok=True)
        return invoice_dir

    def _open_invoice_folder(self):
        invoice_dir = self._invoice_dir()
        try:
            if sys.platform.startswith("win"):
                os.startfile(invoice_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", invoice_dir], check=False)
            else:
                subprocess.run(["xdg-open", invoice_dir], check=False)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to open folder:\n{exc}")

    def sales_screen(self):
        self.clear_main()

        colors = self._theme()
        tk.Label(self.main,text="Sales",font=("Segoe UI",20,"bold"),
                 bg=colors["panel_bg"],fg=colors["text"]).pack(pady=20)

        entry_style = {
            "width": 30,
            "bg": colors["field_bg"],
            "fg": colors["field_fg"],
            "insertbackground": colors["field_fg"]
        }
        self.sale_id = tk.Entry(self.main, **entry_style)
        self.sale_qty = tk.Entry(self.main, **entry_style)

        tk.Label(self.main,text="Product ID",bg=colors["panel_bg"],fg=colors["text"]).pack()
        self.sale_id.pack()
        tk.Label(self.main,text="Quantity",bg=colors["panel_bg"],fg=colors["text"]).pack()
        self.sale_qty.pack()

        tk.Button(
            self.main,
            text="Generate Invoice PDF",
            bg=colors["accent"],
            fg=colors["accent_text"],
            activebackground=colors["accent_hover"],
            activeforeground=colors["accent_text"],
            width=25,
            takefocus=True,
            command=self.generate_invoice
        ).pack(pady=20)

        tk.Button(
            self.main,
            text="Open Invoice Folder",
            bg=colors["warning"],
            fg=colors["warning_text"],
            width=25,
            takefocus=True,
            command=self._open_invoice_folder
        ).pack(pady=(0, 10))

        self._configure_keyboard(
            focus_widget=self.sale_id,
            enter=self.generate_invoice,
            ctrl_s=self.generate_invoice,
            ctrl_n=self.sales_screen,
            esc=self._go_home
        )

    def generate_invoice(self):
        pid = self.sale_id.get()
        qty = self._parse_float(self.sale_qty.get(), "Quantity")
        if qty is None:
            return

        product = database.get_product_by_id(pid)
        if not product:
            messagebox.showerror("Error", "Product not found")
            return

        stock = product[5]
        if qty > stock:
            messagebox.showerror("Error", f"Only {stock} items available")
            return

        database.record_sale(pid, qty)

        total = qty * product[4]
        now = datetime.datetime.now()
        now_display = now.strftime("%d-%m-%Y %H:%M")
        self._log_action("SALE", f"{pid} | qty={qty} | total={total}")

        file_path = os.path.join(
            self._invoice_dir(),
            f"invoice_{pid}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        pdf = canvas.Canvas(file_path, pagesize=A4)

        pdf.drawString(200,800,"INVOICE")
        pdf.drawString(50,750,f"Date: {now_display}")
        pdf.drawString(50,720,f"Product: {product[1]}")
        pdf.drawString(50,690,f"Qty: {qty}")
        pdf.drawString(50,660,f"Total: ₹{total}")

        pdf.save()

        self._open_invoice_folder()
        messagebox.showinfo("Success", f"Invoice saved as:\n{file_path}")
        self.inventory_screen()

    def sales_history_screen(self, search_query=""):
        self.clear_main()

        colors = self._theme()
        tk.Label(self.main,text="Sales History",font=("Segoe UI",20,"bold"),
                 bg=colors["panel_bg"],fg=colors["text"]).pack(pady=20)

        search_bar = tk.Frame(self.main, bg=colors["panel_bg"])
        search_bar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(search_bar, text="Search", bg=colors["panel_bg"], fg=colors["text"]).pack(side="left")
        self.sales_search = tk.Entry(
            search_bar,
            width=35,
            bg=colors["field_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.sales_search.pack(side="left", padx=(8, 6), fill="x", expand=True)
        if search_query:
            self.sales_search.insert(0, search_query)

        tk.Button(
            search_bar,
            text="Clear",
            bg=colors["card_bg"],
            fg=colors["text"],
            width=8,
            command=lambda: self.sales_history_screen(search_query="")
        ).pack(side="right")

        self.sales_search.bind(
            "<KeyRelease>",
            lambda event: self.sales_history_screen(search_query=self.sales_search.get())
        )

        container = tk.Frame(self.main,bg=colors["panel_bg"])
        container.pack(fill="both",expand=True,padx=30)

        sales = database.search_sales_history(search_query)

        if search_query:
            tk.Label(
                self.main,
                text=f"Showing {len(sales)} result(s)",
                bg=colors["panel_bg"],
                fg=colors["muted"]
            ).pack(anchor="w", padx=30, pady=(0, 6))

        if not sales:
            empty_text = "No sales records found" if not search_query else "No sales records match this search"
            tk.Label(self.main,text=empty_text,
                     bg=colors["panel_bg"],fg=colors["link"]).pack(pady=20)
            self._configure_keyboard(
                focus_widget=self.sales_search,
                esc=self._go_home,
                ctrl_n=self.sales_screen
            )
            return

        for s in sales:
            card = tk.Frame(container,bg=colors["card_bg"],padx=25,pady=15)
            card.pack(fill="x",pady=10)

            tk.Label(card,text=f"Sale ID: {s[0]}",bg=colors["card_bg"],fg=colors["link"]).grid(row=0,column=0)
            tk.Label(card,text=f"Product: {s[2]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=0,column=1,padx=30)

            tk.Label(card,text=f"Price: ₹{s[3]} per unit",bg=colors["card_bg"],fg=colors["text"]).grid(row=1,column=0)
            tk.Label(card,text=f"Qty: {s[4]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=1,column=1,padx=30)

            tk.Label(card,text=f"Total: ₹{s[5]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=2,column=0)
            tk.Label(card,text=f"Date: {s[6]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=2,column=1,padx=30)

        self._configure_keyboard(
            focus_widget=self.sales_search,
            esc=self._go_home,
            ctrl_n=self.sales_screen
        )
