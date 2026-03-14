import threading
from tkinter import messagebox
from popups_gui import LoadingPopup


class ThreadHelper:
    """Reusable background task runner with loader popup."""

    @staticmethod
    def run(parent, task_func, finish_func=None, message="Processing..."):
        """
        Run a task in background thread with a loader popup.

        :param parent: Tk window
        :param task_func: function that performs heavy work (returns result)
        :param finish_func: function (result) executed on UI thread
        :param message: loader message
        """

        loader = LoadingPopup(parent, message)

        def progress_callback(text, percent):
            """Update loader progress safely."""
            parent.after(0, lambda: loader.update_progress(text, percent))

        def worker():
            try:
                result = task_func(progress_callback)
                def finish():
                    loader.close()
                    if finish_func:
                        finish_func(result)

                parent.after(0, finish)

            except Exception as e:
                def error(err=e):
                    loader.close()
                    messagebox.showerror("Error", str(err), parent=parent)

                parent.after(0, error)

        threading.Thread(target=worker, daemon=True).start()