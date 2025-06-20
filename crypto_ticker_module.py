import tkinter as tk
from PIL import Image, ImageTk
import requests
import os
import time

class CryptoTicker:
    def __init__(self, master, width=1000, height=80, bg_color="white",
                 font_name="Segoe UI Symbol", font_size=14, font_weight="bold",
                 scroll_speed=-2, gap_between_lines=100, refresh_interval_ms=60000,
                 icon_base_path="crypto/ico/32", text_color="white"):
        """
        Initializes the CryptoTicker.

        Args:
            master (tk.Tk or tk.Frame): The parent Tkinter widget (root window or a frame).
            width (int): Width of the ticker canvas.
            height (int): Height of the ticker canvas.
            bg_color (str): Background color of the canvas.
            font_name (str): Font family for the ticker text.
            font_size (int): Font size for the ticker text.
            font_weight (str): Font weight for the ticker text (e.g., "bold", "normal").
            scroll_speed (int): Pixels to move per scroll step (negative for leftward).
            gap_between_lines (int): Horizontal space between repeated ticker lines.
            refresh_interval_ms (int): Interval in milliseconds to fetch new data.
            icon_base_path (str): Base path to the cryptocurrency icon directory.
        """
        self.master = master
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.font = (font_name, font_size, font_weight)
        self.scroll_speed = scroll_speed
        self.gap_between_lines = gap_between_lines
        self.refresh_interval_ms = refresh_interval_ms
        self.icon_base_path = icon_base_path
        self.text_color = text_color # This line is correct, assuming 'text_color' param is a string
        self.bg_color = bg_color    # And this too, assuming 'bg_color' param is a string

        # Add a debug print here to see what text_color and bg_color are actually holding
        print(f"DEBUG: CryptoTicker init - text_color='{self.text_color}', bg_color='{self.bg_color}'")

        self.canvas = tk.Canvas(master, width=self.width, height=self.height,
                                bg=self.bg_color, highlightthickness=0) # <-- self.bg_color needs to be a string

        self.canvas = tk.Canvas(master, width=self.width, height=self.height,
                                bg=self.bg_color, highlightthickness=0)
        # The canvas itself will fill its parent frame horizontally
        self.canvas.pack(fill="x", expand=False) # Important: fill="x" for ticker within its frame

        self.images = []  # To keep PhotoImage references
        self.ticker_line_objects = []  # Stores lists of canvas item IDs for each ticker line
        self.data_cache = []  # To store the fetched crypto data
        self.last_data_fetch_time = 0 # Unix timestamp of last data fetch

        # Ensure the canvas is updated to get its correct width (needed if canvas width is derived from master)
        self.master.update_idletasks()
        self._initial_setup_scheduled = False # Flag to ensure initial setup runs once

    def _fetch_data(self):
        """Fetches cryptocurrency data from CoinGecko API."""
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "price_change_percentage": "24h"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            self.data_cache = response.json()
            self.last_data_fetch_time = time.time()
            # print("Data fetched successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        except ValueError as e:
            print(f"Error decoding JSON response: {e}")

    def _get_coin_icon(self, coin_symbol):
        """Loads and returns a PhotoImage for the coin icon."""
        icon_path = os.path.join(self.icon_base_path, f"{coin_symbol.lower()}.png")
        if os.path.exists(icon_path):
            try:
                image = Image.open(icon_path).resize((20, 20))
                return ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading icon for {coin_symbol}: {e}")

        fallback = os.path.join(self.icon_base_path, "generic.png")
        if os.path.exists(fallback):
            image = Image.open(fallback).resize((20, 20))
            return ImageTk.PhotoImage(image)
        return None

    def _create_or_update_ticker_line(self, x_start, data, existing_items=None):
        """
        Creates new canvas items for a ticker line or updates existing ones.
        Returns (list of item IDs, end x-coordinate).
        """
        x = x_start
        current_items = []
        current_image_refs = []

        item_idx = 0
        for coin in data:
            symbol = coin["symbol"].upper()
            change = coin["price_change_percentage_24h"]
            arrow = "▲" if change >= 0 else "▼"
            color = "green" if change >= 0 else "red"
            text_content = f"{symbol} {arrow} {abs(change):.2f}%"

            # Handle icon
            icon = self._get_coin_icon(symbol)
            if icon:
                current_image_refs.append(icon)
                if existing_items and item_idx < len(existing_items) and self.canvas.type(existing_items[item_idx]) == 'image':
                    self.canvas.itemconfig(existing_items[item_idx], image=icon)
                    self.canvas.coords(existing_items[item_idx], x, self.height / 2)
                    icon_id = existing_items[item_idx]
                else:
                    icon_id = self.canvas.create_image(x, self.height / 2, image=icon, anchor="w")
                current_items.append(icon_id)
                item_idx += 1
                x += 28

            # Handle text
            if existing_items and item_idx < len(existing_items) and self.canvas.type(existing_items[item_idx]) == 'text':
                self.canvas.itemconfig(existing_items[item_idx], text=text_content, fill=color)
                self.canvas.coords(existing_items[item_idx], x, self.height / 2)
                text_id = existing_items[item_idx]
            else:
                text_id = self.canvas.create_text(x, self.height / 2, text=text_content, anchor="w", fill=color, font=self.font)
            current_items.append(text_id)
            item_idx += 1

            bbox = self.canvas.bbox(text_id)
            if bbox:
                x += bbox[2] - bbox[0] + 40 # Padding between items

        # If there are more existing_items than new content, delete the extras
        if existing_items:
            for i in range(item_idx, len(existing_items)):
                self.canvas.delete(existing_items[i])

        self.images.extend(current_image_refs)

        return current_items, x

    def _scroll(self):
        """Performs the scrolling animation and recycles lines."""
        if not self.master.winfo_exists():
            return

        for line_data in self.ticker_line_objects:
            for item in line_data["items"]:
                self.canvas.move(item, self.scroll_speed, 0)

        if self.ticker_line_objects and self.canvas.coords(self.ticker_line_objects[0]["items"][-1])[0] < -50:
            recycled_line_data = self.ticker_line_objects.pop(0)

            last_line_end_x = 0
            if self.ticker_line_objects:
                last_item_coords = self.canvas.coords(self.ticker_line_objects[-1]["items"][-1])
                if last_item_coords:
                    bbox = self.canvas.bbox(self.ticker_line_objects[-1]["items"][-1])
                    if bbox:
                        last_line_end_x = bbox[2]
            else:
                last_line_end_x = self.canvas.winfo_width()

            new_start_x = last_line_end_x + self.gap_between_lines

            updated_items, updated_end_x = self._create_or_update_ticker_line(
                new_start_x, self.data_cache, existing_items=recycled_line_data["items"]
            )

            recycled_line_data["items"] = updated_items
            recycled_line_data["end"] = updated_end_x

            self.ticker_line_objects.append(recycled_line_data)

        self.master.after(50, self._scroll)

    def _periodic_data_refresh(self):
        """Schedules and performs periodic data fetching."""
        if not self.master.winfo_exists():
            return

        if time.time() - self.last_data_fetch_time > self.refresh_interval_ms / 1000:
            self._fetch_data()

        self.master.after(self.refresh_interval_ms, self._periodic_data_refresh)

    def start(self):
        """Starts the ticker's scrolling and data refreshing."""
        if not self._initial_setup_scheduled:
            self.master.after(100, self._initial_setup)
            self._initial_setup_scheduled = True

    def _initial_setup(self):
        """Performs initial data fetch and ticker line creation."""
        self._fetch_data()

        if not self.data_cache:
            print("No data fetched. Cannot start ticker without data. Retrying in 5 seconds...")
            self.master.after(5000, self._initial_setup) # Retry after 5 seconds
            return

        x1 = self.canvas.winfo_width()
        line1_items, line1_end = self._create_or_update_ticker_line(x1, self.data_cache)

        x2 = line1_end + self.gap_between_lines
        line2_items, line2_end = self._create_or_update_ticker_line(x2, self.data_cache)

        self.ticker_line_objects.extend([
            {"items": line1_items, "end": line1_end},
            {"items": line2_items, "end": line2_end}
        ])

        self._scroll()
        self._periodic_data_refresh()


