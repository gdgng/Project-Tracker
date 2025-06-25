import tkinter as tk
from tkinter import ttk
import configparser
import os

# Configuration file name
CONFIG_FILE = "tracker.cfg"

class ConfigTracker(tk.Tk):
    """
    A GUI application for managing configuration settings with a user-friendly interface.

    This class creates a window with four sections:
    - Refresh Rate: Dropdown menus for setting refresh intervals
    - Write Data: Checkboxes for enabling data writing options
    - Optional URL: Text entry for live view URL
    - Miscellaneous Options: Various boolean settings
    """

    def __init__(self, parent=None):
        """Initialize the Config Tracker application."""
        # Fix 1: Allow parent parameter and handle it properly
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)

        # Window configuration
        self.geometry("600x500")
        self.title("Config Tracker - Crypto Price Tracker V1.1")

        # Fix 2: Better error handling for icon loading
        self.load_icon()

        # Initialize configuration parser and load existing settings
        self.config = configparser.ConfigParser()
        self.load_config()

        # Create the GUI
        self.create_gui()

    def load_icon(self):
        """Load application icon with proper error handling."""
        icon_paths = [
            os.path.join(os.getcwd(), "crypto", "config.ico"),
            os.path.join(os.getcwd(), "config.ico"),
            os.path.join(os.path.dirname(__file__), "crypto", "config.ico"),
            os.path.join(os.path.dirname(__file__), "config.ico")
        ]

        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
                    break
            except (tk.TclError, FileNotFoundError):
                continue

    def create_gui(self):
        """Create the main GUI elements."""
        # Create main container frame for the top row sections
        main_frame = tk.Frame(self)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # ===== REFRESH RATE SECTION (Top Left) =====
        refresh_frame = tk.LabelFrame(main_frame, text="Refresh Rate", font=("Arial", 12, "bold"),
                                      relief="solid", bd=2, padx=10, pady=10)
        refresh_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Available refresh rate values in seconds
        self.refresh_values = [30, 60, 120, 180, 240, 300]

        # Initialize StringVar variables for refresh rate dropdowns
        self.main_var = tk.StringVar(value=self.config.get("RefreshRate", "Main", fallback="180"))
        self.warm_var = tk.StringVar(value=self.config.get("RefreshRate", "Warm", fallback="30"))
        self.cold_var = tk.StringVar(value=self.config.get("RefreshRate", "Cold", fallback="30"))
        self.total_var = tk.StringVar(value=self.config.get("RefreshRate", "Total", fallback="30"))

        # Create dropdown menus for each refresh rate setting
        self.create_dropdown(refresh_frame, "Main", self.main_var)
        self.create_dropdown(refresh_frame, "Warm", self.warm_var)
        self.create_dropdown(refresh_frame, "Cold", self.cold_var)
        self.create_dropdown(refresh_frame, "Total", self.total_var)

        # ===== WRITE DATA SECTION (Top Right) =====
        write_frame = tk.LabelFrame(main_frame, text="Write Data", font=("Arial", 12, "bold"),
                                    relief="solid", bd=2, padx=10, pady=10)
        write_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Initialize BooleanVar variables for write data checkboxes
        self.write_warm = tk.BooleanVar(value=self.config.getboolean("WriteData", "Warm", fallback=False))
        self.write_cold = tk.BooleanVar(value=self.config.getboolean("WriteData", "Cold", fallback=False))
        self.write_total = tk.BooleanVar(value=self.config.getboolean("WriteData", "Total", fallback=True))
        self.write_csv = tk.BooleanVar(value=self.config.getboolean("WriteData", "CSV", fallback=True))

        # Create checkboxes for each write data option
        self.create_checkbox(write_frame, "Warm Storage", self.write_warm)
        self.create_checkbox(write_frame, "Cold Storage", self.write_cold)
        self.create_checkbox(write_frame, "Total Assets", self.write_total)
        self.create_checkbox(write_frame, "CSV Load & Calc", self.write_csv)

        # Create second row container frame for the bottom sections
        second_row_frame = tk.Frame(self)
        second_row_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # ===== OPTIONAL URL SECTION (Bottom Left) =====
        url_frame = tk.LabelFrame(second_row_frame, text="Optional URLs (live View)", font=("Arial", 12, "bold"),
                                  relief="solid", bd=2, padx=10, pady=10)
        url_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Initialize StringVar variables for three URL and Name entries
        self.url1_var = tk.StringVar(value=self.config.get("OptionalURL", "URL1", fallback=""))
        self.Name1_var = tk.StringVar(value=self.config.get("OptionalURL", "Name1", fallback=""))
        self.url2_var = tk.StringVar(value=self.config.get("OptionalURL", "URL2", fallback=""))
        self.Name2_var = tk.StringVar(value=self.config.get("OptionalURL", "Name2", fallback=""))
        self.url3_var = tk.StringVar(value=self.config.get("OptionalURL", "URL3", fallback=""))
        self.Name3_var = tk.StringVar(value=self.config.get("OptionalURL", "Name3", fallback=""))

        # Create URL entry fields
        self.create_url_entry(url_frame, "Optional URL  1", self.url1_var)
        self.create_url_entry(url_frame, "Optional Name 1", self.Name1_var)
        self.create_url_entry(url_frame, "Optional URL  2", self.url2_var)
        self.create_url_entry(url_frame, "Optional Name 2", self.Name2_var)
        self.create_url_entry(url_frame, "Optional URL  3", self.url3_var)
        self.create_url_entry(url_frame, "Optional Name 3", self.Name3_var)

        # ===== MISCELLANEOUS OPTIONS SECTION (Bottom Right) =====
        misc_frame = tk.LabelFrame(second_row_frame, text="Miscellaneous Options", font=("Arial", 12, "bold"),
                                   relief="solid", bd=2, padx=10, pady=10)
        misc_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Initialize BooleanVar variables for miscellaneous options
        self.debug_mode = tk.BooleanVar(value=self.config.getboolean("Miscellaneous", "DebugMode", fallback=False))
        self.day_mod = tk.BooleanVar(value=self.config.getboolean("Miscellaneous", "darkmod", fallback=True))
        self.DemoMode = tk.BooleanVar(value=self.config.getboolean("Miscellaneous", "DemoMode", fallback=False))
        self.Cold_Aval = tk.BooleanVar(value=self.config.getboolean("Miscellaneous", "Cold Storage Available", fallback=False))

        # Create checkboxes for miscellaneous options
        self.create_checkbox(misc_frame, "Debug Mode", self.debug_mode)
        self.create_checkbox(misc_frame, "Dark mode activated", self.day_mod)
        self.create_checkbox(misc_frame, "Demo Mode", self.DemoMode)
        self.create_checkbox(misc_frame, "Cold Storage Available", self.Cold_Aval)

        # ===== SAVE BUTTON =====
        tk.Button(self, text="Save Config", command=self.save_config).pack(pady=10)

    def create_dropdown(self, parent, label, var):
        """Create a dropdown (combobox) widget with a label."""
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill="x")
        tk.Label(frame, text=label, width=10).pack(side="left")
        ttk.Combobox(frame, textvariable=var, values=self.refresh_values, width=10).pack(side="right")

    def create_checkbox(self, parent, label, var):
        """Create a checkbox widget with a label."""
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill="x")
        tk.Checkbutton(frame, text=label, variable=var, onvalue=True, offvalue=False).pack(anchor="w")

    def create_url_entry(self, parent, label, var):
        """Create a text entry widget with a label for URL input."""
        frame = tk.Frame(parent)
        frame.pack(pady=2, fill="x")
        tk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
        tk.Entry(frame, textvariable=var, width=25).pack(side="right", fill="x", expand=True)

    def load_config(self):
        """Load settings from the configuration file if it exists."""
        try:
            if os.path.exists(CONFIG_FILE):
                self.config.read(CONFIG_FILE)
        except (configparser.Error, IOError) as e:
            print(f"Error loading config file: {e}")
            # Continue with default values

    def save_config(self):
        """Save current settings to the configuration file."""
        try:
            # Save refresh rate settings
            if not self.config.has_section("RefreshRate"):
                self.config.add_section("RefreshRate")
            self.config["RefreshRate"] = {
                "Main": self.main_var.get(),
                "Warm": self.warm_var.get(),
                "Cold": self.cold_var.get(),
                "Total": self.total_var.get()
            }

            # Save write data settings
            if not self.config.has_section("WriteData"):
                self.config.add_section("WriteData")
            self.config["WriteData"] = {
                "Warm": str(self.write_warm.get()),
                "Cold": str(self.write_cold.get()),
                "Total": str(self.write_total.get()),
                "CSV": str(self.write_csv.get())
            }

            # Save optional URL and Name settings
            if not self.config.has_section("OptionalURL"):
                self.config.add_section("OptionalURL")
            self.config["OptionalURL"] = {
                "URL1": self.url1_var.get(),
                "Name1": self.Name1_var.get(),
                "URL2": self.url2_var.get(),
                "Name2": self.Name2_var.get(),
                "URL3": self.url3_var.get(),
                "Name3": self.Name3_var.get()
            }

            # Save miscellaneous options
            if not self.config.has_section("Miscellaneous"):
                self.config.add_section("Miscellaneous")
            self.config["Miscellaneous"] = {
                "DebugMode": str(self.debug_mode.get()),
                "darkmod": str(self.day_mod.get()),
                "DemoMode": str(self.DemoMode.get()),
                "Cold Storage Available": str(self.Cold_Aval.get())
            }

            # Write all settings to the configuration file
            with open(CONFIG_FILE, "w") as configfile:
                self.config.write(configfile)

            print("Configuration saved successfully.")

        except (IOError, OSError) as e:
            print(f"Error saving configuration: {e}")

    def get_config_dict(self):
        """Return current configuration as a dictionary for external access."""
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config[section])
        return config_dict

def create_config_window(parent=None):
    """Factory function to create a ConfigTracker window."""
    return ConfigTracker(parent)

def run_standalone():
    """Run the application in standalone mode."""
    app = ConfigTracker()
    app.mainloop()

# Application entry point
if __name__ == "__main__":
    run_standalone()
