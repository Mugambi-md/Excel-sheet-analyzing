import tkinter as tk
from tkinter import filedialog, messagebox
from base_window import BaseWindow
from read_files import InputReader, DataExtractor
from popups_gui import ColumnSelectorGUI

class MainGUI(BaseWindow):
    def __init__(self, parent):
        self.window = parent
        self.window.title("Data Frame Builder")
        self.center_window(self.window, 500, 450)
        self.window.configure(bg="aliceblue")
        self.window.grab_set()

        self.first_file = None
        self.second_file = None
        self.df_selected = None
        self.df_second_selected = None
        self.second_selected_columns = None
        self.join_key = None
        self.final_df = None
        self.ref_frame = None
        self.data_frame = None
        self.main_frame = tk.Frame(
            self.window, bg="aliceblue", bd=4, relief="solid"
        )

        self.build_ui()
    def build_ui(self):
        """Build user interface."""
        self.main_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)
        # Title 1
        tk.Label(
            self.main_frame, text="Load File With Reference Key Columns",
            bg="aliceblue", fg="blue", font=("Arial", 12, "bold", "underline")
        ).pack(pady=(5, 0), anchor="s")

        self.ref_frame = self.create_click_frame(
            "↓\nSelect xlsx, xls or CSV", self.load_reference_file
        )
        # Title 2
        tk.Label(
            self.main_frame, text="Load File With Columns to Build Data Frame",
            bg="aliceblue", fg="blue", font=("Arial", 12, "bold", "underline")
        ).pack(pady=(5, 0), anchor="s")
        self.data_frame = self.create_click_frame(
            "↓\nSelect xlsx, xls or CSV", self.load_second_file
        )
        # Export Button
        tk.Button(
            self.main_frame, text="Export data\nExcel/CSV", fg="green", bd=4,
            relief="groove", font=("Arial", 11, "bold"), command=self.export_data
        ).pack(pady=(10, 0))

    def create_click_frame(self, text, command):
        frame = tk.Frame(self.main_frame, height=100, bd=3, relief="ridge")
        frame.pack(fill="x", padx=10)
        frame.pack_propagate(False)

        label = tk.Label(frame, text=text, font=("Arial", 11, "italic"))
        label.pack(expand=True)

        frame.bind("<Button-1>", lambda e: command())
        label.bind("<Button-1>", lambda e: command())

        return frame

    # File loaders
    def load_reference_file(self):
        path = filedialog.askopenfilename(
            title="Select Reference File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv")
            ]
        )
        if not path:
            return
        self.first_file = path
        reader = InputReader(self.first_file)
        columns = reader.get_columns()

        selector = ColumnSelectorGUI(
            self.window, columns, "Select Reference Columns"
        )
        selected_columns = selector.selected_columns

        if not selected_columns:
            messagebox.showwarning(
                "No Selection", "No Columns Selected", parent=self.window
            )
            return
        self.join_key = selector.join_key.get()
        self.df_selected = reader.extract_columns(selected_columns)

        messagebox.showinfo(
            "Loaded", f"Reference File Loaded\nJoin Key: {self.join_key}.",
            parent=self.window
        )

    def load_second_file(self):
        path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv")
            ]
        )
        if not path:
            return
        reader = InputReader(path)
        columns = reader.get_columns()

        selector = ColumnSelectorGUI(
            self.window, columns, "Select Data Columns"
        )

        if not selector.selected_columns:
            return

        self.second_file = path
        self.df_second_selected = reader.extract_columns(
            selector.selected_columns
        )
        messagebox.showinfo(
            "Loaded", "Second File and Columns Loaded Successfully.",
            parent=self.window
        )

    def export_data(self):
        if self.df_selected is None or self.df_second_selected is None:
            messagebox.showerror(
                "Missing Data", "Load Both Files and Select Columns.",
                parent=self.window
            )
            return
        extractor = DataExtractor(self.second_file)
        self.final_df = extractor.left_join(
            df_left=self.df_selected,
            join_key=self.join_key
        )

        save_path = filedialog.asksaveasfilename(
            title="Save Output",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel file", "*.xlsx"),
                ("CSV files", "*.csv")
            ]
        )
        if not save_path:
            return

        if save_path.endswith(".csv"):
            self.final_df.to_csv(save_path, index=False)
        else:
            self.final_df.to_excel(save_path, index=False)

        messagebox.showinfo(
            "Success", f"File Exported Successfully to:\n{save_path}",
            parent=self.window
        )

if __name__ == "__main__":
    root = tk.Tk()
    # Enable DPI scaling (call once before widgets)
    BaseWindow.enable_dpi_scaling(root, scale=1.25)
    app = MainGUI(root)
    root.mainloop()