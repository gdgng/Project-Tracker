import openpyxl
import requests
import time
import json
import hmac
import hashlib
import logging
import sys
import os
import csv
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from collections import defaultdict
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment


# Load warm storage credentials from tracker.xlsx
try:
    ws = openpyxl.load_workbook('tracker.xlsx')['Credentials']
    Warm_API_Name = ws.cell(row=2,column=2).value
    WARM_API_KEY = ws.cell(row=3, column=2).value
    WARM_API_SECRET = ws.cell(row=4, column=2).value
    WARM_API_URL = ws.cell(row=5, column=2).value
except (FileNotFoundError, KeyError, Exception) as e:
    print(f"Error opening 'tracker.xlsx': {e}")
    sys.exit()


# Warm Storage API Functions
def create_signature(ts, method, endp, body=None):
    """
    Create the HMAC SHA256 signature for authentication with the Bitvavo API.
    """
    msg = str(ts) + method + '/v2/' + endp
    if body:
        msg += json.dumps(body)
    return hmac.new(WARM_API_SECRET.encode('utf-8'), msg.encode(), hashlib.sha256).hexdigest()

def warm_exchange_req(method, endpoint, params=None):
    """
    Perform an API request to Bitvavo using the given method and endpoint.
    """
    ts = int(time.time() * 1000)  # Current timestamp in milliseconds
    headers = {f'{Warm_API_Name}-Access-Key': WARM_API_KEY,
               f'{Warm_API_Name}-Access-Timestamp': str(ts),
               f'{Warm_API_Name}-Access-Signature': create_signature(ts, method, endpoint, params)}

    try:
        resp = requests.request(method, WARM_API_URL + endpoint, headers=headers, params=params)
        resp.raise_for_status()  # Raise an exception for HTTP errors
        return resp.json()  # Return the response data in JSON format
    except requests.exceptions.RequestException as e:
        logging.error(f"Warm Storage Access API error ({endpoint}): {e}")
        return None

def get_warm_exchange_ticker(market):
    """
    Fetch the ticker price for a specific market (e.g., 'BTC-EUR') from the warm exchange.
    """
    return warm_exchange_req('GET', f"ticker/price?market={market}")

def get_warm_exchange_balance():
    """
    Fetch the balance for all available coins in warm storage.
    """
    data = warm_exchange_req('GET', "balance")
    if data:
        return {item['symbol']: {'available': float(item['available']), 'in_order': float(item['inOrder'])} for item in data}
    return None

def get_crypto_ticker(crypto):
    """
    Get the price of a cryptocurrency in EUR. Returns 1.0 for EUR itself.
    """
    if crypto == "EUR":
        return {'eur_rate': 1.0, 'updated': int(time.time())}

    data = get_warm_exchange_ticker(f"{crypto}-EUR")
    if data and 'price' in data:
        return {'eur_rate': float(data['price']), 'updated': int(time.time())}

    logging.error(f"Error: Price not found for {crypto}")
    return None

def read_cold_storage_xlsx(file_path='tracker.xlsx'):
    try:
        df = pd.read_excel(file_path, sheet_name='Cold_Storage', header=1)
        return dict(zip(df['Coin'].str.upper(), df['Amount']))
    except Exception as e:
        print(f"Error reading cold storage from '{file_path}': {e}")
        return {}



