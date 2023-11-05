import os

import gdown
import numpy as np
import pandas as pd

if __name__ == "__main__":
    # Download the file from Google Drive
    if not os.path.exists("./jobs/data"):
        os.makedirs("./jobs/data")
    if not os.path.exists("./jobs/data/churn.txt"):
        gdown.download(
            id="1uCEfEtIH1AYyW1SFzYZjKRnFMZu8_qJw",
            output="./jobs/data/churn.txt",
            quiet=False,
        )
    else:
        print("File has been already downloaded")

    # Read the file
    churn_dataset = pd.read_csv("./jobs/data/churn.txt")

    # Data preprocessing
    churn_dataset = churn_dataset.drop("Phone", axis=1)
    churn_dataset["Area Code"] = churn_dataset["Area Code"].astype(object)
    churn_dataset["Total Customer Spend"] = churn_dataset.apply(
        lambda x: x["Day Charge"]
        + x["Night Charge"]
        + x["Eve Charge"]
        + x["Intl Charge"],
        axis=1,
    )
    churn_dataset = churn_dataset.drop(
        ["Day Charge", "Eve Charge", "Night Charge", "Intl Charge"], axis=1
    )

    churn_dataset = pd.get_dummies(churn_dataset)
    churn_dataset = pd.concat(
        [
            churn_dataset["Churn?_True."],
            churn_dataset.drop(["Churn?_False.", "Churn?_True."], axis=1),
        ],
        axis=1,
    )

    # Split the dataset into train and test
    train_data, validation_data, test_data = np.split(
        churn_dataset.sample(frac=1, random_state=1729),
        [int(0.6 * len(churn_dataset)), int(0.7 * len(churn_dataset))],
    )
    train_data.to_csv("./jobs/data/train.csv", index=False)
    validation_data.to_csv("./jobs/data/validation.csv", index=False)
    test_data.to_csv("./jobs/data/test.csv", index=False)
