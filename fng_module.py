import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.animation as animation
import time
import tkinter as tk
from tkinter import ttk, Menu, messagebox, Button, PhotoImage, scrolledtext as tkscroll
from PIL import Image, ImageTk
import os
import matplotlib
#matplotlib.rcParams['toolbar'] = 'None'

# IMPORTANT: Import your CryptoTicker class from its module
from crypto_ticker_module import CryptoTicker
global is_tracker_active
is_tracker_active=False
# --- CryptoData Class (No changes needed, kept for completeness) ---
class CryptoData:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    def fetch_bitcoin_price(self):
        try:
            url = f"{self.base_url}/simple/price"
            params = { 'ids': 'bitcoin', 'vs_currencies': 'eur,usd' }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['bitcoin']['eur'], data['bitcoin']['usd']
        except requests.RequestException as e:
            print(f"Error fetching Bitcoin price: {e}. Using dummy data.")
            return 30000.00, 32000.00
    def fetch_top_gainers_losers(self):
        try:
            url = f"{self.base_url}/coins/markets"
            params = { 'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1, 'sparkline': False, 'price_change_percentage': '24h' }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            valid_coins = [coin for coin in data if coin.get('price_change_percentage_24h') is not None]
            sorted_by_change = sorted(valid_coins, key=lambda x: x['price_change_percentage_24h'])
            top_losers = sorted_by_change[:10]
            top_gainers = sorted_by_change[-10:][::-1]
            return top_gainers, top_losers
        except requests.RequestException as e:
            print(f"Error fetching crypto data: {e}. Using dummy data.")
            return [{'name': 'DummyCoinA', 'symbol': 'DCA', 'price_change_percentage_24h': 10.5}, {'name': 'DummyCoinB', 'symbol': 'DCB', 'price_change_percentage_24h': 8.2}], [{'name': 'DummyCoinX', 'symbol': 'DCX', 'price_change_percentage_24h': -7.1}, {'name': 'DummyCoinY', 'symbol': 'DCY', 'price_change_percentage_24h': -9.8}]

# --- CryptoFearGreedIndex Class (No changes needed) ---
class CryptoFearGreedIndex:
    def __init__(self, master):
        self.master = master
        self.base_url = "https://api.alternative.me/fng/"
        self.data = None
        self.crypto_data = CryptoData()
        self.arrow = None
        self.current_value = 0
        self.animation_running = False

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        self.fig, self.ax = plt.subplots(figsize=(14, 8), subplot_kw=dict(projection='polar'))
        self.canvas_agg = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas_agg.get_tk_widget()
        #self.toolbar = NavigationToolbar2Tk(self.canvas_agg, self.master)
        #self.toolbar.update()
        self.toolbar= None

    def fetch_data(self, limit=30):
        try:
            url = f"{self.base_url}?limit={limit}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.data = response.json()['data']
            return True
        except requests.RequestException as e:
            print(f"Error fetching FGI data: {e}. Using dummy data.")
            self.data = [{'value': '50', 'value_classification': 'Neutral', 'timestamp': str(int(time.time()))}, {'value': '48', 'value_classification': 'Fear', 'timestamp': str(int(time.time() - 86400))}]
            return False

    def get_specific_values(self):
        if not self.data: return None
        values = {'current': None, 'yesterday': None, 'last_week': None, 'last_month': None, 'last_year': None}
        if self.data:
            values['current'] = { 'value': int(self.data[0]['value']), 'classification': self.data[0]['value_classification'], 'timestamp': self.data[0]['timestamp'] }
            if len(self.data) > 1: values['yesterday'] = { 'value': int(self.data[1]['value']), 'classification': self.data[1]['value_classification'], 'timestamp': self.data[1]['timestamp'] }
            if len(self.data) >= 8: values['last_week'] = { 'value': int(self.data[7]['value']), 'classification': self.data[7]['value_classification'], 'timestamp': self.data[7]['timestamp'] }
            if len(self.data) >= 30: values['last_month'] = { 'value': int(self.data[29]['value']), 'classification': self.data[29]['value_classification'], 'timestamp': self.data[29]['timestamp'] }
            if len(self.data) >= 365: values['last_year'] = { 'value': int(self.data[364]['value']), 'classification': self.data[364]['value_classification'], 'timestamp': self.data[364]['timestamp'] }
            elif len(self.data) > 300: values['last_year'] = { 'value': int(self.data[-1]['value']), 'classification': self.data[-1]['value_classification'], 'timestamp': self.data[-1]['timestamp'] }
        return values

    def get_smooth_color_for_value(self, value):
        value = max(0, min(100, value))
        color_points = [(0, (139, 0, 0)), (10, (165, 42, 42)), (20, (178, 34, 34)), (25, (205, 92, 92)), (35, (255, 69, 0)), (45, (255, 140, 0)), (50, (255, 215, 0)), (55, (255, 255, 0)), (65, (173, 255, 47)), (75, (50, 205, 50)), (85, (34, 139, 34)), (95, (0, 100, 0)), (100, (0, 64, 0)) ]
        for i in range(len(color_points) - 1):
            val1, color1 = color_points[i]; val2, color2 = color_points[i + 1]
            if val1 <= value <= val2:
                t = (value - val1) / (val2 - val1) if val2 != val1 else 0
                r = int(color1[0] + t * (color2[0] - color1[0])); g = int(color1[1] + t * (color2[1] - color1[1])); b = int(color1[2] + t * (color2[2] - color1[2]))
                return f'#{r:02x}{g:02x}{b:02x}'
        return '#000000'

    def get_color_for_value(self, value): return self.get_smooth_color_for_value(value)

    def add_crypto_lists(self, fig, top_gainers, top_losers):
        gainers_ax = fig.add_axes([0.02, 0.35, 0.25, 0.5]); gainers_ax.axis('off'); gainers_ax.text(0.5, 0.95, 'TOP 10 GAINERS', ha='center', va='top', fontsize=12, fontweight='bold', color='green', transform=gainers_ax.transAxes)
        for i, coin in enumerate(top_gainers):
            y_pos = 0.85 - (i * 0.08); name = coin['name'][:12] + '...' if len(coin['name']) > 12 else coin['name']; change = coin['price_change_percentage_24h']
            gainers_ax.text(0.05, y_pos, f"{i+1}.", ha='left', va='center', fontsize=9, fontweight='bold', transform=gainers_ax.transAxes); gainers_ax.text(0.15, y_pos, name, ha='left', va='center', fontsize=9, transform=gainers_ax.transAxes); gainers_ax.text(0.95, y_pos, f"+{change:.1f}%", ha='right', va='center', fontsize=9, fontweight='bold', color='green', transform=gainers_ax.transAxes)
        losers_ax = fig.add_axes([0.73, 0.35, 0.25, 0.5]); losers_ax.axis('off'); losers_ax.text(0.5, 0.95, 'TOP 10 LOSERS', ha='center', va='top', fontsize=12, fontweight='bold', color='red', transform=losers_ax.transAxes)
        for i, coin in enumerate(top_losers):
            y_pos = 0.85 - (i * 0.08); name = coin['name'][:12] + '...' if len(coin['name']) > 12 else coin['name']; change = coin['price_change_percentage_24h']
            losers_ax.text(0.05, y_pos, f"{i+1}.", ha='left', va='center', fontsize=9, fontweight='bold', transform=losers_ax.transAxes); losers_ax.text(0.15, y_pos, name, ha='left', va='center', fontsize=9, transform=losers_ax.transAxes); losers_ax.text(0.95, y_pos, f"{change:.1f}%", ha='right', va='center', fontsize=9, fontweight='bold', color='red', transform=losers_ax.transAxes)

    def create_smooth_gradient_gauge(self, ax):
        from matplotlib.colors import LinearSegmentedColormap
        n_colors = 256; color_list = []
        for i in range(n_colors):
            value = i / (n_colors - 1) * 100; hex_color = self.get_smooth_color_for_value(value)
            rgb = tuple(int(hex_color[j:j+2], 16)/255.0 for j in (1, 3, 5)); color_list.append(rgb)
        custom_cmap = LinearSegmentedColormap.from_list('fear_greed', color_list, N=n_colors)
        theta = np.linspace(0, np.pi, 1000); theta_mesh, r_mesh = np.meshgrid(theta, np.linspace(0, 1, 100))
        color_values = np.zeros_like(theta_mesh)
        for i, t in enumerate(theta): color_values[:, i] = (np.pi - t) / np.pi * 100
        mesh = ax.pcolormesh(theta_mesh, r_mesh, color_values, cmap=custom_cmap, shading='gouraud', alpha=0.9)
        return mesh

    def animate_arrow(self, frame):
        if self.arrow is not None: self.arrow.remove()
        current_animated_value = (frame / 50.0) * self.current_value
        current_angle = (100 - current_animated_value) / 100 * np.pi
        self.arrow = self.ax.arrow(current_angle, 0, 0, 0.8, head_width=0.1, head_length=0.1, fc='black', ec='black', linewidth=2)
        return [self.arrow]

    def create_live_gauge_plot(self):
        self.update_gauge_data()
        self.timer = self.fig.canvas.new_timer(interval=300000) # 5 minutes otherwise coingecko complains
        self.timer.add_callback(self.update_gauge_data)
        self.timer.start()
        return self.canvas_widget

    def update_gauge_data(self):
        print(f"Updating FGI data at {datetime.now().strftime('%H:%M:%S')}...")
        self.fig.clear(); self.ax = self.fig.add_subplot(111, projection='polar')
        self.fetch_data(limit=400)
        values = self.get_specific_values()
        if not values or not values['current']:
            print("No current FGI data available to display. Retrying fetch in 5 seconds.")
            self.master.after(5000, self.update_gauge_data)
            return

        self.current_value = values['current']['value']; current_classification = values['current']['classification']
        print("Fetching crypto gainers and losers..."); top_gainers, top_losers = self.crypto_data.fetch_top_gainers_losers()
        print("Fetching Bitcoin price..."); btc_eur, btc_usd = self.crypto_data.fetch_bitcoin_price()
        self.create_smooth_gradient_gauge(self.ax)
        self.ax.set_ylim(0, 1); self.ax.set_xlim(0, np.pi); self.ax.set_yticks([])
        self.ax.set_xticks([0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi])
        self.ax.set_xticklabels(['100\nExtreme\nGreed', '75\nGreed', '50\nNeutral', '25\nFear', '0\nExtreme\nFear'])
        title = f"Current Crypto Fear & Greed Index: {self.current_value} ({current_classification})"; self.ax.set_title(title, pad=20, fontsize=14, fontweight='bold')
        if btc_eur and btc_usd: self.fig.text(0.5, 0.87, f"Bitcoin price: €{btc_eur:,.2f} / ${btc_usd:,.2f}", ha='center', fontsize=12, fontweight='bold', color='#FF9500')
        self.fig.text(0.5, 0.84, f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ha='center', fontsize=12)
        self.ax.grid(False); self.ax.set_rgrids([])
        self.add_gauge_circles(self.fig, values)
        if top_gainers and top_losers: self.add_crypto_lists(self.fig, top_gainers, top_losers)
        else: print("Could not fetch crypto data for lists - displaying gauge only")
        self.arrow = None; frames = 51
        self.arrow_anim = animation.FuncAnimation(self.fig, self.animate_arrow, frames=frames, interval=20, blit=True, repeat=False)
        self.fig.canvas.draw(); self.fig.canvas.flush_events()
        print(f"FGI updated successfully! Next update in 5 minutes seconds...")

    def add_gauge_circles(self, fig, values):
        circle_ax = fig.add_axes([0.28, 0.02, 0.44, 0.3]); circle_ax.set_xlim(0, 14); circle_ax.set_ylim(0, 4); circle_ax.axis('off'); circle_ax.set_aspect('equal')
        positions = [3, 5, 7, 9, 11]; labels = ['Now', 'Yesterday', 'Last Week', 'Last Month', 'Last Year']; periods = ['current', 'yesterday', 'last_week', 'last_month', 'last_year']
        for i, (period, label, x_pos) in enumerate(zip(periods, labels, positions)):
            if values[period]:
                value = values[period]['value']; color = self.get_color_for_value(value)
                # The next line will generatie an user Warning
                # to be solved by facecolor=color or loosing the edgecolor
                #circle = plt.Circle((x_pos, 2.8), 0.32, color=color, alpha=0.9, edgecolor='black', linewidth=2); circle_ax.add_patch(circle)
                circle = plt.Circle((x_pos, 2.8), 0.32, color=color, alpha=0.9,  linewidth=2); circle_ax.add_patch(circle)
                circle_ax.text(x_pos, 2.8, str(value), ha='center', va='center', fontweight='bold', fontsize=10, color='black')
                circle_ax.text(x_pos, 1.8, label, ha='center', va='center', fontsize=8, fontweight='bold', color='black')

    def display_summary(self, values):
        print("="*60); print("CRYPTO FEAR & GREED INDEX SUMMARY"); print("="*60)
        for period, data in values.items():
            if data:
                date = datetime.fromtimestamp(int(data['timestamp'])).strftime('%Y-%m-%d')
                print(f"{period.replace('_', ' ').title():12}: {data['value']:3} ({data['classification']}) - {date}")
        print("="*60); print("\nLegend:")
        print("0-25   : Extreme Fear"); print("25-45  : Fear"); print("45-55  : Neutral")
        print("55-75  : Greed"); print("75-100 : Extreme Greed")


def main():

    root = tk.Tk()
    root.title("Crypto Fear & Greed Index Tracker V1.5")
    icon_path = os.path.join(os.getcwd(), "crypto", f"fng.ico")
    root.iconbitmap(icon_path)  # Your .ico file path here

    initial_width = 1400
    initial_height = 800
    root.geometry(f"{initial_width}x{initial_height}")

    # --- Use grid for the root window layout ---
    root.grid_rowconfigure(0, weight=1)  # Row 0 (for main content) expands vertically
    root.grid_rowconfigure(1, weight=0)  # Row 1 (for ticker) has fixed height
    root.grid_columnconfigure(0, weight=1) # Column 0 expands horizontally

    # 1. Create a frame for the main content (Fear & Greed Index plot and other widgets)
    main_content_frame = tk.Frame(root, bg="lightcyan")
    # Use grid instead of pack
    main_content_frame.grid(row=0, column=0, sticky="nsew") # Fills its grid cell

    # 2. Instantiate CryptoFearGreedIndex
    fng_app = CryptoFearGreedIndex(master=main_content_frame)

    # Get the Tkinter widget for the matplotlib figure and pack it within main_content_frame
    fng_canvas_widget = fng_app.create_live_gauge_plot()
    fng_canvas_widget.pack(side="top", fill="both", expand=True) # Matplotlib canvas still uses pack within its frame

    # If you want the matplotlib toolbar:
    #fng_app.toolbar.pack(side="top", fill="x", expand=False) # Toolbar still uses pack within its frame

    # 3. Create a frame specifically for the CryptoTicker
    ticker_container_frame = tk.Frame(root, height=80, bg="white")
    # Use grid instead of pack
    ticker_container_frame.grid(row=1, column=0, sticky="ew") # Fills horizontally

    # Force geometry calculation for ticker_container_frame immediately after grid-ing
    root.update_idletasks() # Update everything
    ticker_container_frame.update_idletasks() # Update specifically the ticker frame

    # Print its width immediately after forcing update
    print(f"DEBUG: Ticker container frame width after initial grid-ing and update_idletasks: {ticker_container_frame.winfo_width()}")


    # 4. Instantiate the CryptoTicker class
    crypto_ticker = CryptoTicker(
        master=ticker_container_frame,
        # Pass the *actual* width of the container frame which should now be correct
        width=ticker_container_frame.winfo_width(), # It should now be the full root width
        height=60,
        bg_color="white",
        font_name="Verdana",
        font_size=10,
        scroll_speed=-2,
        gap_between_lines=150,
        refresh_interval_ms=60000,
        icon_base_path=os.path.join(os.path.dirname(__file__), "crypto", "ico", "32")
    )

    # --- Keep the robust ticker start logic ---
    def start_ticker_when_ready():
        root.update_idletasks() # Ensure all pending layout updates are processed
        current_root_width = root.winfo_width()
        current_ticker_frame_width = ticker_container_frame.winfo_width()

        print(f"Checking ticker readiness: Root width={current_root_width}, Ticker Frame width={current_ticker_frame_width}")

        if current_root_width > 100 and current_ticker_frame_width > 100:
            print("Ticker container is ready. Starting CryptoTicker.")
            crypto_ticker.start() # Now it's safe to call start()
        else:
            print("Ticker container not ready (still tiny). Retrying in 100ms...")
            root.after(100, start_ticker_when_ready)
    # --- END NEW LOGIC ---

    # Call the new function to initiate the conditional start
    root.after(200, start_ticker_when_ready)

    # Initial data summary print to console (optional)
    initial_values = fng_app.get_specific_values()
    if initial_values:
        fng_app.display_summary(initial_values)

    def on_closing():
        if hasattr(fng_app, 'timer') and fng_app.timer:
            fng_app.timer.stop()
            is_tracker_active=True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()
