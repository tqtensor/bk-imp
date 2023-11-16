import os
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, status
from xgboost import XGBClassifier

router = APIRouter()


@router.post(
    path="/inferences",
    status_code=status.HTTP_200_OK,
)
async def run(dataset: str):
    """
    Runs the inference model to determine the churn probability of each
    customer.

    :param str dataset: The path to the dataset to run the inference model on.

    :return: A pandas DataFrame containing the dataset with an additional
    column "Churn Probability" which represents the churn probability for each
    customer, and the XGBClassifier model used to make the predictions.
    """
    # Load dataset
    if dataset == "test":
        dataset = pd.read_csv("./jobs/data/test.csv")
    elif dataset == "validation":
        dataset = pd.read_csv("./jobs/data/validation.csv")
    else:
        raise ValueError(
            f"Dataset {dataset} not found. Must be 'test' or 'validation'."
        )

    # Load model
    model = XGBClassifier()
    model.load_model("./jobs/model/xgb_model.json")

    # Predict churn probability
    dataset["Churn Probability"] = model.predict_proba(
        dataset.drop(columns=["Total Customer Spend", "Churn?_True."])
    )[:, 0]

    # Get current UTC time and format it as a string
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    # Include timestamp in filename
    file_path = f"/tmp/predictions_{timestamp}.csv"

    # Save DataFrame to CSV file in tmp folder
    dataset.to_csv(file_path, index=False)

    # Return file path
    return {"file_path": os.path.abspath(file_path)}
