#import "template.typ": *
#let title = "Project: NYC Taxi Demand Forecasting"
#let author = "Do Vo Hoang Hung, Ngo Trieu Long, Tang Quoc Thai"
#let course_id = "CO5241"
#let instructor = "Quan Thanh Tho"
#let semester = "Spring 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#set text(lang:"en", hyphenate:true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

= Project Description
The objective of this project is to develop a robust forecasting model to predict the demand for taxi trips in New York City (NYC). By leveraging time series analysis techniques and incorporating additional data, such as weather information, we aim to enhance the accuracy of the predictions and gain insights into the factors influencing taxi trip demand.

In addition to predicting the demand for taxi trips in NYC, this project also has the broader objective of utilizing the forecasted demand for dynamic pricing purposes. Dynamic pricing refers to the practice of adjusting prices based on real-time demand and supply conditions. By incorporating the forecasted demand into the dynamic pricing strategy, taxi service providers can optimize their pricing decisions, maximize revenue, and efficiently allocate their resources.

However, given the time constraints of the project, the focus will primarily be on developing a robust forecasting model to predict taxi trip demand accurately. This will lay the foundation for the subsequent phase of implementing dynamic pricing strategies.

By forecasting demand accurately and gaining insights into the factors influencing demand, this project sets the stage for the future implementation of dynamic pricing, which has the potential to enhance the efficiency, profitability, and overall customer experience in the taxi industry.

= Background Theory

= Data Preparation

== Data Collection
The dataset is created from two sources:
- NYC Taxi and Limousine Commission (TLC) Trip Record Data.
- Weather data from the API of Meteo.

#figure(
  image("data_sources.png", width: 50%),
  caption: [Data Sources],
)

=== NYC Taxi and Limousine Commission (TLC) Trip Record Data
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

=== Weather data from the API of Meteo
The map of NYC taxi zones is shown below and shapefile can be downloaded from (https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip). A shapefile is a common geospatial vector data format used in geographic information system (GIS) software. It contains both geometric and attribute information about geographic features, such as points, lines, and polygons. In the case of the NYC taxi zones, the shapefile provides information about the boundaries and attributes of each taxi zone in the city.

#figure(
  image("location_data.png", width: 75%),
  caption: [Taxi Zones of NYC],
)

The Python code below loads a shapefile of NYC taxi zones and we calculate the center of each zone. We then use the center coordinates to query the Meteo API and download the weather data for each zone. The weather data is saved in the folder `ml/nyc-dataset/data/weather`.

The API has this pattern:

#emph(text(blue)[
  https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,rain_sum&timezone=GMT
])

Where:

- `lat`: latitude of the zone center.
- `lon`: longitude of the zone center.
- `start_date`: start date of the weather data.
- `end_date`: end date of the weather data.

The return weather data will contains the following fields:
- `weathercode`: weather code.
- `temperature_2m_max`: maximum temp.
- `temperature_2m_min`: minimum temp.
- `temperature_2m_mean`: mean temp.
- `precipitation_sum`: precipitation sum.
- `rain_sum`: rain sum.

```python
def get_lat_lon(sf):
    content = []
    transformer = pyproj.Transformer.from_crs(2263, 4326, always_xy=True)

    for sr in sf.shapeRecords():
        shape = sr.shape
        rec = sr.record
        loc_id = rec[shp_dic["LocationID"]]

        x = (shape.bbox[0] + shape.bbox[2]) / 2
        y = (shape.bbox[1] + shape.bbox[3]) / 2
        lon, lat = transformer.transform(x, y)

        content.append((loc_id, lon, lat))

    return pd.DataFrame(
        content, columns=["LocationID", "longitude", "latitude"]
    )


# Read shape file
sf = shapefile.Reader("nyc-dataset/data/taxi_zones/taxi_zones.shp")
fields_name = [field[0] for field in sf.fields[1:]]
shp_dic = dict(zip(fields_name, list(range(len(fields_name)))))
attributes = sf.records()
shp_attr = [dict(zip(fields_name, attr)) for attr in attributes]

df_loc = pd.DataFrame(shp_attr).join(
    get_lat_lon(sf).set_index("LocationID"), on="LocationID"
)
```

Example of the location data from `df_loc`.

