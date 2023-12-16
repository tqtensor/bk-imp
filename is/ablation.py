import json
import os

import numpy as np
import requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))

api_url = "http://localhost:8000/optimizations"
gdrive_id = "1eoUK9SDh-7ZV-wMbZ56eBy7X1ufoBjDE"
api_token = "2vR7Zmm#k9o@mxOs"

for budget in np.arange(0.01, 0.55, 0.01):
    payload = {
        "lower_bound": 0.55,
        "upper_bound": 0.95,
        "gamma": 100,
    }
    headers = {
        "accept": "application/json",
        "api-token": api_token,
        "Content-Type": "application/json",
    }
    response = requests.post(
        api_url + f"?gdrive_id={gdrive_id}&budget={budget}",
        json=payload,
        headers=headers,
    )
    data = response.json()
    budget = int(budget * 100)
    filename = f"budget_{budget}.json"

    with open(filename, "w") as file:
        json.dump(data, file)
