import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from automation import Automation, settings
from app.core.excel_handler import ExcelHandler
from app.ui.mapping_popup import MappingPopup

# Optional drag-and-drop support via tkinterdnd2 (install separately if needed)
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False


class MainFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.username = ctk.StringVar()
        self.password = ctk.StringVar()
        self.status_text = ctk.StringVar(value="🟡 Waiting for input...")
        self.excel_file = None
        self.mapped_headers = {}
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = ctk.CTkLabel(self, text="⚙️ Automation Portal", font=("Helvetica", 24, "bold"))
        title.pack(pady=(30, 5))

        subtitle = ctk.CTkLabel(self, text="Configure credentials and upload Excel to begin",
                                font=("Helvetica", 13), text_color="#A0A0A0")
        subtitle.pack(pady=(0, 20))

        # Credentials
        creds = ctk.CTkFrame(self, corner_radius=10)
        creds.pack(pady=10, padx=20, fill="x")
        # Use grid with column weight so entries expand/shrink and avoid overflow
        creds.grid_columnconfigure(0, weight=0)
        creds.grid_columnconfigure(1, weight=1)
        creds.grid_columnconfigure(2, weight=0)
        creds.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(creds, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        # remove fixed width and let grid manage expansion
        ctk.CTkEntry(creds, textvariable=self.username).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(creds, text="Password:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(creds, textvariable=self.password, show="*").grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Excel Upload
        # Drag & drop area (falls back to button if DnD not available)
        dnd_available = DND_AVAILABLE
        if dnd_available:
            # Use a CTkFrame containing an instruction label to receive drops
            drop_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1f1f2e")
            drop_frame.pack(pady=20, padx=40, fill="x")
            drop_label = ctk.CTkLabel(drop_frame, text="Drag & drop Excel file here or click to select",
                                      font=("Helvetica", 14))
            drop_label.pack(padx=20, pady=20, fill="both")
            # Bind click to open file dialog
            drop_label.bind("<Button-1>", lambda e: self.browse_excel())

            # Register drop target on the underlying tk widget if available
            try:
                # get the underlying tk widget and register
                widget = drop_label._apply_widgets()[0]
            except Exception:
                # fallback to using the master root
                widget = self.master

            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', self.on_drop)
            except Exception:
                # best-effort: if registration fails, fall back to button
                dnd_available = False

        if not dnd_available:
            self.upload_btn = ctk.CTkButton(
                self,
                text="🗂️ Select Excel File",
                width=400,
                height=80,
                fg_color="#1f1f2e",
                hover_color="#233f70",
                font=("Helvetica", 14),
                command=self.browse_excel
            )
            self.upload_btn.pack(pady=30)

        # Download Folder
        self.next_btn = ctk.CTkButton(
            self,
            text="📁 Select Download Folder",
            width=250,
            height=40,
            state="disabled",
            command=self.select_folder
        )
        self.next_btn.pack(pady=10)

        # Status
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(pady=(30, 5), fill="x", padx=20)
        ctk.CTkLabel(status_frame, textvariable=self.status_text, anchor="w").pack(side="left", padx=10, pady=5)
        self.progress = ctk.CTkProgressBar(status_frame)
        self.progress.pack(side="right", fill="x", expand=True, padx=10)
        self.progress.set(0)

    def browse_excel(self):
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file:
            return
        self.excel_file = file
        try:
            headers = ExcelHandler.read_headers(file)
            MappingPopup(self, headers, self.mapping_done)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read Excel file:\n{e}")

    def on_drop(self, event):
        """Handle files dropped onto the UI (expects DND_FILES format)."""
        try:
            data = event.data
        except Exception:
            # Some bindings provide the data as a string directly
            data = getattr(event, 'data', None)

        if not data:
            return

        # tkinterdnd2 provides a string with filenames separated by spaces and
        # possibly enclosed in braces if they contain spaces. Use tk.splitlist
        try:
            paths = self.master.tk.splitlist(data)
        except Exception:
            # naive fallback
            paths = [p.strip() for p in data.split()]

        # pick the first valid Excel file
        excel_path = None
        for p in paths:
            # remove surrounding braces
            if p.startswith('{') and p.endswith('}'):
                p = p[1:-1]
            if os.path.isfile(p) and p.lower().endswith(('.xlsx', '.xls')):
                excel_path = os.path.abspath(p)
                break

        if not excel_path:
            messagebox.showerror("Invalid file", "Please drop a valid Excel file (.xlsx or .xls).")
            return

        # Set and process the file (same flow as browse)
        self.excel_file = excel_path
        try:
            headers = ExcelHandler.read_headers(excel_path)
            MappingPopup(self, headers, self.mapping_done)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read dropped Excel file:\n{e}")

    def mapping_done(self, mapping):
        self.mapped_headers = mapping
        # Save mapping and selected file into global settings so other parts
        # of the app can access them immediately.
        try:
            if self.excel_file:
                abs_path = os.path.abspath(self.excel_file)
            else:
                abs_path = None

            cfg = {
                "excel_file": abs_path,
                "header_mapping": self.mapped_headers,
            }
            # include credentials if present
            if self.username.get():
                cfg["username"] = self.username.get()
            if self.password.get():
                cfg["password"] = self.password.get()

            settings.config(cfg)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not persist mapping to settings: {e}")

        messagebox.showinfo("Success", "Header mapping completed successfully!")
        self.next_btn.configure(state="normal")
        # update status area with selected file and mapping summary
        if abs_path:
            self.update_status(f"🟢 File selected: {abs_path}", progress=0)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if not folder:
            return

        if not self.username.get() or not self.password.get():
            messagebox.showerror("Error", "Please enter Username and Password.")
            return

        settings.config({
            "username": self.username.get(),
            "password": self.password.get(),
            "excel_file": self.excel_file,
            "header_mapping": self.mapped_headers,
            "download_folder": folder
        })

        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        try:
            self.update_status("🔵 Running automation...", progress=0.2)
            automation = Automation()
            automation.run()
            for i in range(1, 6):
                self.update_status(f"📄 Processing step {i}/5...", progress=i / 5)
                self.master.after(300)
            self.update_status("✅ Completed successfully!", progress=1.0)
        except Exception as e:
            self.update_status(f"❌ Error: {e}", progress=0)

    def update_status(self, text, progress=None):
        self.status_text.set(text)
        if progress is not None:
            self.progress.set(progress)
