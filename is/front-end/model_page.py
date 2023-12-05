import os

import matplotlib.pyplot as plt
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://backend:8000"
API_TOKEN = os.getenv("API_TOKEN")


def app():
    st.title("Model Training")

    # Input for Google Drive ID
    gdrive_id = st.text_input("Enter your Google Drive ID:")

    # Only proceed if Google Drive ID is provided and the "Process" button is
    # clicked
    if gdrive_id and st.button("Train"):
        with st.spinner("Training..."):
            # API endpoint
            url = API_URL + f"/trains?gdrive_id={gdrive_id}"

            # Request headers
            headers = {"accept": "application/json", "api-token": API_TOKEN}

            # Send POST request to the backend API
            response = requests.post(url, headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()["data"]
                roc_curve = data["roc_curve"]
                fpr = roc_curve["fpr"]
                tpr = roc_curve["tpr"]
                auc = roc_curve["auc"]

                # Plot the AUC ROC curve
                plt.plot(fpr, tpr, label=f"AUC: {auc:.2f}")
                plt.xlabel("False Positive Rate")
                plt.ylabel("True Positive Rate")
                plt.title("AUC ROC Curve")
                plt.legend(loc="lower right")
                st.pyplot(plt)
                st.success("Model training completed successfully")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
