# -*- coding: utf-8 -*-
import os
import datetime
from tkinter import messagebox, filedialog

from .. import database


class BackupMixin:
    def backup_database(self):
        backup_dir = os.path.join(self.base_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"inventory_{timestamp}.db")
        try:
            database.backup_database(backup_path)
            self._log_action("BACKUP", backup_path)
            messagebox.showinfo("Success", f"Backup saved to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def restore_database(self):
        confirm = messagebox.askyesno(
            "Restore Database",
            "Restoring will overwrite current data. Continue?"
        )
        if not confirm:
            return
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            database.restore_database(file_path)
            self._log_action("RESTORE", file_path)
            messagebox.showinfo(
                "Success",
                "Restore completed. Please restart the app to reload data."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
