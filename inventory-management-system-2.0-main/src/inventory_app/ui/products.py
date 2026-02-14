# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog

from .. import database


class ProductMixin:
    def add_product_screen(self):
        self.clear_main()

        colors = self._theme()
        self.form_title = tk.Label(self.main, text="Add Product", font=("Segoe UI", 20, "bold"),
                                   bg=colors["panel_bg"], fg=colors["text"])
        self.form_title.pack(pady=20)

        form = tk.Frame(self.main, bg=colors["panel_bg"])
        form.pack()

        entry_style = {
            "width": 40,
            "bg": colors["field_bg"],
            "fg": colors["field_fg"],
            "insertbackground": colors["field_fg"]
        }
        self.pid = tk.Entry(form, **entry_style)
        self.name = tk.Entry(form, **entry_style)

        self.cat = ttk.Combobox(form, width=38, values=[
            "Grocery","Electronics","Medical","Clothing","Footwear",
            "Stationery","Hardware","Home Appliance","Kitchen",
            "Cosmetics","Mobile Accessories","Electrical",
            "Furniture","Sports","Bakery","Dairy",
            "Fruits & Vegetables","General Store","Other"
        ])
        self.cat.current(0)

        self.unit = ttk.Combobox(form, width=38, values=[
            "kg","gram","liter","ml","pcs","dozen","packet",
            "box","bottle","meter","cm","inch","feet"
        ])
        self.unit.current(0)

        self.price = tk.Entry(form, **entry_style)
        self.qty = tk.Entry(form, **entry_style)

        for label, entry in [("Product ID",self.pid),("Name",self.name),
                             ("Category",self.cat),("Unit",self.unit),
                             ("Price",self.price),("Quantity",self.qty)]:
            tk.Label(form, text=label, bg=colors["panel_bg"], fg=colors["text"]).pack()
            entry.pack(pady=5)

        self.save_btn = tk.Button(
            form,
            text="Save Product",
            bg=colors["accent"],
            fg=colors["accent_text"],
            activebackground=colors["accent_hover"],
            activeforeground=colors["accent_text"],
            width=20,
            takefocus=True,
            command=self.save_product
        )
        self.save_btn.pack(pady=20)

        self._configure_keyboard(
            focus_widget=self.pid,
            enter=self.save_btn.invoke,
            ctrl_s=self.save_btn.invoke,
            ctrl_n=self.add_product_screen,
            esc=self._go_home
        )

    def save_product(self):
        try:
            pid = self.pid.get().strip()
            name = self.name.get().strip()
            if not pid or not name:
                messagebox.showerror("Error", "Product ID and Name are required")
                return

            price = self._parse_float(self.price.get(), "Price")
            qty = self._parse_float(self.qty.get(), "Quantity")
            if price is None or qty is None:
                return

            existing = database.get_product_by_id(pid)
            if existing:
                choice = messagebox.askyesnocancel(
                    "Product Exists",
                    "Product ID already exists.\n"
                    "Yes = Add to stock\n"
                    "No = Replace quantity\n"
                    "Cancel = abort"
                )
                if choice is None:
                    return
                if choice:
                    new_qty = existing[5] + qty
                    database.update_product(
                        pid,
                        name,
                        self.cat.get(),
                        self.unit.get(),
                        price,
                        new_qty
                    )
                    self._log_action("UPDATE_PRODUCT", f"{pid} | add_qty={qty} | new_qty={new_qty}")
                else:
                    database.update_product(
                        pid,
                        name,
                        self.cat.get(),
                        self.unit.get(),
                        price,
                        qty
                    )
                    self._log_action("UPDATE_PRODUCT", f"{pid} | set_qty={qty}")
                messagebox.showinfo("Success", "Product Updated")
                self.inventory_screen()
                return

            database.add_product(
                pid,
                name,
                self.cat.get(),
                self.unit.get(),
                price,
                qty
            )
            self._log_action("ADD_PRODUCT", f"{pid} | {name}")
            messagebox.showinfo("Success","Product Added")
            self.inventory_screen()
        except Exception as e:
            messagebox.showerror("Error",str(e))

    def edit_product_screen(self, pid):
        product = database.get_product_by_id(pid)
        if not product:
            messagebox.showerror("Error", "Product not found")
            return

        self.add_product_screen()
        self.form_title.config(text="Update Product")

        self.pid.delete(0, tk.END)
        self.pid.insert(0, product[0])
        self.pid.config(state="disabled")

        self.name.delete(0, tk.END)
        self.name.insert(0, product[1])

        if product[2]:
            self.cat.set(product[2])
        if product[3]:
            self.unit.set(product[3])

        self.price.delete(0, tk.END)
        self.price.insert(0, str(product[4]))

        self.qty.delete(0, tk.END)
        self.qty.insert(0, str(product[5]))

        self.save_btn.config(text="Update Product", command=self.update_product)

        self._configure_keyboard(
            focus_widget=self.name,
            enter=self.save_btn.invoke,
            ctrl_s=self.save_btn.invoke,
            ctrl_n=self.add_product_screen,
            esc=self._go_home
        )

    def update_product(self):
        try:
            pid = self.pid.get().strip()
            name = self.name.get().strip()
            if not pid or not name:
                messagebox.showerror("Error", "Product ID and Name are required")
                return

            price = self._parse_float(self.price.get(), "Price")
            qty = self._parse_float(self.qty.get(), "Quantity")
            if price is None or qty is None:
                return

            database.update_product(
                pid,
                name,
                self.cat.get(),
                self.unit.get(),
                price,
                qty
            )
            self._log_action("UPDATE_PRODUCT", f"{pid} | set_qty={qty} | price={price}")
            messagebox.showinfo("Success", "Product Updated")
            self.inventory_screen()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def inventory_screen(self, search_query=""):
        self.clear_main()

        colors = self._theme()
        tk.Label(self.main, text="Inventory", font=("Segoe UI", 20, "bold"),
                 bg=colors["panel_bg"], fg=colors["text"]).pack(pady=10)

        all_products = database.get_all_products()
        products = database.search_products(search_query) if search_query else all_products
        limit = getattr(database, "LOW_STOCK_LIMIT", 10)
        low_stock = [p for p in all_products if p[5] <= limit]
        low_stock_count = len(low_stock)

        def fmt_qty(val):
            try:
                num = float(val)
                if num.is_integer():
                    return str(int(num))
                return f"{num:.2f}"
            except (TypeError, ValueError):
                return str(val)

        def fmt_price(val):
            try:
                return f"{float(val):.2f}"
            except (TypeError, ValueError):
                return str(val)

        body = tk.Frame(self.main, bg=colors["panel_bg"])
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        left = tk.Frame(body, bg=colors["panel_bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(
            body,
            bg=colors["card_bg"],
            width=320,
            highlightbackground=colors["border"],
            highlightthickness=1
        )
        right.pack(side="right", fill="y", padx=(20, 0))
        right.pack_propagate(False)

        tk.Label(
            right,
            text="Insights",
            bg=colors["card_bg"],
            fg=colors["text"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 6))

        right_content = tk.Frame(right, bg=colors["card_bg"])
        right_content.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Right panel cards
        def side_card(title):
            box = tk.Frame(
                right_content,
                bg=colors["panel_bg"],
                padx=12,
                pady=10,
                highlightbackground=colors["border"],
                highlightthickness=1
            )
            tk.Label(
                box,
                text=title,
                bg=colors["panel_bg"],
                fg=colors["muted"],
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            return box

        total_products = len(products)
        total_qty = sum(p[5] for p in products) if products else 0
        total_value = sum(p[4] * p[5] for p in products) if products else 0

        summary_box = side_card("Summary")
        tk.Label(summary_box, text=f"Total Products: {total_products}", bg=colors["panel_bg"],
                 fg=colors["text"]).pack(anchor="w", pady=(4, 0))
        tk.Label(summary_box, text=f"Low Stock: {low_stock_count}", bg=colors["panel_bg"],
                 fg=colors["text"]).pack(anchor="w")
        tk.Label(summary_box, text=f"Total Qty: {fmt_qty(total_qty)}", bg=colors["panel_bg"],
                 fg=colors["text"]).pack(anchor="w")
        tk.Label(summary_box, text=f"Stock Value: ₹{total_value:.2f}", bg=colors["panel_bg"],
                 fg=colors["text"]).pack(anchor="w")
        summary_box.pack(fill="x", pady=(0, 12))

        low_box = side_card("Low Stock Items")
        if low_stock:
            for p in low_stock[:5]:
                tk.Label(
                    low_box,
                    text=f"{p[1]} • {fmt_qty(p[5])} {p[3]}",
                    bg=colors["panel_bg"],
                    fg=colors["danger"]
                ).pack(anchor="w")
        else:
            tk.Label(low_box, text="None", bg=colors["panel_bg"], fg=colors["muted"]).pack(anchor="w", pady=(4, 0))
        low_box.pack(fill="x", pady=(0, 12))

        activity_box = side_card("Recent Activity")
        logs = database.get_audit_logs(limit=5)
        if logs:
            for log in logs:
                tk.Label(
                    activity_box,
                    text=f"{log[1]} • {log[2]}",
                    bg=colors["panel_bg"],
                    fg=colors["text"]
                ).pack(anchor="w")
                tk.Label(
                    activity_box,
                    text=f"{log[4]}",
                    bg=colors["panel_bg"],
                    fg=colors["muted"],
                    font=("Segoe UI", 8)
                ).pack(anchor="w", pady=(0, 4))
        else:
            tk.Label(activity_box, text="No recent activity", bg=colors["panel_bg"],
                     fg=colors["muted"]).pack(anchor="w", pady=(4, 0))
        activity_box.pack(fill="x")

        if low_stock_count > 0:
            tk.Label(
                left,
                text=f"Low stock items: {low_stock_count} (<= {limit})",
                bg=colors["banner_bg"],
                fg=colors["banner_text"],
                font=("Segoe UI", 12, "bold"),
                pady=6
            ).pack(fill="x", padx=10, pady=6)

        search_bar = tk.Frame(left, bg=colors["panel_bg"])
        search_bar.pack(fill="x", padx=10, pady=(6, 10))

        tk.Label(search_bar, text="Search", bg=colors["panel_bg"], fg=colors["text"]).pack(side="left")
        self.inventory_search = tk.Entry(
            search_bar,
            width=30,
            bg=colors["field_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.inventory_search.pack(side="left", padx=(8, 6), fill="x", expand=True)
        if search_query:
            self.inventory_search.insert(0, search_query)

        tk.Button(
            search_bar,
            text="Clear",
            bg=colors["card_bg"],
            fg=colors["text"],
            width=8,
            command=lambda: self.inventory_screen(search_query="")
        ).pack(side="right")

        self.inventory_search.bind(
            "<KeyRelease>",
            lambda event: self.inventory_screen(search_query=self.inventory_search.get())
        )

        if search_query:
            tk.Label(
                left,
                text=f"Showing {len(products)} of {len(all_products)}",
                bg=colors["panel_bg"],
                fg=colors["muted"]
            ).pack(anchor="w", padx=12, pady=(0, 6))

        container = tk.Frame(left, bg=colors["panel_bg"])
        container.pack(fill="both", expand=True, padx=0)

        columns = 2
        for c in range(columns):
            container.grid_columnconfigure(c, weight=1)

        if not products:
            empty_text = "No products found" if not search_query else "No products found for this search"
            tk.Label(container, text=empty_text, bg=colors["panel_bg"],
                     fg=colors["muted"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            self._configure_keyboard(
                focus_widget=self.inventory_search,
                esc=self._go_home,
                ctrl_n=self._new_product
            )
            return

        first_action_button = None
        for i, p in enumerate(products, start=1):
            status = "LOW STOCK ⚠️" if p[5] <= limit else "IN STOCK ✅"
            color = colors["danger"] if p[5] <= limit else colors["success"]

            card = tk.Frame(
                container,
                bg=colors["card_bg"],
                padx=25,
                pady=15,
                highlightbackground=colors["border"],
                highlightthickness=2
            )
            row = (i - 1) // columns
            col = (i - 1) % columns
            card.grid(row=row, column=col, sticky="ew", padx=10, pady=10)

            tk.Label(card, text=f"Serial: {i}", bg=colors["card_bg"], fg=colors["link"]).grid(row=0,column=0)
            tk.Label(card, text=f"Product ID: {p[0]}", bg=colors["card_bg"], fg=colors["text"]).grid(row=0,column=1,padx=30)
            tk.Label(card, text=f"Name: {p[1]}", bg=colors["card_bg"], fg=colors["text"]).grid(row=1,column=0)
            tk.Label(card, text=f"Category: {p[2]}", bg=colors["card_bg"], fg=colors["text"]).grid(row=1,column=1,padx=30)
            tk.Label(card, text=f"Unit: {p[3]}", bg=colors["card_bg"], fg=colors["text"]).grid(row=2,column=0)
            tk.Label(card, text=f"Price: ₹{fmt_price(p[4])}", bg=colors["card_bg"], fg=colors["text"]).grid(row=2,column=1,padx=30)
            tk.Label(card, text=f"Quantity: {fmt_qty(p[5])}", bg=colors["card_bg"], fg=colors["text"]).grid(row=3,column=0)
            tk.Label(card, text=f"Status: {status}", bg=colors["card_bg"], fg=color).grid(row=3,column=1,padx=30)

            actions = tk.Frame(card, bg=colors["card_bg"])
            actions.grid(row=0, column=2, rowspan=4, padx=20, pady=5)

            add_stock_btn = tk.Button(actions, text="Add Stock", bg=colors["accent"], fg=colors["accent_text"],
                                      activebackground=colors["accent_hover"], activeforeground=colors["accent_text"],
                                      width=12, takefocus=True,
                                      command=lambda pid=p[0]: self.add_stock(pid))
            add_stock_btn.pack(pady=4)
            if first_action_button is None:
                first_action_button = add_stock_btn

            tk.Button(actions, text="Edit", bg=colors["warning"], fg=colors["warning_text"],
                      width=12, takefocus=True,
                      command=lambda pid=p[0]: self.edit_product_screen(pid)).pack(pady=4)
            tk.Button(actions, text="Delete", bg=colors["danger"], fg=colors["danger_text"],
                      width=12, takefocus=True,
                      command=lambda pid=p[0]: self.delete_item(pid)).pack(pady=4)

        self._configure_keyboard(
            focus_widget=self.inventory_search,
            esc=self._go_home,
            ctrl_n=self._new_product
        )

    def delete_item(self, pid):
        if messagebox.askyesno("Confirm", "Delete product?"):
            database.delete_product(pid)
            self._log_action("DELETE_PRODUCT", f"{pid}")
            self.inventory_screen()

    def add_stock(self, pid):
        product = database.get_product_by_id(pid)
        if not product:
            messagebox.showerror("Error", "Product not found")
            return

        qty = simpledialog.askfloat("Add Stock", "Enter quantity to add:")
        if qty is None:
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return

        new_qty = product[5] + qty
        database.update_product(
            pid,
            product[1],
            product[2],
            product[3],
            product[4],
            new_qty
        )
        self._log_action("UPDATE_PRODUCT", f"{pid} | add_qty={qty} | new_qty={new_qty}")
        messagebox.showinfo("Success", f"Stock updated. New qty: {new_qty}")
        self.inventory_screen()