#align(center)[#table(
  columns: 5,
  align: (col, row) => (auto,auto,auto,auto,auto,).at(col),
  inset: 6pt,
  text(size: 8pt, fill: blue, weight: "medium")[zone], text(size: 8pt, fill: blue, weight: "medium")[location\_id], text(size: 8pt, fill: blue, weight: "medium")[borough], text(size: 8pt, fill: blue, weight: "medium")[longitude], text(size: 8pt, fill: blue, weight: "medium")[latitude],
  [Newark Airport],
  [1],
  [EWR],
  [-74.171526],
  [40.689488],
  [Jamaica Bay],
  [2],
  [Queens],
  [-73.822490],
  [40.610791],
  [Allerton/Pelham Gardens],
  [3],
  [Bronx],
  [-73.844947],
  [40.865745],
  [Alphabet City],
  [4],
  [Manhattan],
  [-73.977726],
  [40.724137],
  [Arden Heights],
  [5],
  [Staten Island],
  [-74.187537],
  [40.550665],
)
]

== Data Preprocessing
First, we group the data by hour and location to calculate the number of trips. We then filter the data from 2021 and 2022.

```python
# Read the data
df = pd.read_parquet("nyc-dataset/data/trips")

# Filter the data from 2021 and 2022
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df = df[
    (df["tpep_pickup_datetime"].dt.year >= 2021)
    & (df["tpep_pickup_datetime"].dt.year <= 2022)
]
df["tpep_pickup_hour"] = df["tpep_pickup_datetime"].dt.round("1h")

# Group the data by hour and location to calculate the number of trips
df = (
    df.groupby(["tpep_pickup_hour", "PULocationID"])
    .size()
    .reset_index(name="trip_count")
)
df["time"] = df["tpep_pickup_hour"].dt.date
df.rename({"PULocationID": "location_id"}, axis=1, inplace=True)
```

Second, we load the weather data from the folder `ml/nyc-dataset/data/weather` and merge it with the trip data.

```python
dfs = []
for filename in glob.glob(f"{output_dir}/*.csv"):
    df_weather = pd.read_csv(filename)
    df_weather["time"] = pd.to_datetime(df_weather["time"]).dt.date
    df_weather["location_id"] = int(filename.split("_")[1].split(".")[0])
    dfs.append(df_weather)
df_weather = pd.concat(dfs)

dataset = df.merge(
    df_weather,
    left_on=["time", "location_id"],
    right_on=["time", "location_id"],
    how="left",
)
```

Example of the dataset after merging the trip data with the weather data.

#align(center)[#table(
  columns: 9,
  align: (col, row) => (auto,auto,auto,auto,auto,auto,auto,auto,auto,).at(col),
  inset: 6pt,
  text(size: 8pt, fill: blue, weight: "medium")[pickup\_dt], text(size: 8pt, fill: blue, weight: "medium")[location\_id], text(size: 8pt, fill: blue, weight: "medium")[trip\_count], text(size: 8pt, fill: blue, weight: "medium")[weather\_code],
  text(size: 8pt, fill: blue, weight: "medium")[temp\_2m\_max], text(size: 8pt, fill: blue, weight: "medium")[temp\_2m\_min],
  text(size: 8pt, fill: blue, weight: "medium")[temp\_2m\_mean], text(size: 8pt, fill: blue, weight: "medium")[ppt\_sum], text(size: 8pt, fill: blue, weight: "medium")[rain\_sum],
  [2022-12-01 13:00:00],
  [236],
  [1],
  [3.0],
  [8.6],
  [0.9],
  [3.8],
  [0.0],
  [0.0],
  [2022-12-01 13:00:00],
  [239],
  [1],
  [3.0],
  [8.8],
  [1.1],
  [4.0],
  [0.0],
  [0.0],
  [2022-12-01 14:00:00],
  [68],
  [1],
  [3.0],
  [9.3],
  [1.2],
  [4.2],
  [0.0],
  [0.0],
  [2022-12-01 14:00:00],
  [90],
  [1],
  [3.0],
  [9.2],
  [1.2],
  [4.1],
  [0.0],
  [0.0],
  [2022-12-01 15:00:00],
  [141],
  [1],
  [3.0],
  [8.7],
  [1.0],
  [3.9],
  [0.0],
  [0.0],
  [2022-12-01 15:00:00],
  [162],
  [1],
  [3.0],
  [8.4],
  [0.7],
  [3.6],
  [0.0],
  [0.0],
  [2022-12-01 15:00:00],
  [237],
  [1],
  [3.0],
  [8.7],
  [1.0],
  [3.9],
  [0.0],
  [0.0],
  [2022-12-01 16:00:00],
  [141],
  [2],
  [3.0],
  [8.7],
  [1.0],
  [3.9],
  [0.0],
  [0.0],
  [2022-12-01 16:00:00],
  [162],
  [1],
  [3.0],
  [8.4],
  [0.7],
  [3.6],
  [0.0],
  [0.0],
  [2022-12-02 00:00:00],
  [237],
  [1],
  [1.0],
  [5.5],
  [-2.7],
  [1.1],
  [0.0],
  [0.0],
)
]

= ML Pipeline

= Results Evaluation
