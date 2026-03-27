import yfinance as yf
import pandas as pd
import os


# FILE PATHS
GOLD_FILE = "data/raw/gold_raw.csv"
SILVER_FILE = "data/raw/silver_raw.csv"


# SYMBOLS
GOLD_SYMBOL = "GC=F"   # Gold
SILVER_SYMBOL = "SI=F" # Silver



# CORE FUNCTION
def fetch_data(symbol, file_path):
    """
    Fetch data from yfinance with incremental update
    """

    os.makedirs("data/raw", exist_ok=True)

    
    # If file exists → update
    if os.path.exists(file_path):
        try:
            old_data = pd.read_csv(file_path)

            # safety check
            if old_data.empty:
                print(f" {file_path} is empty. Re-downloading full data...")
                raise Exception("Empty file")

            last_date = old_data['Date'].iloc[-1]

            print(f"Updating {symbol} from {last_date}...")

            new_data = yf.download(symbol, start=last_date)

            if new_data.empty:
                print("No new data available.")
                return old_data

            new_data.reset_index(inplace=True)

            updated_data = pd.concat([old_data, new_data])
            updated_data.drop_duplicates(subset="Date", inplace=True)

        except Exception as e:
            print(f"Error reading file → Re-downloading full data ({symbol})")

            updated_data = yf.download(symbol, start="2015-01-01")
            updated_data.reset_index(inplace=True)

    
    # If file does not exist
    else:
        print(f"Downloading full data for {symbol}...")

        updated_data = yf.download(symbol, start="2015-01-01")
        updated_data.reset_index(inplace=True)

    
    # Final Safety Check
    if updated_data.empty:
        raise ValueError(f" Failed to fetch data for {symbol}")

    # save file
    updated_data.to_csv(file_path, index=False)
    print(f" Data saved → {file_path}")
    return updated_data



# WRAPPER FUNCTIONS
def fetch_gold_data():
    return fetch_data(GOLD_SYMBOL, GOLD_FILE)

def fetch_silver_data():
    return fetch_data(SILVER_SYMBOL, SILVER_FILE)

def fetch_all():
    print("\nFetching Gold Data...")
    gold = fetch_gold_data()

    print("\nFetching Silver Data...")
    silver = fetch_silver_data()

    return gold, silver


# MAIN RUN
if __name__ == "__main__":
    print(" Starting Data Fetch...\n")
    gold_df, silver_df = fetch_all()
    print("\n Data Fetch Complete!")