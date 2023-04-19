#!/bin/bash

# Set the directory where the JSON files should be stored
DATA_DIR="bigdata-mini-project/data/"

# Check if the Digital_Music.json file exists in the data directory
if [ ! -f "${DATA_DIR}Digital_Music.json" ]; then

  # If the file does not exist, download it from the first link
  echo "Downloading Digital_Music.json file..."
  wget --no-check-certificate -P "${DATA_DIR}" "https://jmcauley.ucsd.edu/data/amazon_v2/categoryFiles/Digital_Music.json.gz"

  # Extract the downloaded file
  echo "Extracting Digital_Music.json file..."
  gunzip "${DATA_DIR}Digital_Music.json.gz"

fi

# Check if the meta_Digital_Music.json file exists in the data directory
if [ ! -f "${DATA_DIR}meta_Digital_Music.json" ]; then

  # If the file does not exist, download it from the second link
  echo "Downloading meta_Digital_Music.json file..."
  wget --no-check-certificate -P "${DATA_DIR}" "https://jmcauley.ucsd.edu/data/amazon_v2/metaFiles2/meta_Digital_Music.json.gz"

  # Extract the downloaded file
  echo "Extracting meta_Digital_Music.json file..."
  gunzip "${DATA_DIR}meta_Digital_Music.json.gz"

fi

echo "Done."