# --- Example of how to use the CryptoTicker class in another program ---
if __name__ == "__main__":
    def main_app():
        root = tk.Tk()
        root.title("Main Application with Crypto Ticker at Bottom")
        root.geometry("800x400") # Initial size

        # 1. Create a frame for your main content (everything above the ticker)
        main_content_frame = tk.Frame(root, bg="lightblue")
        # Pack the main content frame to the TOP.
        # It must be packed *before* the ticker frame so it gets the "remaining" space.
        # fill="both" and expand=True allow it to take up all available space.
        main_content_frame.pack(side="top", fill="both", expand=True)

        # Add some content to the main content frame
        tk.Label(main_content_frame, text="Your Main Application Content Here",
                 font=("Helvetica", 24), bg="lightblue").pack(pady=50)
        tk.Label(main_content_frame, text="This area will expand and contract with the window.",
                 font=("Helvetica", 12), bg="lightblue").pack()


        # 2. Create a frame specifically for the CryptoTicker
        # This frame will act as the master for the CryptoTicker's canvas
        ticker_container_frame = tk.Frame(root, height=80, bg="darkgray") # Set a fixed height
        # Pack the ticker container frame to the BOTTOM.
        # Crucially, it's packed *after* the main content frame.
        # fill="x" makes it expand horizontally with the window.
        # expand=False (default) prevents it from taking up vertical space unnecessarily.
        ticker_container_frame.pack(side="bottom", fill="x", expand=False)

        # Create an instance of CryptoTicker, using ticker_container_frame as its master
        crypto_ticker = CryptoTicker(
            master=ticker_container_frame,
            # The width of the canvas should match the container frame's width.
            # We can't use root.winfo_width() directly here because it might not be finalized yet.
            # The canvas's fill="x" will make it match its parent's width automatically.
            width=800, # Initial width, will be overridden by fill="x" in ticker's pack
            height=80,
            bg_color="black",
            font_name="Consolas", # A monospace font often looks good for tickers
            font_size=16,
            font_weight="bold",
            scroll_speed=-2,
            gap_between_lines=120,
            refresh_interval_ms=45000,
            icon_base_path=os.path.join(os.getcwd(), "crypto", "ico", "32")
        )
        print("CryptoTicker started")
        crypto_ticker.start() # Start the ticker

        root.mainloop()

    main_app()
