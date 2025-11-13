import customtkinter as ctk
from app.ui.theme import apply_theme
from app.ui.main_frame import MainFrame
import threading
import sys
from tkinter import messagebox


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_theme()
        self.title("Automation Tool")
        width, height = 600, 500
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = MainFrame(self)
        frame.pack(expand=True, fill="both")

    def on_close(self):
        active_threads = [t for t in threading.enumerate() if t is not threading.main_thread()]
        if len(active_threads) > 0:
            if not messagebox.askyesno("Exit?", "Background tasks are running. Quit anyway?"):
                return
        self.destroy()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.mainloop()