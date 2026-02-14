# -*- coding: utf-8 -*-
try:
    from .app import InventoryApp, run
except ImportError:
    # Allow running this file directly without package context
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
    from inventory_app.app import InventoryApp, run

__all__ = ["InventoryApp", "run"]


if __name__ == "__main__":
    run()
