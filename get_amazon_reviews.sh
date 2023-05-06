#!/bin/bash

# Set the directory where the JSON files should be stored
DATA_DIR="bigdata-mini-project/data/"

# Prompt the user for the dataset name
read -p "Enter the name of the Amazon review dataset to download (e.g., Digital_Music): " DATASET_NAME

# Check if the JSON file for the specified dataset exists in the data directory
if [ ! -f "${DATA_DIR}${DATASET_NAME}.json" ]; then

  # If the file does not exist, download it from the first link
  echo "Downloading ${DATASET_NAME}.json file..."
  wget --no-check-certificate -P "${DATA_DIR}" "https://jmcauley.ucsd.edu/data/amazon_v2/categoryFiles/${DATASET_NAME}.json.gz"

  # Extract the downloaded file
  echo "Extracting ${DATASET_NAME}.json file..."
  gunzip "${DATA_DIR}${DATASET_NAME}.json.gz"

fi

# Check if the meta JSON file for the specified dataset exists in the data directory
if [ ! -f "${DATA_DIR}meta_${DATASET_NAME}.json" ]; then

  # If the file does not exist, download it from the second link
  echo "Downloading meta_${DATASET_NAME}.json file..."
  wget --no-check-certificate -P "${DATA_DIR}" "https://jmcauley.ucsd.edu/data/amazon_v2/metaFiles2/meta_${DATASET_NAME}.json.gz"

  # Extract the downloaded file
  echo "Extracting meta_${DATASET_NAME}.json file..."
  gunzip "${DATA_DIR}meta_${DATASET_NAME}.json.gz"

fi

echo "Done."
