import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://backend:8000"
API_TOKEN = os.getenv("API_TOKEN")


def process_data(
    gdrive_id,
    dataset_name,
    entity_column,
    label_column,
    profit_column,
    categorical_columns,
    numeric_columns,
):
    # API endpoint
    url = (
        API_URL
        + f"/datasets?gdrive_id={gdrive_id}&dataset_name={dataset_name}&entity_column={entity_column}&label_column={label_column}&profit_column={profit_column}"
    )

    # Headers
    headers = {
        "accept": "application/json",
        "api-token": API_TOKEN,
        "Content-Type": "application/json",
    }

    # Data
    data = {
        "categorical_columns": categorical_columns,
        "numeric_columns": numeric_columns,
    }

    # Make the API call
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        data = response.json()
        st.json(data["data"])
        return data["200"]
    else:
        return f"Error: {response.status_code} - {response.text}"


def app():
    st.title("Dataset Processing")

    # Collect inputs from the user
    gdrive_id = st.text_input("Enter your Google Drive ID:")
    dataset_name = st.text_input("Enter your dataset name:")
    entity_column = st.text_input("Enter your entity column:")
    label_column = st.text_input("Enter your label column:")
    profit_column = st.text_input("Enter your profit column:")
    categorical_columns = st.text_input(
        "Enter your categorical columns (comma-separated):"
    )
    numeric_columns = st.text_input(
        "Enter your numeric columns (comma-separated):"
    )

    # Convert comma-separated inputs to lists
    categorical_columns = [
        col.strip() for col in categorical_columns.split(",")
    ]
    numeric_columns = [col.strip() for col in numeric_columns.split(",")]

    if st.button("Process"):
        with st.spinner("Processing..."):
            result = process_data(
                gdrive_id,
                dataset_name,
                entity_column,
                label_column,
                profit_column,
                categorical_columns,
                numeric_columns,
            )
            st.success(result)
