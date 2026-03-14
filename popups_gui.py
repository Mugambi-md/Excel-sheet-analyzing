import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkfont
from base_window import BaseWindow, ScrollableFrame


class ColumnSelectorGUI(BaseWindow):
    def __init__(self, parent, columns, title="Select Columns"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.center_window(self.window, 400, 600, parent)
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
        self.listbox.pack(side="left", fill="both", expand=True, ipadx=5)
        scrollbar = tk.Scrollbar(self.list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for col in self.columns:
            self.listbox.insert(tk.END, col)

        tk.Label(
            self.main_frame, text="Select Join Key:", fg="green",
            font=("Arial", 14, "bold", "underline")
        ).pack(pady=(5, 0))

        btn_frame = ScrollableFrame(self.main_frame, "white", 170)
        btn_frame.pack(fill="both", expand=True)
        radio_frame = btn_frame.scrollable_frame

        for col in self.columns:
            tk.Radiobutton(
                radio_frame, text=col, variable=self.join_key, value=col,
                bg="white", font=("Arial", 11, "bold")
            ).pack(anchor="w", pady=2, padx=5)

        tk.Button(
            self.main_frame, text="Confirm", bg="blue", fg="white", bd=4,
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


class LoadingPopup(BaseWindow):
    """Small loading popup window."""
    def __init__(self, parent, message="Processing data."):
        self.window = tk.Toplevel(parent)
        self.window.title("Loading...")
        self.window.configure(bg="aliceblue")
        self.center_window(self.window, 260, 170, parent)
        self.window.transient(parent)
        self.window.grab_set()
        # self.window.protocol("WM_DELETE_WINDOW", lambda: None)

        self.message = message
        self.main_frame = tk.Frame(self.window, bg="aliceblue", bd=2, relief="ridge")
        # Loader (Spinning indicator)
        self.canvas = tk.Canvas(
            self.main_frame, width=40, height=40, bg="aliceblue",
            highlightthickness=0
        )
        self.arc = self.canvas.create_arc(
            5, 5, 35, 35,
            start=0, extent=90,
            style="arc", width=4,
            outline="purple"
        )
        # Progress Label
        self.pregress_label = tk.Label(
            self.main_frame, text="", bg="aliceblue", fg="purple",
            font=("Arial", 11, "italic"), wraplength=220, justify="center"
        )
        # Wait Label
        self.wait_label = tk.Label(
            self.main_frame, text="Please Wait", bg="aliceblue", fg="blue",
            font=("Georgia", 11, "italic")
        )

        self.angle = 0
        self.dots = ""

        self.build_ui()
        self.window.update()

    def build_ui(self):
        """Build User Interface."""
        self.main_frame.pack(expand=True)
        tk.Label(
            self.main_frame, text=self.message, bg="aliceblue", fg="blue",
            font=("Georgia", 12, "italic")
        ).pack(pady=(5, 2))
        self.canvas.pack(pady=2)
        self.pregress_label.pack(pady=(5, 0))
        self.wait_label.pack(pady=(2, 10))
        self.animate_spinner()
        self.animate_dots()

    def animate_spinner(self):
        """Rotate the Spinner."""
        if not self.window.winfo_exists():
            return

        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        self.window.after(40, self.animate_spinner)

    def animate_dots(self):
        """Animate the dots after 'Please wait'."""
        if not self.window.winfo_exists():
            return

        self.dots += "."
        if len(self.dots) > 3:
            self.dots = ""
        self.wait_label.config(text=f"Please Wait{self.dots}")
        self.window.after(400, self.animate_dots)

    def update_progress(self, text, percent=None):
        """Update progress text safely."""
        try:
            if percent is not None:
                text = f"{text} ({percent}%)"
            self.pregress_label.config(text=text)
            self.window.update_idletasks()
        except tk.TclError:
            pass

    def close(self):
        """Close Popup."""
        self.window.destroy()


class PreviewWindow:
    """Preview extracted dataframe before export."""
    def __init__(self, parent, title, dataframe, confirm_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("Preview Data")
        self.window.configure(bg="aliceblue")
        self.window.state("zoomed")
        self.window.grab_set()

        self.df = dataframe
        self.confirm_callback = confirm_callback
        self.file_name = title
        style = ttk.Style(self.window)
        style.theme_use("clam")
        style.configure("Treeview", font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
        self.main_frame = tk.Frame(
            self.window, bg="aliceblue", bd=4, relief="solid"
        )
        self.table_frame = tk.Frame(
            self.main_frame, bg="aliceblue", bd=2, relief="ridge"
        )
        self.tree = ttk.Treeview(
            self.table_frame, columns=list(self.df.columns), show="headings"
        )

        self.build_ui()

    def build_ui(self):
        self.main_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)
        # Buttons
        btn_frame = tk.Frame(self.main_frame, bg="aliceblue")
        btn_frame.pack(fill="x", padx=10)
        title_txt = self.file_name.capitalize()
        tk.Label(
            btn_frame, text=title_txt, bg="aliceblue", fg="purple",
            justify="center", font=("Georgia", 20, "bold", "italic", "underline")
        ).pack(side="left")
        tk.Button(
            btn_frame, text="Cancel", fg="red", bd=2, relief="groove",
            font=("Arial", 10, "bold"), command=self.window.destroy
        ).pack(side="right")
        tk.Button(
            btn_frame, text="Export", bg="green", fg="white", bd=2,
            relief="groove", font=("Arial", 10, "bold"), command=self.confirm_export
        ).pack(side="right")
        # Table Frame
        self.table_frame.pack(fill="both", expand=True)
        # Scrollbars
        y_scroll = tk.Scrollbar(
            self.table_frame, orient="vertical", command=self.tree.yview
        )
        x_scroll = tk.Scrollbar(
            self.table_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
        )
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Setup Columns
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=30, anchor="center")

        # Insert preview rows
        for _, row, in self.df.head(300).iterrows():
            formatted_row = [self.format_value(v) for v in row]
            self.tree.insert("", "end", values=formatted_row)

        self.auto_resize_treeview()

    def confirm_export(self):
        """Call callback from MainGUI."""
        self.window.destroy()
        self.confirm_callback()

    def auto_resize_treeview(self, preview_rows=300):
        """Automatically resize columns."""
        font = tkfont.Font()
        sample_df = self.df.head(preview_rows)

        for col in self.df.columns:
            max_width = font.measure(str(col))

            for value in sample_df[col]:
                text = str(self.format_value(value))
                width = font.measure(text)
                if width > max_width:
                    max_width = width

            self.tree.column(col, width=max_width + 5)

    @staticmethod
    def format_value(value):
        """Format number with separators."""
        if value is None:
            return ""

        try:
            if isinstance(value, float):
                if value.is_integer():
                    return f"{int(value):,}"
                return f"{value:,.2f}"

            if isinstance(value, int):
                return f"{value:,}"
        except Exception:
            pass
        return str(value)