def calculate_buy_stake_sell_data(csv_filepath, real_time_prices):
    avg_price = 0
    data_per_coin = defaultdict(lambda: {
        'bought_amount': 0,
        'bought_cost': 0,
        'staked_amount': 0,
        'sold_amount': 0,
        'deposited_amount': 0,
        'total_invested': 0  # New field to track investment per coin
    })
    eur_in = 0.0
    eur_out = 0.0
    all_rows = []

    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_rows.append(row)
                tx_type = row.get('Type', '').lower()
                currency = row.get('Currency', '').upper()
                amount_str = row.get('Amount')
                quote_currency = row.get('Quote Currency', '').upper()
                quote_price_str = row.get('Quote Price')
                received_paid_currency = row.get('Received / Paid Currency', '').upper()
                received_paid_amount_str = row.get('Received / Paid Amount')
                fee_currency = row.get('Fee currency', '').upper()
                fee_amount_str = row.get('Fee amount')

                try:
                    amount = float(amount_str)
                except (ValueError, TypeError):
                    continue

                if currency not in real_time_prices:  # Use real_time_prices keys
                    continue

                try:
                    fee_amount = float(fee_amount_str) if fee_amount_str else 0.0
                except (ValueError, TypeError):
                    fee_amount = 0.0

                if tx_type == 'buy' and quote_currency == 'EUR':
                    try:
                        price = float(quote_price_str)
                        cost = amount * price
                        data_per_coin[currency]['bought_amount'] += amount
                        data_per_coin[currency]['bought_cost'] += cost
                        data_per_coin[currency]['total_invested'] += cost + (fee_amount if fee_currency == 'EUR' else 0.0)
                    except (ValueError, TypeError):
                        pass
                elif tx_type == 'staking':
                    data_per_coin[currency]['staked_amount'] += amount
                elif tx_type == 'sell':
                    data_per_coin[currency]['sold_amount'] += abs(amount)
                elif tx_type == 'deposit' and currency != 'EUR':
                    data_per_coin[currency]['deposited_amount'] += amount
                elif currency == 'EUR' and tx_type == 'deposit':
                    eur_in += amount
                elif currency == 'EUR' and tx_type == 'withdrawal':
                    eur_out += abs(amount)

        result = {}
        for coin, data in sorted(data_per_coin.items()):
            bought = data['bought_amount']
            staked = data['staked_amount']
            sold = data['sold_amount']
            deposited = data.get('deposited_amount', 0.0)
            total_invested = data.get('total_invested', 0.0)

            current = (bought + staked + deposited) - sold
            avg_price = round(data['bought_cost'] / bought, 2) if bought > 0 else 0.0

            value_now = current * real_time_prices.get(coin, 0)
            profit_loss = round(value_now - total_invested, 2)

            result[coin] = {
                'bought': round(bought, 8),
                'staked': round(staked, 8),
                'sold': round(sold, 8),
                'current': round(current, 8),
                'avg_price': avg_price,
                'invest': round(total_invested, 2),  # Investment per coin
                'profit_loss': profit_loss
            }

        return result, round(eur_in, 2), round(eur_out, 2), all_rows

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {}, 0.0, 0.0, []



def flatten_cols(cols):
    """Flattens multi-level column headers into a single tuple of strings."""
    new_cols = []
    for col in cols:
        if isinstance(col, tuple):
            new_cols.append(' '.join(str(c) for c in col if c))
        else:
            new_cols.append(str(col))
    return new_cols



