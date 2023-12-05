import pandas as pd
from fastapi import APIRouter, status
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
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
        train.drop(columns=["label", "entity_id", "profit"]),
        train["label"],
    )

    # Create the XGBoost model instance with default parameters
    model = XGBClassifier(use_label_encoder=False)

    # Fit the model to the training data
    model.fit(X_train, y_train)

    # Get the predicted probabilities
    train_pred_proba = model.predict_proba(X_train)

    # Use the probabilities of the positive class
    train_pred_proba_pos = train_pred_proba[:, 1]

    # Calculate false positive rates, true positive rates, and thresholds
    fpr, tpr, thresholds = roc_curve(y_train, train_pred_proba_pos)

    # Calculate AUC
    auc = roc_auc_score(y_train, train_pred_proba_pos)

    # Save the model
    model.save_model(f"/tmp/{gdrive_id}_model.json")

    return {
        status.HTTP_200_OK: "Model trained successfully.",
        "data": {
            "roc_curve": {
                "fpr": fpr.tolist()[1:],
                "tpr": tpr.tolist()[1:],
                "thresholds": thresholds.tolist()[1:],
                "auc": auc,
            },
        },
    }


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

    :return: A dictionary containing the HTTP status code and a success message.
    :rtype: dict
    """

    # Split dataset into train and test sets
    df = pd.read_csv(f"/tmp/{gdrive_id}_features.csv")
    _, test = train_test_split(df, test_size=0.2, random_state=42)
    X_test = test.drop(columns=["label", "entity_id", "profit"])

    # Load model
    model = XGBClassifier()
    model.load_model(f"/tmp/{gdrive_id}_model.json")

    # Predict churn probability
    X_test["proba"] = model.predict_proba(X_test)[:, 0]

    # Save predictions
    pd.concat([test, X_test["proba"]], axis=1).to_csv(
        f"/tmp/{gdrive_id}_predictions.csv", index=False
    )

    return {
        status.HTTP_200_OK: "Inference completed successfully.",
    }
