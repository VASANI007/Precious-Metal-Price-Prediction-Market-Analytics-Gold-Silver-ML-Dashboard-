from src.data.fetch_data import fetch_all
from src.processing.preprocess import preprocess
from src.models.train_model import train_model
from src.models.predict import predict_next


def run_pipeline():
    print("\n Starting Full Pipeline...\n")

    print(" Fetching Data...")
    fetch_all()

    print("\n Processing Data...")
    preprocess()

    print("\n Training Model...")
    train_model()

    print("\n Predicting...")
    pred = predict_next()

    print(f"\n Next Day Gold Price Prediction: {pred:.2f} INR")

    print("\n Pipeline Completed!")


if __name__ == "__main__":
    run_pipeline()