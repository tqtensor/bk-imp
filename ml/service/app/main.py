import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI()
model = joblib.load("model/RandomForestRegressor.pkl")


# Get expected model input columns
expected_columns = model.steps[-1][1].feature_names_in_


@app.post("/predict")
def predict(data: list):
    try:
        # Convert JSON payload to pandas DataFrame
        input_data = pd.get_dummies(pd.DataFrame(data), drop_first=True)

        # Add missing columns with False values
        for column in expected_columns:
            if column not in input_data.columns:
                input_data[column] = False

        # Reorder columns to match the training data
        input_data = input_data.reindex(
            columns=expected_columns, fill_value=False
        )

        # Perform prediction
        predictions = model.predict(input_data)

        return {"predictions": predictions.tolist()}

    except Exception as e:
        # Return appropriate error response
        raise HTTPException(status_code=400, detail=str(e))
