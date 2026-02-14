# -*- coding: utf-8 -*-
import tkinter as tk


class KeyboardMixin:
    def _init_keyboard_state(self):
        if not hasattr(self, "_bound_shortcuts"):
            self._bound_shortcuts = []
        if not hasattr(self, "_keyboard_actions"):
            self._keyboard_actions = {}

    def _unbind_shortcuts(self):
        for seq in getattr(self, "_bound_shortcuts", []):
            self.root.unbind_all(seq)
        self._bound_shortcuts = []

    def _bind_shortcut(self, sequence, handler):
        self.root.bind_all(sequence, handler)
        self._bound_shortcuts.append(sequence)

    def _is_root_event(self, event):
        try:
            return event.widget.winfo_toplevel() == self.root
        except Exception:
            return True

    def _is_text_input(self, widget):
        if widget is None:
            return False
        if not hasattr(widget, "winfo_class"):
            return False
        cls = widget.winfo_class()
        return cls in ("Entry", "Text", "TCombobox", "Spinbox", "TEntry")

    def _invoke_focused(self):
        widget = self.root.focus_get()
        if widget and hasattr(widget, "invoke"):
            try:
                widget.invoke()
                return True
            except tk.TclError:
                return False
        return False

    def _sidebar_first(self):
        buttons = getattr(self, "sidebar_buttons", None)
        if buttons:
            return buttons[0]
        return None

    def _go_home(self):
        if getattr(self, "current_user", None):
            if self.current_role in ("admin", "manager"):
                self.inventory_screen()
            else:
                self.sales_screen()
        else:
            self.login_screen()

    def _new_product(self):
        if self.current_role in ("admin", "manager"):
            self.add_product_screen()

    def _configure_keyboard(self, *, focus_widget=None, enter=None, esc=None, ctrl_s=None, ctrl_n=None):
        self._init_keyboard_state()
        self._unbind_shortcuts()
        self._keyboard_actions = {
            "enter": enter,
            "esc": esc,
            "ctrl_s": ctrl_s,
            "ctrl_n": ctrl_n
        }

        self._bind_shortcut("<Return>", self._handle_enter)
        self._bind_shortcut("<KP_Enter>", self._handle_enter)
        self._bind_shortcut("<Escape>", self._handle_escape)

        if ctrl_s:
            self._bind_shortcut("<Control-s>", self._handle_ctrl_s)
        if ctrl_n:
            self._bind_shortcut("<Control-n>", self._handle_ctrl_n)

        for seq in ("<Up>", "<Down>", "<Left>", "<Right>"):
            self._bind_shortcut(seq, self._handle_arrow)

        if focus_widget is None:
            focus_widget = self._sidebar_first()
        if focus_widget is not None:
            try:
                focus_widget.focus_set()
            except tk.TclError:
                pass

    def _handle_enter(self, event):
        if not self._is_root_event(event):
            return
        if self._is_text_input(event.widget) and event.widget.winfo_class() == "TCombobox":
            return
        action = self._keyboard_actions.get("enter")
        if callable(action):
            action()
            return "break"
        if self._invoke_focused():
            return "break"
        return None

    def _handle_escape(self, event):
        if not self._is_root_event(event):
            return
        action = self._keyboard_actions.get("esc") or self._go_home
        if callable(action):
            action()
            return "break"
        return None

    def _handle_ctrl_s(self, event):
        if not self._is_root_event(event):
            return
        action = self._keyboard_actions.get("ctrl_s")
        if callable(action):
            action()
            return "break"
        return None

    def _handle_ctrl_n(self, event):
        if not self._is_root_event(event):
            return
        action = self._keyboard_actions.get("ctrl_n")
        if callable(action):
            action()
            return "break"
        return None

    def _handle_arrow(self, event):
        if not self._is_root_event(event):
            return
        if self._is_text_input(event.widget):
            return
        if event.keysym in ("Up", "Left"):
            target = event.widget.tk_focusPrev()
        else:
            target = event.widget.tk_focusNext()
        if target:
            target.focus_set()
            return "break"
        return None
