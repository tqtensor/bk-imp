import joblib
from fastapi import FastAPI

app = FastAPI()
model = joblib.load("model/RandomForestRegressor.pkl")


@app.post("/predict")
def predict(data: list):
    predictions = model.predict(data)
    return {"predictions": predictions}
