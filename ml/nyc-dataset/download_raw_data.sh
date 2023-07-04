#!/bin/bash

# Ask the user to choose a dataset type
read -p "Enter the dataset type (yellow, green, fhv, fhvhv): " dataset_type

# Ask the user to choose a year or select "all years"
read -p "Enter the year for trip data download (e.g., 2021) or type 'all' for all years: " year

# Construct the dataset filter based on the chosen dataset type
dataset_filter=""
if [ "$dataset_type" != "all" ]; then
    dataset_filter="$dataset_type"
fi

# Construct the URL filter based on the chosen year
year_filter=""
if [ "$year" != "all" ]; then
    year_filter="$year"
fi

# Download the trip data using wget and apply the filters
cd ml/nyc-dataset
wget -i <(grep -i "$dataset_filter" raw_data_urls | grep -i "$year_filter") -P data/trips -w 2

# Download taxi zone shape file
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip .
unzip taxi_zones.zip -d data/taxi_zones
rm taxi_zones.zip
