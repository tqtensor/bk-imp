import os
from typing import List

from fastapi import APIRouter, status

router = APIRouter()

import json

import featurewiz as fwiz
import gdown
import pandas as pd


@router.post(
    path="/datasets",
    status_code=status.HTTP_200_OK,
)
async def preprocess(
    gdrive_id: str,
    dataset_name: str,
    entity_column: str,
    label_column: str,
    categorical_columns: List[str],
    numeric_columns: List[str],
    profit_column: str,
) -> dict:
    """
    Preprocesses the dataset by performing operations such as downloading the
    dataset, converting column types, dropping unnecessary columns, and
    performing feature engineering. The preprocessed dataset and its metadata
    are saved to files.

    :param gdrive_id: The Google Drive ID of the dataset to be preprocessed.
    :type gdrive_id: str
    :param dataset_name: The name of the dataset.
    :type dataset_name: str
    :param entity_column: The name of the entity column in the dataset.
    :type entity_column: str
    :param label_column: The name of the label column in the dataset.
    :type label_column: str
    :param categorical_columns: The list of categorical columns in the dataset.
    :type categorical_columns: List[str]
    :param numeric_columns: The list of numeric columns in the dataset.
    :type numeric_columns: List[str]
    :param profit_column: The name of the profit column in the dataset.
    :type profit_column: str
    :return: A dictionary containing the HTTP status code and a success message.
    :rtype: dict
    :raises Exception: If there is an error reading the file or converting
    numeric columns.
    """

    if not os.path.exists(f"/tmp/{gdrive_id}"):
        gdown.download(id=gdrive_id, output=f"/tmp/{gdrive_id}", quiet=False)

    try:
        df = pd.read_csv(f"/tmp/{gdrive_id}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")

    # Preprocess
    for cat_col in categorical_columns:
        df[cat_col] = df[cat_col].astype("category")

    try:
        for num_col in numeric_columns:
            df[num_col] = df[num_col].astype("float32")
    except Exception as e:
        raise Exception(f"Error converting numeric column: {e}")

    # Drop columns that are not needed
    needed_columns = (
        [entity_column, label_column, profit_column]
        + categorical_columns
        + numeric_columns
    )
    df.drop(
        columns=[col for col in df.columns if col not in needed_columns],
        inplace=True,
    )

    # Feature engineering
    feature_names, features = fwiz.featurewiz(
        dataname=df.drop(columns=[entity_column, profit_column]),
        target=label_column,
        corr_limit=0.70,
        verbose=0,
        sep=",",
        header=0,
        test_data="",
        feature_engg=["interactions", "groupby"],
        category_encoders="HashingEncoder",
        dask_xgboost_flag=False,
        nrows=None,
        skip_sulov=False,
        skip_xgboost=False,
    )

    # Save features
    features = pd.concat(
        [df[[entity_column, profit_column]], features], axis=1
    )
    features.rename(
        columns={
            label_column: "label",
            entity_column: "entity_id",
            profit_column: "profit",
        },
        inplace=True,
    )
    features.to_csv(f"/tmp/{gdrive_id}_features.csv", index=False)
    features_metadata = {
        "dataset_name": dataset_name,
        "path": f"/tmp/{gdrive_id}_features.csv",
        "features": feature_names,
    }
    with open(f"/tmp/{gdrive_id}_features_metadata.json", "w") as f:
        json.dump(features_metadata, f)

    return {
        status.HTTP_200_OK: "Dataset preprocessed successfully.",
    }
