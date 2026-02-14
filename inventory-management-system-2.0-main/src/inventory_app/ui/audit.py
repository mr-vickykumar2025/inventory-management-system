# -*- coding: utf-8 -*-
import tkinter as tk

from .. import database


class AuditMixin:
    def audit_log_screen(self, search_query=""):
        self.clear_main()

        colors = self._theme()
        tk.Label(self.main,text="Audit Log",font=("Segoe UI",20,"bold"),
                 bg=colors["panel_bg"],fg=colors["text"]).pack(pady=20)

        search_bar = tk.Frame(self.main, bg=colors["panel_bg"])
        search_bar.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(search_bar, text="Search", bg=colors["panel_bg"], fg=colors["text"]).pack(side="left")
        self.audit_search = tk.Entry(
            search_bar,
            width=35,
            bg=colors["field_bg"],
            fg=colors["field_fg"],
            insertbackground=colors["field_fg"]
        )
        self.audit_search.pack(side="left", padx=(8, 6), fill="x", expand=True)
        if search_query:
            self.audit_search.insert(0, search_query)

        tk.Button(
            search_bar,
            text="Clear",
            bg=colors["card_bg"],
            fg=colors["text"],
            width=8,
            command=lambda: self.audit_log_screen(search_query="")
        ).pack(side="right")

        self.audit_search.bind(
            "<KeyRelease>",
            lambda event: self.audit_log_screen(search_query=self.audit_search.get())
        )

        container = tk.Frame(self.main,bg=colors["panel_bg"])
        container.pack(fill="both",expand=True,padx=30)

        logs = database.search_audit_logs(search_query)

        if not logs:
            empty_text = "No audit logs found" if not search_query else "No audit logs match this search"
            tk.Label(self.main,text=empty_text,
                     bg=colors["panel_bg"],fg=colors["link"]).pack(pady=20)
            self._configure_keyboard(
                focus_widget=self.audit_search,
                esc=self._go_home,
                ctrl_n=self._new_product
            )
            return

        canvas = tk.Canvas(container,bg=colors["panel_bg"],highlightthickness=0)
        scrollbar = tk.Scrollbar(container,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right",fill="y")
        canvas.pack(side="left",fill="both",expand=True)

        scroll_frame = tk.Frame(canvas,bg=colors["panel_bg"])
        scroll_window = canvas.create_window((0,0),window=scroll_frame,anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(scroll_window,width=event.width)

        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)),"units")

        def _on_linux_scroll(event):
            direction = -1 if event.num == 4 else 1
            canvas.yview_scroll(direction,"units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>",_on_mousewheel)
            canvas.bind_all("<Button-4>",_on_linux_scroll)
            canvas.bind_all("<Button-5>",_on_linux_scroll)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        scroll_frame.bind("<Configure>",_on_frame_configure)
        canvas.bind("<Configure>",_on_canvas_configure)
        canvas.bind("<Enter>",_bind_mousewheel)
        canvas.bind("<Leave>",_unbind_mousewheel)
        scroll_frame.bind("<Enter>",_bind_mousewheel)
        scroll_frame.bind("<Leave>",_unbind_mousewheel)

        for log in logs:
            card = tk.Frame(scroll_frame,bg=colors["card_bg"],padx=25,pady=15)
            card.pack(fill="x",pady=10)

            tk.Label(card,text=f"Log ID: {log[0]}",bg=colors["card_bg"],fg=colors["link"]).grid(row=0,column=0)
            tk.Label(card,text=f"User: {log[1]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=0,column=1,padx=30)

            tk.Label(card,text=f"Action: {log[2]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=1,column=0)
            tk.Label(card,text=f"Details: {log[3]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=1,column=1,padx=30)

            tk.Label(card,text=f"Date: {log[4]}",bg=colors["card_bg"],fg=colors["text"]).grid(row=2,column=0)

        self._configure_keyboard(
            focus_widget=self.audit_search,
            esc=self._go_home,
            ctrl_n=self._new_product
        )
