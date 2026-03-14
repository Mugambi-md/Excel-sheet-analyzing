from tkinterdnd2 import DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
from base_window import BaseWindow, ScrollableFrame
from read_files import InputReader, DataExtractor
from popups_gui import ColumnSelectorGUI, PreviewWindow
from utils import ThreadHelper


class MainGUI(BaseWindow):
    def __init__(self, parent):
        self.window = parent
        self.window.title("DataSieve")
        icon_path = self._get_resource_path("myicon.ico")
        self.window.iconbitmap(icon_path)
        self.center_window(self.window, 400, 450)
        self.window.configure(bg="aliceblue")
        self.window.grab_set()

        self.ref_frame = None
        self.ref_label = None
        self.data_frame = None
        self.data_label = None
        self.first_file = None
        self.second_file = None
        self.df_selected = None
        self.df_second_selected = None
        self.join_key = None
        self.final_df = None

        self.main_frame = tk.Frame(
            self.window, bg="aliceblue", bd=4, relief="solid"
        )
        self.top_frame = tk.Frame(self.main_frame, bg="aliceblue")
        self.menu_btn = tk.Label(
            self.top_frame, text="⁞", bg="aliceblue", cursor="hand2",
            font=("Arial", 20, "bold")
        )
        self.side_menu = ScrollableFrame(self.window, bg="white", width=270)

        self.build_ui()

    @staticmethod
    def _get_resource_path(relative_path):
        """Get absolute path to resource (works for Pyinstaller)."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def build_ui(self):
        """Build user interface."""
        self.main_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)
        self.top_frame.pack(side="top", fill="x", pady=(0, 10))
        self.menu_btn.pack(side="left", padx=(3, 10))
        self.menu_btn.bind("<Button-1>", lambda e: self.open_side_menu())
        # Window Title
        tk.Label(
            self.top_frame, text="Sieve Data", bg="aliceblue", fg="purple",
            font=("Georgia", 22, "bold", "italic", "underline")
        ).pack(anchor="center")
        # Title 1
        tk.Label(
            self.main_frame, text="Upload Sheet to Reference From", fg="blue",
            bg="aliceblue", font=("Arial", 14, "bold", "italic")
        ).pack(pady=(10, 0), anchor="s")

        self.ref_frame, self.ref_label = self.create_click_frame(
            "↓\nSelect xlsx, xls or CSV",
            self.load_reference_file,
            self.load_reference_file
        )
        # Title 2
        tk.Label(
            self.main_frame, text="Upload Sheet to Sieve From", fg="blue",
            bg="aliceblue", font=("Arial", 14, "bold", "italic")
        ).pack(pady=(10, 0), anchor="s")
        self.data_frame, self.data_label = self.create_click_frame(
            "↓\nSelect xlsx, xls or CSV",
            self.load_second_file,
            self.load_second_file
        )
        # Export Button
        tk.Button(
            self.main_frame, text="Export", bg="green", fg="white", bd=4,
            relief="groove", font=("Arial", 12, "bold"), height=1,
            command=self.export_data
        ).pack(pady=10)
        tk.Label(
            self.main_frame, text="©SwiftGlance2026", bg="aliceblue",
            font=("Arial", 11, "italic")
        ).pack(pady=10, anchor="center")

    def create_click_frame(self, text, command, drop_callback):
        """Creates a clickable frame to upload file."""
        frame = tk.Frame(self.main_frame, height=80, bd=2, relief="groove")
        frame.pack(fill="x", padx=10)
        frame.pack_propagate(False)

        label = tk.Label(
            frame, text=text, fg="blue", wraplength=250, font=("Arial", 12, "italic")
        )
        label.pack(expand=True)

        frame.bind("<Button-1>", lambda e: command())
        label.bind("<Button-1>", lambda e: command())
        # Drag & Drop support
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind("<<Drop>>", lambda e: drop_callback(e.data))

        return frame, label

    # Normalize dropped path
    @staticmethod
    def _normalize_dropped_path(data):
        path = data.strip()
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        return path

    # File loaders
    def load_reference_file(self, path=None):
        """Loading file for data referencing while extracting from Second file."""
        if not path:
            path = filedialog.askopenfilename(
                title="Select Reference File",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv")
                ]
            )
        else:
            path = self._normalize_dropped_path(path)

        if not path:
            return
        self.first_file = path
        filename = os.path.basename(path)
        self.ref_label.config(text=filename, fg="green")
        # Show loader
        ThreadHelper.run(
            parent=self.window,
            message="Uploading Reference File...",
            task_func=self._load_reference_task,
            finish_func=self._load_reference_finish
        )

    def _load_reference_task(self, progress):
        """Background loader for reference file."""
        progress("Opening Reference File...", 10)
        reader = InputReader(self.first_file)
        progress("Reading Column Headers...", 50)
        columns = reader.get_columns()
        progress("Preparing Column Selector...", 90)

        return reader, columns

    def _load_reference_finish(self, result):
        """Background loader for reference file."""
        reader, columns = result

        selector = ColumnSelectorGUI(
            self.window, columns, "Select Reference Columns"
        )
        if not selector.selected_columns:
            messagebox.showwarning(
                "No Selection", "No Columns Selected", parent=self.window
            )
            return
        self.join_key = selector.join_key.get()
        self.df_selected = reader.extract_columns(selector.selected_columns)
        messagebox.showinfo(
            "Loaded", "Reference File Loaded Successfully.\n"
            f"Join Key: {self.join_key}.", parent=self.window
            )

    def load_second_file(self, path=None):
        """Loading second file to extract data."""
        if not path:
            path = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=[
                    ("Excel files", "*.xlsx *.xls"),
                    ("CSV files", "*.csv")
                ]
            )
        else:
            path = self._normalize_dropped_path(path)

        if not path:
            return
        self.second_file = path
        filename = os.path.basename(path)
        self.data_label.config(text=filename, fg="green")
        # Show loader
        ThreadHelper.run(
            parent=self.window,
            message="Uploading Main Data File...",
            task_func=self._load_second_task,
            finish_func=self._load_second_finish
        )

    def _load_second_task(self, progress):
        """Background loader for second file."""
        progress("Opening Main Data File...", 10)
        reader = InputReader(self.second_file)
        progress("Reading Column Headers...", 50)
        columns = reader.get_columns()
        progress("Preparing Column Selector...", 90)
        return reader, columns

    def _load_second_finish(self, result):
        reader, columns = result
        selector = ColumnSelectorGUI(
            self.window, columns, "Select Columns You Want Data From"
        )
        if not selector.selected_columns:
            messagebox.showwarning(
                "No Selection", "No Columns Selected", parent=self.window
            )
            return
        self.df_second_selected = reader.extract_columns(
            selector.selected_columns
        )
        messagebox.showinfo(
            "Loaded", "Second File Loaded Successfully.", parent=self.window
        )

    @staticmethod
    def generate_unique_filename(directory, base_name, extension):
        """generate a unique filename by adding number if file exists."""
        counter = 0
        file_name = f"{base_name}{extension}"
        full_path = os.path.join(directory, file_name)
        while os.path.exists(full_path):
            counter += 1
            file_name = f"{base_name}_{counter}{extension}"
            full_path = os.path.join(directory, file_name)
        return file_name

    def export_data(self):
        if self.df_selected is None or self.df_second_selected is None:
            messagebox.showerror(
                "Missing Data", "Load Both Files and Select Columns.",
                parent=self.window
            )
            return
        # Show loader
        ThreadHelper.run(
            parent=self.window,
            message="Exporting Data File...",
            task_func=self._export_task,
            finish_func=self._export_finish
        )

    def _export_task(self, progress):
        """Background Export Process."""
        progress("Preparing Extractor...", 10)
        extractor = DataExtractor(self.second_file)

        progress("Matching Reference Data...", 40)
        result = extractor.left_join(
            df_left=self.df_selected,
            df_right=self.df_second_selected,
            join_key=self.join_key
        )

        progress("Preparing Preview...", 80)

        progress("Done.", 100)

        return result

    def _export_finish(self, final_df):
        self.final_df = final_df
        self.preview_window()

    def open_side_menu(self):
        """Show the left side Menu."""
        self.side_menu.place(x=0, y=0, height=self.window.winfo_height())
        inside_frame = self.side_menu.scrollable_frame
        # Clear Previous widgets
        for w in inside_frame.winfo_children():
            w.destroy()
        # Close button
        close_btn = tk.Label(
            inside_frame, text="X", bg="white", fg="red", cursor="hand2",
            font=("Arial", 12)
        )
        close_btn.pack(anchor="ne", padx=5)
        close_btn.bind("<Button-1>", lambda e: self.close_side_menu())
        # How it works \u2753
        self.collapsible_section(
            parent=inside_frame, title="How It Works ?", context_text=(
                "DataSieve.\n\nThis application extracts data from large "
                "Excel or CSV files by matching columns.\nUpload the first "
                "data sheet (Excel or CSV) in reference frame that has or "
                "original data that you want to select in overall sheet (data"
                " sheet in data frame). Select columns that will be available "
                "also in data sheet, select one reference column that has "
                "unique values across all rows in the sheet.\nSelect and "
                "upload main data sheet (overall sheet) in data frame that "
                "contain all data to select the columns you selected earlier "
                "in the first data sheet. Select columns that you want to "
                "pick from overall data sheet. Press Confirm button "
                "and Export button to create a new CSV or Excel Sheet"
            ),
            text_font=("Arial", 11)
        )
        # Menu buttons (About)
        self.collapsible_section(
            parent=inside_frame, title="About (App Info)", context_text=(
                "DataSieve.\n\nThis application extracts data from two large"
                " Excel or CSV files by matching reference columns and creates"
                " one sheet (CSV or Excel) on pressing export button.\n"
                "It helps automate spreadsheet data filtering and sorting.\n\n"
                "Version: V1.0\nBuild: Desktop Edition\nAuthor: Mugambi(Swift"
                "Glance)\nEmail: mugambi4sm@gmail.com\n©SwiftGlance2026"
                " All rights reserved."
            ),
            text_font=("Arial", 11, "italic")
        )

    def close_side_menu(self):
        """Hide the side menu."""
        self.side_menu.place_forget()

    @staticmethod
    def collapsible_section(parent, title, context_text, text_font):
        """Creates a collapsible menu section."""
        container = tk.Frame(parent, bg="white")
        container.pack(fill="x", pady=(0, 2))

        header = tk.Frame(container, bg="white")
        header.pack(fill="x")

        arrow = tk.Label(
            header, text="v", bg="white", fg="green", font=("Arial", 12, "bold")
        )
        arrow.pack(side="right", padx=5)

        title_lbl = tk.Label(
            header, text=title, bg="white", fg="green", cursor="hand2",
            font=("Arial", 14, "bold")
        )
        title_lbl.pack(side="left", padx=10, pady=(5, 0))
        content = tk.Label(
            container, text=context_text, bg="white", justify="left",
            wraplength=255, font=text_font
        )
        content_visible = False

        def toggle():
            nonlocal content_visible

            if content_visible:
                content.pack_forget()
                arrow.config(text="v")
                content_visible = False
            else:
                content.pack(padx=5, pady=5)
                arrow.config(text="ʌ")
                content_visible = True

        header.bind("<Button-1>", lambda e: toggle())
        title_lbl.bind("<Button-1>", lambda e: toggle())
        arrow.bind("<Button-1>", lambda e: toggle())

    def preview_window(self):
        """Open Preview window."""
        ref_name = os.path.basename(self.first_file)
        ref_base = os.path.splitext(ref_name)[0]
        file_name = f"{ref_base}_updated"
        PreviewWindow(
            parent=self.window,
            title=file_name,
            dataframe=self.final_df,
            confirm_callback=lambda: self.confirm_export()
        )

    def confirm_export(self):
        """Save file after confirmation."""
        # Create default filename and save location based on reference file
        ref_name = os.path.basename(self.first_file)
        ref_base = os.path.splitext(ref_name)[0]

        initial_dir = os.path.dirname(self.first_file)
        base_name = f"{ref_base}_updated"
        # Default extension
        extension = ".xlsx"
        default_name = self.generate_unique_filename(
            initial_dir, base_name, extension
        )
        save_path = filedialog.asksaveasfilename(
            title="Save Output",
            initialdir=initial_dir,
            initialfile=default_name,
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
        self.reset_state()
        messagebox.showinfo(
            "Success", f"File Exported Successfully to:\n{save_path}",
            parent=self.window
        )

    def reset_state(self):
        """Reset UI after Export."""
        self.ref_label.config(text="↓\nSelect xlsx, xls or CSV", fg="blue")
        self.data_label.config(text="↓\nSelect xlsx, xls or CSV", fg="blue")
        self.first_file = None
        self.second_file = None
        self.df_selected = None
        self.df_second_selected = None
        self.join_key = None
        self.final_df = None

if __name__ == "__main__":
    from tkinterdnd2 import TkinterDnD
    root = TkinterDnD.Tk()
    # Enable DPI scaling (call once before widgets)
    BaseWindow.enable_dpi_scaling(root, scale=1.25)
    app = MainGUI(root)
    root.mainloop()