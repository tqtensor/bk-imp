import os

import matplotlib.pyplot as plt
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://backend:8000"
API_TOKEN = os.getenv("API_TOKEN")


def app():
    st.title("Budget Optimization")

    # Input for Google Drive ID
    gdrive_id = st.text_input("Enter your Google Drive ID:")

    # Input for budget
    budget = st.number_input(
        r"Enter budget (% of profit):",
        min_value=0.0,
        max_value=0.5,
        value=0.05,
    )

    # Create a box for the convincing factor inputs
    with st.expander("Convincing Factor"):
        st.markdown(
            r"""We could include that business insight into the optimization by setting the value for the convincing factor $\gamma$ as follows:

- $\gamma_{i}$ = 100. This is equivalent to giving less importance as deciding factor to the discount $c_{i}$  for customers whose churn probability $\alpha_{i}$ is below 0.55 (they are loyal and less likeley to churn) and/or greater than 0.95 (they will most likely leave despite the retention campaign)
- $\gamma_{i}$ = 1. This is equivalent to saying that the probability customer i will accept the discount $c_{i}$ is equal to $\beta = 1-e^{-c_{i}}$ for customer whose $\alpha_{i}$ $\in$ [0.55, 0.95]
"""
        )
        lower_bound = st.number_input(
            "Enter lower bound:", min_value=0.0, max_value=1.0, value=0.55
        )
        upper_bound = st.number_input(
            "Enter upper bound:", min_value=0.0, max_value=1.0, value=0.95
        )
        gamma = st.number_input("Enter gamma:", min_value=0.0, value=100.0)

    # Only proceed if Google Drive ID is provided and the "Optimize" button is clicked
    if gdrive_id and st.button("Optimize"):
        with st.spinner("Optimizing..."):
            # API endpoint
            url = (
                API_URL
                + f"/optimizations?gdrive_id={gdrive_id}&budget={budget}"
            )

            # Request headers
            headers = {
                "accept": "application/json",
                "api-token": API_TOKEN,
                "Content-Type": "application/json",
            }

            # Request data
            data = {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "gamma": gamma,
            }

            # Send POST request to the backend API
            response = requests.post(url, headers=headers, json=data)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()["data"]
                expected_total_profit_optimal = data[
                    "expected_total_profit_optimal"
                ]
                expected_total_profit_no_campaign = data[
                    "expected_total_profit_no_campaign"
                ]
                expected_total_profit_uniform_campaign = data[
                    "expected_total_profit_uniform_campaign"
                ]

                # Plot the data
                profits = [
                    expected_total_profit_no_campaign,
                    expected_total_profit_uniform_campaign,
                    expected_total_profit_optimal,
                ]
                labels = [
                    "No Campaign",
                    "Uniform Campaign",
                    "Optimal Campaign",
                ]
                plt.bar(labels, profits)
                plt.ylabel("Expected Total Profit")
                plt.title("Comparison of Expected Total Profits")
                st.pyplot(plt)
                st.success("Optimization completed successfully")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
