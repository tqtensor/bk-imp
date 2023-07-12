#import "template.typ": *
#let title = "Project: NYC Taxi Demand Forecasting"
#let author = "Do Vo Hoang Hung, Ngo Trieu Long, Tang Quoc Thai"
#let course_id = "CO5241"
#let instructor = "Quan Thanh Tho"
#let semester = "Spring 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

#abstract[
TODO: Abstract
]

== Project Description
The objective of this project is to develop a robust forecasting model to predict the demand for taxi trips in New York City (NYC). By leveraging time series analysis techniques and incorporating additional data, such as weather information, we aim to enhance the accuracy of the predictions and gain insights into the factors influencing taxi trip demand.

In addition to predicting the demand for taxi trips in NYC, this project also has the broader objective of utilizing the forecasted demand for dynamic pricing purposes. Dynamic pricing refers to the practice of adjusting prices based on real-time demand and supply conditions. By incorporating the forecasted demand into the dynamic pricing strategy, taxi service providers can optimize their pricing decisions, maximize revenue, and efficiently allocate their resources.

However, given the time constraints of the project, the focus will primarily be on developing a robust forecasting model to predict taxi trip demand accurately. This will lay the foundation for the subsequent phase of implementing dynamic pricing strategies.

By forecasting demand accurately and gaining insights into the factors influencing demand, this project sets the stage for the future implementation of dynamic pricing, which has the potential to enhance the efficiency, profitability, and overall customer experience in the taxi industry.

== Background Theory

== Data Preparation
=== Data Collection
The dataset is created from two sources:
- NYC Taxi and Limousine Commission (TLC) Trip Record Data with the script below.
- Weather data from the API of Meteo.

#figure(
  image("data_sources.png", width: 50%),
  caption: [Data Sources],
)

In the script below we can specify the type of dataset (yellow, green, fhv, fhvhv) and the year of the dataset. The script will download the dataset from the TLC website and save it in the folder `ml/nyc-dataset/data/trips`. The script will also download the weather data from the Meteo API and save it in the folder `ml/nyc-dataset/data/weather`.

```bash
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
```

== ML Pipeline

== Results Evaluation
