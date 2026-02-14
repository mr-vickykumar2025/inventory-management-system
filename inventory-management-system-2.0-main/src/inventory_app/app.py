# -*- coding: utf-8 -*-
import os
import tkinter as tk

from . import database
from .ui.theme import ThemeMixin
from .ui.session import SessionMixin
from .ui.keyboard import KeyboardMixin
from .ui.login import LoginMixin
from .ui.dashboard import DashboardMixin
from .ui.products import ProductMixin
from .ui.sales import SalesMixin
from .ui.audit import AuditMixin
from .ui.low_stock import LowStockMixin
from .ui.backup import BackupMixin
from .ui.validation import ValidationMixin


class InventoryApp(
    ThemeMixin,
    SessionMixin,
    KeyboardMixin,
    LoginMixin,
    DashboardMixin,
    ProductMixin,
    SalesMixin,
    AuditMixin,
    LowStockMixin,
    BackupMixin,
    ValidationMixin
):
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                pass
        self.theme = "dark"
        self.base_dir = database.get_app_base_dir()
        self._apply_root_theme()
        self.current_user = None
        self.current_role = None
        self.login_screen()


def run():
    database.create_tables()

    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
