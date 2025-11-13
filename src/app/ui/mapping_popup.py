import customtkinter as ctk
from tkinter import messagebox

class MappingPopup(ctk.CTkToplevel):
    def __init__(self, master, headers, on_confirm):
        super().__init__(master)
        self.headers = headers
        self.on_confirm = on_confirm
        self.mapping_vars = {}
        self.option_menus = {}
        self.selected_headers = set()

        self.configure_window()
        self.create_ui()

    def configure_window(self):
        self.title("Map Excel Headers")
        self.geometry("550x500")
        self.resizable(False, False)
        self.grab_set()  # Make popup modal

    def create_ui(self):
        ctk.CTkLabel(
            self,
            text="🧩 Map Excel Headers",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(20, 10))

        desc = (
            "Select corresponding Excel columns for each field below.\n"
            "Each Excel header can only be mapped once."
        )
        ctk.CTkLabel(
            self,
            text=desc,
            text_color="#A0A0A0",
            font=("Helvetica", 12),
            justify="center"
        ).pack(pady=(0, 20))

        # Required mapping fields
        fields = {
            "ACCOUNT_NAME": "ACCOUNT NAME",
            "ORDER_ID": "AUTO NAME",
            "REPORT_TYPE": "REPORT TYPE",
            "REPORT_NAME": "REPORT NAME",
            "PRIORITY": "PRIORITY",
            "PAGE": "PAGE",
        }

        # Container frame for dropdowns
        self.dropdown_frame = ctk.CTkScrollableFrame(self)
        self.dropdown_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Build dropdowns dynamically
        for key, label in fields.items():
            frame = ctk.CTkFrame(self.dropdown_frame, corner_radius=10)
            frame.pack(pady=6, fill="x")

            ctk.CTkLabel(frame, text=f"{key}:", width=150).pack(side="left", padx=10)
            var = ctk.StringVar(value="")
            menu = ctk.CTkOptionMenu(
                frame,
                variable=var,
                values=self.headers,
                width=300,
                command=lambda choice, f=key: self.on_selection(f, choice)
            )
            menu.pack(side="right", padx=10)

            self.mapping_vars[key] = var
            self.option_menus[key] = menu

        # Confirm button
        ctk.CTkButton(
            self,
            text="✅ Confirm Mapping",
            command=self.confirm,
            width=200,
            height=40
        ).pack(pady=25)

    def on_selection(self, field, choice):
        """Handle dropdown change and disable the selected value in other dropdowns."""
        prev_value = getattr(self, f"_prev_{field}", None)
        if prev_value:
            self.selected_headers.discard(prev_value)

        if choice:
            self.selected_headers.add(choice)
        setattr(self, f"_prev_{field}", choice)

        # Update dropdowns to remove selected items
        for f, menu in self.option_menus.items():
            current_val = self.mapping_vars[f].get()
            available = [h for h in self.headers if h not in self.selected_headers or h == current_val]
            menu.configure(values=available)

    def confirm(self):
        mapping = {}
        for field, var in self.mapping_vars.items():
            value = var.get()
            if not value:
                messagebox.showerror("Missing Field", f"Please map all fields before confirming.\nField missing: {field}")
                return
            mapping[field] = value

        print("\n✅ Final Mapping Object:")
        for k, v in mapping.items():
            print(f"  {k} → {v}")

        messagebox.showinfo("Success", "All fields mapped successfully!")
        self.on_confirm(mapping)
        self.destroy()
