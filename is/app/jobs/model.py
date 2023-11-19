import os

import pandas as pd
from fastapi import APIRouter, status
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from xgboost import XGBClassifier

router = APIRouter()


@router.post(
    path="/trains",
    status_code=status.HTTP_200_OK,
)
async def train(gdrive_id: str):
    """
    Trains an XGBoost model on the dataset specified by the Google Drive ID.
    The dataset is split into training and test sets, and GridSearchCV is used
    for hyperparameter tuning. The best model is saved to a file.

    :param gdrive_id: The Google Drive ID of the dataset to be used for
    training.
    :type gdrive_id: str
    :return: A dictionary containing the ROC AUC and F1-score of the best
    model on the training set.
    :rtype: dict
    """

    # Split dataset into train and test sets
    df = pd.read_csv(f"/tmp/{gdrive_id}_features.csv")
    train, _ = train_test_split(df, test_size=0.2, random_state=42)
    X_train, y_train = (
        train.drop(columns=["label", "entity_id"]),
        train["label"],
    )

    # Define a hyperparameter grid for GridSearchCV
    param_grid = {
        "max_depth": [3, 5, 7],
        "eta": [0.1, 0.2, 0.3],
        "gamma": [0, 1, 2, 4],
        "min_child_weight": [1, 3, 6],
        "subsample": [0.7, 0.8, 0.9],
        "objective": ["binary:logistic"],
    }

    # Create the XGBoost model instance with default parameters
    model = XGBClassifier(use_label_encoder=False)

    # Fit the model to the training data
    model.fit(X_train, y_train)

    # Calculate ROC AUC and F1-score on train set
    train_pred = model.predict(X_train)
    roc_auc = roc_auc_score(y_train, train_pred)
    f1 = f1_score(y_train, train_pred)

    # Save the model
    model.save_model(f"/tmp/{gdrive_id}_model.json")

    return {"roc_auc": roc_auc, "f1_score": f1}


@router.post(
    path="/inferences",
    status_code=status.HTTP_200_OK,
)
async def inference(gdrive_id: str):
    """
    Runs the inference model to determine the churn probability of each
    customer. The function loads the dataset and the trained model, makes
    predictions, and saves the predictions to a CSV file.

    :param gdrive_id: The Google Drive ID of the dataset to run the inference model on.
    :type gdrive_id: str

    :return: None. The function saves the predictions to a CSV file.
    :rtype: None
    """

    # Split dataset into train and test sets
    df = pd.read_csv(f"/tmp/{gdrive_id}_features.csv")
    _, test = train_test_split(df, test_size=0.2, random_state=42)
    X_test = test.drop(columns=["label", "entity_id"])

    # Load model
    model = XGBClassifier()
    model.load_model(f"/tmp/{gdrive_id}_model.json")

    # Predict churn probability
    X_test["proba"] = model.predict_proba(X_test)[:, 0]

    # Save predictions
    pd.concat([test, X_test["proba"]], axis=1).to_csv(
        f"/tmp/{gdrive_id}_predictions.csv", index=False
    )