def create_excel_with_pivots(filename, all_data, relevant_coins):
    try:
        if os.path.exists(filename):
            book = openpyxl.load_workbook(filename)
            sheets_to_delete = ['Raw Data', 'Pivot Table Summary', 'Pivot Table Detailed']
            for sheet_name in sheets_to_delete:
                if sheet_name in book.sheetnames:
                    del book[sheet_name]
        else:
            book = openpyxl.Workbook()

        # Write Raw Data
        df_raw = pd.DataFrame(all_data)
        ws_raw = book.create_sheet('Raw Data')
        ws_raw.append(list(df_raw.columns))
        for row in pd.DataFrame.to_numpy(df_raw):
            ws_raw.append(list(row))

        if not df_raw.empty:
            # Convert numeric columns properly
            for col in ['Amount', 'Quote Price', 'Fee amount', 'Received / Paid Amount']:
                df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

            # Normalize coin names to uppercase
            df_raw['Currency'] = df_raw['Currency'].str.upper()

            # Filter for relevant coins and EUR
            df_filtered = df_raw[df_raw['Currency'].isin(relevant_coins) | (df_raw['Currency'] == 'EUR')]

            if not df_filtered.empty:
                # Create Summary Pivot Table
                pivot_summary = pd.pivot_table(
                    df_filtered,
                    values=['Amount', 'Quote Price', 'Fee amount', 'Received / Paid Amount'],
                    index='Currency',
                    columns='Type',
                    aggfunc='sum',
                    margins=True,
                    margins_name='Total'
                )
                ws_summary = book.create_sheet('Pivot Table Summary')

                # Write the first level of headers
                first_level_summary_headers = [pivot_summary.index.name] + list(pivot_summary.columns.levels[0])
                ws_summary.append(first_level_summary_headers)

                flat_cols_summary = [pivot_summary.index.name] + flatten_cols(pivot_summary.columns)
                ws_summary.append(flat_cols_summary)

                # Merge and center the first-level headers for Summary
                header_row_summary_level_two = ws_summary[2]
                start_col_summary = 2
                for main_header in ['Amount', 'Quote Price', 'Fee amount', 'Received / Paid Amount']:
                    start_merge = -1
                    end_merge = -1
                    for i, cell in enumerate(header_row_summary_level_two[1:], start=2):
                        if cell.value and cell.value.startswith(main_header):
                            if start_merge == -1:
                                start_merge = i
                            end_merge = i
                        elif start_merge != -1 and not cell.value.startswith(main_header):
                            break

                    if start_merge != -1 and end_merge != -1:
                        start_letter = get_column_letter(start_merge)
                        end_letter = get_column_letter(end_merge)
                        ws_summary.merge_cells(f'{start_letter}1:{end_letter}1')
                        ws_summary[f'{start_letter}1'].alignment = Alignment(horizontal='center')

                # Write data rows
                for index, row in pivot_summary.iterrows():
                    ws_summary.append([index] + list(row))

                # Create Detailed Pivot Table
                pivot_detailed = pd.pivot_table(
                    df_filtered,
                    values=['Amount', 'Quote Price', 'Fee amount', 'Received / Paid Amount'],
                    index=['Timezone', 'Date', 'Time', 'Type', 'Currency'],
                    columns=['Quote Currency', 'Received / Paid Currency', 'Fee currency'],
                    aggfunc='sum',
                    fill_value=0
                )
                ws_detailed = book.create_sheet('Pivot Table Detailed')
                index_names = list(pivot_detailed.index.names)

                # Write the first level of headers for detailed table
                first_level_detailed_headers = index_names + list(pivot_detailed.columns.levels[0])
                ws_detailed.append(first_level_detailed_headers)

                flat_cols_detailed = index_names + flatten_cols(pivot_detailed.columns)
                ws_detailed.append(flat_cols_detailed)

                # Merge and center the first-level headers for Detailed
                header_row_detailed_level_two = ws_detailed[2]
                start_col_detailed = len(index_names) + 1
                for main_header in ['Amount', 'Quote Price', 'Fee amount', 'Received / Paid Amount']:
                    start_merge_detailed = -1
                    end_merge_detailed = -1
                    for i, cell in enumerate(header_row_detailed_level_two[len(index_names):], start=len(index_names) + 1):
                        if cell.value and cell.value.startswith(main_header):
                            if start_merge_detailed == -1:
                                start_merge_detailed = i
                            end_merge_detailed = i
                        elif start_merge_detailed != -1 and not cell.value.startswith(main_header):
                            break

                    if start_merge_detailed != -1 and end_merge_detailed != -1:
                        start_letter_detailed = get_column_letter(start_merge_detailed)
                        end_letter_detailed = get_column_letter(end_merge_detailed)
                        ws_detailed.merge_cells(f'{start_letter_detailed}1:{end_letter_detailed}1')
                        ws_detailed[f'{start_letter_detailed}1'].alignment = Alignment(horizontal='center')

                # Write data rows for detailed table
                for index, row in pivot_detailed.iterrows():
                    ws_detailed.append(list(index) + list(row))

        try:
            book.save(filename)
            print(f"Excel file '{filename}' updated successfully.")
        except PermissionError:
            messagebox.showerror("Permission Error", f"Could not save '{filename}'. The file might be open in another application.")

    except Exception as e:
        print(f"Error updating Excel file with pivot tables: {e}")

