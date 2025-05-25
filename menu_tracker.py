import tkinter as tk
from tkinter import Menu

class TrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tracker App")

        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        # Store options_menu as attribute so we can update it later
        self.options_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Options", menu=self.options_menu)

        # Fill full menu at startup
        self.main_menu()

        # Setup other static menus
        self.setup_other_menus()

        # Placeholder buttons for testing
        tk.Button(self, text="Show Warm Storage", command=self.call_show_warm_storage).pack(pady=5)
        tk.Button(self, text="Show Cold Storage", command=self.call_show_cold_storage).pack(pady=5)
        tk.Button(self, text="Show Total Assets", command=self.call_show_total_assets).pack(pady=5)
        tk.Button(self, text="Back to Main", command=self.return_to_main_screen).pack(pady=5)

    def main_menu(self):
        # Options menu
        self.options_menu.delete(0, 'end')
        self.options_menu.add_command(label="Warm Storage", command=self.call_show_warm_storage)
        self.options_menu.add_command(label="Cold Storage", command=self.call_show_cold_storage)
        self.options_menu.add_command(label="Input Stocks", command=lambda: self.set_total_stocks())
        self.options_menu.add_command(label="Total Assets", command=self.call_show_total_assets)

        # External menu
        external_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Live View", menu=external_menu)
        external_menu.add_command(label="Fear and Greed", command=self.call_fear_and_greed)
        external_menu.add_command(label="AGGR Live View", command=self.call_aggr_window)
        external_menu.add_command(label="Mempool", command=self.call_mempool_window)
        external_menu.add_command(label="CoinTelegraph", command=self.call_cte_window)

        # History menu
        history_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="CSV Data", menu=history_menu)
        history_menu.add_command(label="Load & Calculate", command=self.call_csv_window)

        # Config menu
        config_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Config", menu=config_menu)
        config_menu.add_command(label="Parameters", command=self.add_warm_storage)
        config_menu.add_command(label="Open Excel", command=lambda: self.open_excel_file('tracker.xlsx'))
        config_menu.add_command(label="Init Excel", command=self.init_excel)

        # About menu
        about_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About", command=self.call_show_about)

    def sub_menu(self):
        self.options_menu.delete(0, 'end')
        self.options_menu.add_command(label="Write Data", command=self.write_data_function)
        self.options_menu.add_command(label="Back to Main", command=self.return_to_main_screen)


    def call_show_warm_storage(self):
        self.sub_menu()
        print("Warm Storage screen opened")

    def call_show_cold_storage(self):
        self.sub_menu()
        print("Cold Storage screen opened")

    def call_show_total_assets(self):
        self.sub_menu()
        print("Total Assets screen opened")

    def return_to_main_screen(self):
        self.main_menu()
        print("Returned to Main Screen")

    def write_data_function(self):
        print("Write Data function called")

    def set_total_stocks(self):
        print("Input Stocks triggered")

    def call_fear_and_greed(self):
        print("Fear and Greed view opened")

    def call_aggr_window(self):
        print("AGGR Live View opened")

    def call_mempool_window(self):
        print("Mempool window opened")

    def call_cte_window(self):
        print("CoinTelegraph window opened")

    def call_csv_window(self):
        print("CSV Load & Calculate opened")

    def add_warm_storage(self):
        print("Parameters setup opened")

    def open_excel_file(self, filename):
        print(f"Opening Excel file: {filename}")

    def init_excel(self):
        print("Excel initialized")

    def call_show_about(self):
        print("About dialog opened")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
