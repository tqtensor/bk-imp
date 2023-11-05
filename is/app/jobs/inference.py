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
    dataset = pd.read_csv(dataset)

    # Load model
    model = XGBClassifier()
    model.load_model("./jobs/model/xgb_model.json")

    # Predict churn probability
    dataset["Churn Probability"] = model.predict_proba(
        dataset.drop(columns=["Total Customer Spend", "Churn?_True."])
    )[:, 0]
    return dataset