def browse_file():
    filepath = filedialog.askopenfilename(
        title="Select Bitvavo CSV file",
        filetypes=[("CSV files", "*.csv")],
        initialdir=os.getcwd()
    )
    if filepath:
        # Reading cold storage coins from the tracker.xlsx
        cold_storage_data = read_cold_storage_xlsx()

        # Reading warm storage coins
        warm_storage_data = get_warm_exchange_balance()

        # Combine cold and warm storage coins into a list of relevant coins
        relevant_coins = list(set(cold_storage_data.keys()).union(set(warm_storage_data.keys())))

        # Fetch real-time prices for relevant coins
        real_time_prices = {}
        for coin in relevant_coins:
            if coin == 'EUR':
                real_time_prices[coin] = 1.0
            else:
                ticker_data = get_warm_exchange_ticker(f"{coin}-EUR")
                if ticker_data and 'price' in ticker_data:
                    real_time_prices[coin] = float(ticker_data['price'])
                else:
                    real_time_prices[coin] = 0  # Default to 0 if price not found
                    print(f"Warning: Could not fetch price for {coin}. Setting price to 0.")

        results, eur_in_total, eur_out_total, all_csv_data = calculate_buy_stake_sell_data(filepath, real_time_prices)
        total_invest_overall = round(eur_in_total - eur_out_total, 2) # Keep track of overall investment

        for row in treeview.get_children():
            treeview.delete(row)

        if results:
            for coin, data in results.items():
                if data['current'] >= 0.00000001 and coin in relevant_coins:
                    treeview.insert('', 'end', values=(
                        coin,
                        data['bought'],
                        data['staked'],
                        data['sold'],
                        data['current'],
                        data['avg_price'],
                        data['invest'],  # Use the per-coin investment
                        data['profit_loss']
                    ))
            print("In -->",eur_in_total)
            eur_in_label.config(text=f"Total EUR In: € {eur_in_total}")
            eur_out_label.config(text=f"Total EUR Out: € {eur_out_total}")
            total_invest_label.config(text=f"Total Invest: € {total_invest_overall}") # Display overall investment
            finished_button.config(state=tk.NORMAL) # Enable the button after processing
        else:
            treeview.insert('', 'end', values=("No relevant transactions found.",))
            eur_in_label.config(text="Total EUR In: € 0.00")
            eur_out_label.config(text="Total EUR Out: € 0.00")
            total_invest_label.config(text="Total Invest: € 0.00")
            finished_button.config(state=tk.DISABLED) # Disable if no data

        create_excel_with_pivots("tracker.xlsx", all_csv_data, relevant_coins)

def exit_program():
    root.destroy()


# GUI setup
root = tk.Tk()
root.title("Bitvavo CSV Analyzer")
root.geometry("1100x650") # Increased height to accommodate the button
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

tk.Label(root, text="Select Bitvavo CSV File", font=("Helvetica", 14)).pack(pady=10)
tk.Button(root, text="Browse...", command=browse_file, width=20).pack(pady=5)

columns = ('Coin', 'Bought', 'Staked', 'Sold', 'Current', 'Avg €', 'Invest €', 'Profit/Loss €')
treeview = ttk.Treeview(root, columns=columns, show='headings')

for col in columns:
    treeview.heading(col, text=col)
    treeview.column(col, minwidth=100, width=150, stretch=True)

treeview.pack(padx=10, pady=10, fill="both", expand=True)

scrollbar_y = tk.Scrollbar(root, orient="vertical", command=treeview.yview)
scrollbar_y.pack(side="right", fill="y")
treeview.configure(yscrollcommand=scrollbar_y.set)

scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=treeview.xview)
scrollbar_x.pack(side="bottom", fill="x")
treeview.configure(xscrollcommand=scrollbar_x.set)

totals_frame = tk.Frame(root)
totals_frame.pack(pady=10)

eur_in_label = tk.Label(totals_frame, text="Total EUR In: € 0.00", font=("Helvetica", 12))
eur_in_label.pack(side="left", padx=10)

eur_out_label = tk.Label(totals_frame, text="Total EUR Out: € 0.00", font=("Helvetica", 12))
eur_out_label.pack(side="left", padx=10)

total_invest_label = tk.Label(totals_frame, text="Total Invest: € 0.00", font=("Helvetica", 12))
total_invest_label.pack(side="left", padx=10)

finished_button = tk.Button(root, text="Finished", command=exit_program, bg="lightgray", fg="forestgreen", font=("Helvetica", 12), state=tk.DISABLED)
finished_button.pack(pady=0, padx=10, anchor="e") # Anchor to the right

root.mainloop()
