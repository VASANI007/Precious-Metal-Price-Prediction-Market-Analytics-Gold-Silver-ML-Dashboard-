import pandas as pd
import yfinance as yf
import os


# FILE PATHS
GOLD_FILE = "data/raw/gold_raw.csv"
SILVER_FILE = "data/raw/silver_raw.csv"
OUTPUT_FILE = "data/processed/final_data.csv"


# CONSTANTS

OUNCE_TO_GRAM = 31.1035


def load_data():
    gold = pd.read_csv(GOLD_FILE)
    silver = pd.read_csv(SILVER_FILE)
    return gold, silver


def fetch_usd_inr():
    print("Fetching USD/INR data...")

    usd_inr = yf.download("USDINR=X", start="2015-01-01")

    if isinstance(usd_inr.columns, pd.MultiIndex):
        usd_inr.columns = usd_inr.columns.get_level_values(0)

    usd_inr.reset_index(inplace=True)
    usd_inr = usd_inr[['Date', 'Close']]
    usd_inr.rename(columns={'Close': 'USD_INR'}, inplace=True)

    return usd_inr


def preprocess():
    gold, silver = load_data()

    
    # Date conversion
    gold['Date'] = pd.to_datetime(gold['Date'])
    silver['Date'] = pd.to_datetime(silver['Date'])

    
    # Select columns
    gold = gold[['Date', 'Close']]
    silver = silver[['Date', 'Close']]

    
    # Rename columns
    gold.rename(columns={'Close': 'Gold_USD'}, inplace=True)
    silver.rename(columns={'Close': 'Silver_USD'}, inplace=True)

    
    # Merge Gold + Silver
    df = pd.merge(gold, silver, on='Date', how='inner')

    # Convert to numeric (IMPORTANT FIX)
    df['Gold_USD'] = pd.to_numeric(df['Gold_USD'], errors='coerce')
    df['Silver_USD'] = pd.to_numeric(df['Silver_USD'], errors='coerce')

    
    # Fetch USD-INR
    usd_inr = fetch_usd_inr()
    usd_inr['Date'] = pd.to_datetime(usd_inr['Date'])

    # Merge Forex Data
    df = pd.merge(df, usd_inr, on='Date', how='left')

    # fill missing forex values
    df['USD_INR'].fillna(method='ffill', inplace=True)

    
    # USD → INR per gram (DYNAMIC)
    df['Gold_24K_1g'] = (df['Gold_USD'] / OUNCE_TO_GRAM) * df['USD_INR']
    df['Silver_1g'] = (df['Silver_USD'] / OUNCE_TO_GRAM) * df['USD_INR']

    
    # Gold 22K
    df['Gold_22K_1g'] = df['Gold_24K_1g'] * (22 / 24)

    
    # Weight Multipliers
    weights = {
        "1g": 1,
        "10g": 10,
        "100g": 100,
        "1kg": 1000
    }

    metals = ["Gold_24K", "Gold_22K", "Silver"]
    for metal in metals:
        base_col = f"{metal}_1g"

        for w_name, w_value in weights.items():
            df[f"{metal}_{w_name}"] = df[base_col] * w_value

    
    # Clean Data
    df = df.sort_values(by='Date')
    df.reset_index(drop=True, inplace=True)

    # remove unwanted columns
    df.drop(columns=['Gold_USD', 'Silver_USD'], inplace=True)

    
    # Save
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n Final data saved → {OUTPUT_FILE}")

    return df


if __name__ == "__main__":
    print(" Processing Data with Dynamic INR...\n")
    df = preprocess()
    print("\nAll Done!")