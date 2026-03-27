import pickle
import pandas as pd
import numpy as np
import os

# FILE PATHS
MODEL_FILE = "models/model.pkl"
DATA_FILE = "data/processed/final_data.csv"

# LOAD MODEL
def load_model():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(" Model not found. Run train_model.py first")

    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)

    return model

# LOAD DATA
def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(" Data not found. Run preprocess.py first")

    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])

    return df

# PREPARE FEATURES
def prepare_features(df):
    df = df[['Date', 'Gold_24K_1g']].dropna()

    df['Day'] = np.arange(len(df))
    df['MA_30'] = df['Gold_24K_1g'].rolling(30).mean()

    df = df.fillna(method='bfill')

    return df

# NEXT DAY PREDICTION
def predict_next():
    model = load_model()
    df = load_data()
    df = prepare_features(df)

    last_day = df['Day'].iloc[-1] + 1
    last_ma = df['MA_30'].iloc[-1]

    X_new = [[last_day, last_ma]]

    prediction = model.predict(X_new)[0]

    return prediction

# FUTURE PREDICTIONS
def predict_future(days=7):
    model = load_model()
    df = load_data()
    df = prepare_features(df)

    predictions = []

    last_day = df['Day'].iloc[-1]
    last_ma = df['MA_30'].iloc[-1]

    for i in range(days):
        next_day = last_day + i + 1

        X_new = [[next_day, last_ma]]
        pred = model.predict(X_new)[0]

        predictions.append(pred)

        # update MA approx (simple simulation)
        last_ma = (last_ma * 29 + pred) / 30

    return predictions

# MAIN RUN
if __name__ == "__main__":
    print("Running Predictions...\n")

    next_price = predict_next()
    print(f"Next Day Prediction: {next_price:.2f} INR")

    future_prices = predict_future(7)
    print("\nNext 7 Days Forecast:")

    for i, price in enumerate(future_prices, start=1):
        print(f"Day {i}: {price:.2f} INR")

    print("\nAll Done!")