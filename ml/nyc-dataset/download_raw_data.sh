#!/bin/bash

# Ask the user to choose a year or select "all years"
read -p "Enter the year for trip data download (e.g., 2021) or type 'all' for all years: " year

# Construct the URL filter based on the chosen year
if [ "$year" = "all" ]; then
    url_filter=""
else
    url_filter="_$year"
fi

# Download the trip data using wget and apply the URL filter
cd ml/nyc-dataset
wget -i <(grep "$url_filter" raw_data_urls.txt) -P data/ -w 2
