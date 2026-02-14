# -*- coding: utf-8 -*-
from tkinter import messagebox


class ValidationMixin:
    def _parse_float(self, value, field_name):
        text = value.strip()
        if not text:
            messagebox.showerror("Error", f"{field_name} is required")
            return None
        try:
            number = float(text)
        except ValueError:
            messagebox.showerror("Error", f"{field_name} must be a number")
            return None
        if number <= 0:
            messagebox.showerror("Error", f"{field_name} must be greater than 0")
            return None
        return number

    def _parse_int(self, value, field_name):
        text = value.strip()
        if not text:
            messagebox.showerror("Error", f"{field_name} is required")
            return None
        try:
            number = int(text)
        except ValueError:
            messagebox.showerror("Error", f"{field_name} must be a whole number")
            return None
        if number <= 0:
            messagebox.showerror("Error", f"{field_name} must be greater than 0")
            return None
        return number
