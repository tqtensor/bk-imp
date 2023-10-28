from xgboost import XGBClassifier
import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.model_selection import GridSearchCV

if __name__ == "__main__":
    # Read the file
    train_data = pd.read_csv("./jobs/data/train.csv")
    validation_data = pd.read_csv("./jobs/data/validation.csv")

    X_train = train_data.drop(["Churn?_True.", "Total Customer Spend"], axis=1)
    y_train = train_data["Churn?_True."]
    X_validation = validation_data.drop(
        ["Churn?_True.", "Total Customer Spend"], axis=1
    )
    y_validation = validation_data["Churn?_True."]

    # Define a hyperparameter grid for GridSearchCV
    param_grid = {
        "max_depth": [3, 5, 7],
        "eta": [0.1, 0.2, 0.3],
        "gamma": [0, 1, 2, 4],
        "min_child_weight": [1, 3, 6],
        "subsample": [0.7, 0.8, 0.9],
        "objective": ["binary:logistic"],
    }

    # Create the XGBoost model instance
    model = XGBClassifier()

    # Create GridSearchCV instance for hyperparameter tuning
    grid_search = GridSearchCV(
        model, param_grid, scoring="average_precision", cv=5, verbose=2
    )

    # Fit GridSearchCV to find the best hyperparameters
    grid_search.fit(X_train, y_train)

    # Get the best hyperparameters
    best_params = grid_search.best_params_

    print("Best Hyperparameters:", best_params)

    # Fit the XGBoost model with the best hyperparameters
    best_model = XGBClassifier(**best_params)
    best_model.fit(X_train, y_train)

    # Predict probabilities on the validation set
    y_pred_prob = best_model.predict_proba(X_validation)[:, 1]

    # Calculate PR AUC score
    pr_auc = average_precision_score(y_validation, y_pred_prob)
    print(f"PR AUC on validation set: {pr_auc:.4f}")

    # Save the model
    best_model.save_model("./jobs/model/xgb_model.json")
