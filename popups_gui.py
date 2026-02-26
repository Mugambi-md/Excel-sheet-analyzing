import tkinter as tk
from tkinter import messagebox
from base_window import BaseWindow, ScrollableFrame


class ColumnSelectorGUI(BaseWindow):
    def __init__(self, parent, columns, title="Select Columns"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.center_window(self.window, 350, 550, parent)
        self.window.transient(parent)
        self.window.grab_set()

        self.columns = columns
        self.selected_columns = []
        self.join_key = tk.StringVar()
        self.main_frame = tk.Frame(self.window, bd=4, relief="solid")
        self.list_frame = tk.Frame(self.main_frame, bd=4, relief="ridge")
        self.listbox = tk.Listbox(
            self.list_frame, selectmode=tk.MULTIPLE, bd=4, relief="ridge",
            font=("Arial", 12)
        )

        self.build_ui()
        parent.wait_window(self.window)

    def build_ui(self):
        """Build UI."""
        self.main_frame.pack(fill="both", expand=True, pady=(0, 5), padx=5)
        tk.Label(
            self.main_frame,
            text="Select Columns (Choose JOIN KEY)",
            fg="blue",
            font=("Arial", 14, "bold", "underline"),
        ).pack(side="top", anchor="center", pady=(5, 0))
        self.list_frame.pack(fill="both", expand=True)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for col in self.columns:
            self.listbox.insert(tk.END, col)

        tk.Label(
            self.main_frame, text="Select Join Key:", fg="green",
            font=("Arial", 14, "bold", "underline")
        ).pack(pady=(5, 0))

        btn_frame = ScrollableFrame(self.main_frame, "lightgray", 170)
        btn_frame.pack(fill="both", expand=True)
        radio_frame = btn_frame.scrollable_frame

        for col in self.columns:
            tk.Radiobutton(
                radio_frame, text=col, variable=self.join_key, value=col
            ).pack(anchor="w", pady=2, padx=5)

        tk.Button(
            self.main_frame, text="Confirm", bg="gray", fg="blue", bd=3,
            relief="groove", font=("Arial", 10, "bold"),
            command=self.confirm_selection,
        ).pack(pady=(5, 0))

    def confirm_selection(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning(
                "No Selection", "Select At Least One Column.",
                parent=self.window
            )
            return
        if not self.join_key.get():
            messagebox.showwarning(
                "No Join Key", "Select Join Key Column.", parent=self.window
            )
            return
        self.selected_columns = [self.listbox.get(i) for i in selected]

        if self.join_key.get() not in self.selected_columns:
            messagebox.showwarning(
                "Invalid Key", "Join Key Must Be in Selected columns",
                parent=self.window
            )
            return
        self.window.destroy()
