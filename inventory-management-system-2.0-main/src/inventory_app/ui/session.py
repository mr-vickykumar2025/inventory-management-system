# -*- coding: utf-8 -*-
from .. import database


class SessionMixin:
    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    def clear_main(self):
        if not hasattr(self, "main"):
            return
        for w in self.main.winfo_children():
            w.destroy()

    def logout(self):
        if self.current_user:
            self._log_action("LOGOUT", "")
        self.current_user = None
        self.current_role = None
        self.login_screen()

    def _log_action(self, action, details=""):
        if self.current_user:
            database.log_action(self.current_user, action, details)
