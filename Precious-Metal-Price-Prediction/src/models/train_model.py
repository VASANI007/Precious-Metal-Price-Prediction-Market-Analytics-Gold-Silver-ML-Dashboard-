import pandas as pd
import numpy as np
import os
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score


# FILE PATHS

DATA_FILE = "data/processed/final_data.csv"
MODEL_FILE = "models/model.pkl"


def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(" Processed data not found. Run preprocess.py first")

    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])

    return df


def prepare_features(df):
    """
    Create features for model training
    """

    df = df[['Date', 'Gold_24K_1g']].dropna()

    # numeric time feature
    df['Day'] = np.arange(len(df))

    # moving average feature
    df['MA_30'] = df['Gold_24K_1g'].rolling(30).mean()

    # fill NA
    df = df.fillna(method='bfill')

    return df


def train_model():
    df = load_data()
    df = prepare_features(df)

    # features (X) and target (y)
    X = df[['Day', 'MA_30']]
    y = df['Gold_24K_1g']

    # split (simple)
    split = int(len(df) * 0.8)

    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # predictions
    y_pred = model.predict(X_test)

    # evaluation
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n Model Performance:")
    print(f"MAE: {mae:.2f}")
    print(f"R2 Score: {r2:.4f}")

    # save model
    os.makedirs("models", exist_ok=True)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)

    print(f"\n Model saved → {MODEL_FILE}")
    return model, df



# RUN
if __name__ == "__main__":
    print("Training Model...\n")
    model, df = train_model()
    print("\nAll Done!")