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

In this background theory session, we will explore two approaches: regression and SARIMAX, which are commonly used in various fields for modeling and forecasting. We will begin by explaining the foundations of these techniques and then delve into the potential reasons behind the longer convergence time and difficulty in achieving convergence with SARIMAX.

== Regression Approach

Regression is a statistical modeling technique used to examine the relationship between a dependent variable and one or more independent variables. It aims to find the best-fitting line or curve that represents the relationship between the variables. The primary objective of regression analysis is to estimate the coefficients of the independent variables and establish their statistical significance.

The fundamental concept in regression analysis is the assumption that the relationship between the dependent variable and independent variables is linear. However, various types of regression models exist to accommodate different scenarios, such as linear regression, polynomial regression, and multiple regression, among others.

Regression models provide valuable insights into the impact of independent variables on the dependent variable and help in predicting future outcomes based on these relationships.

== SARIMAX Approach
SARIMAX, which stands for Seasonal AutoRegressive Integrated Moving Average with eXogenous variables, is a popular method used for time series analysis and forecasting. It extends the traditional ARIMA model by incorporating additional factors, such as seasonality and exogenous variables.

ARIMA (AutoRegressive Integrated Moving Average) models capture the linear dependencies in a time series by considering the autoregressive (AR), integrated (I), and moving average (MA) components. These models are suitable for data exhibiting trends, seasonality, and non-stationarity.

SARIMAX further enhances the ARIMA model by introducing exogenous variables that can impact the time series. Exogenous variables are independent variables that may have a causal relationship with the dependent variable but are not affected by it.

In this project we found that applying SARIMAX on the demand forecast of NYC taxi trips is not as effective as applying regression. The reasons for this are explained in the next section.
- While SARIMAX is a powerful modeling technique, it can sometimes present challenges that result in longer convergence time and difficulties in achieving convergence. Several factors could contribute to these issues:

- Data Complexity: SARIMAX models can struggle with complex datasets that exhibit high levels of noise, outliers, or irregular patterns. When the data contains intricate relationships or unexpected variations, the model may require more iterations to converge.

- Seasonality: SARIMAX incorporates the consideration of seasonal patterns in the data. However, if the seasonality is highly irregular or changes over time, the model may face difficulties in capturing and adjusting to these patterns accurately.

- Exogenous Variables: The inclusion of exogenous variables introduces additional complexity to the model. If the exogenous variables are not well-correlated with the dependent variable or have weak explanatory power, it can hinder convergence and impact the model's forecasting performance.

- Insufficient Data: SARIMAX models require a sufficient amount of historical data to estimate the model parameters accurately. If the dataset is limited, contains gaps, or lacks stationarity, the model's convergence may be compromised.

- Model Hyperparameters: SARIMAX models involve several hyperparameters that need to be tuned appropriately. Inadequate selection of hyperparameters, such as the order of differencing or the number of seasonal terms, can lead to convergence issues.

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

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
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
```)

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

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
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
```)

Second, we load the weather data from the folder `ml/nyc-dataset/data/weather` and merge it with the trip data.

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
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
```)

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

== Architecture

#figure(
  image("pipeline.jpg", width: 100%),
  caption: [ML Training and Deployment Pipeline],
)

The ML pipeline consists of the following steps:
1. Feature Engineering:
  - Transform raw timeseries data into meaningful features.
  - Create sliding window features to capture patterns and dependencies within the data.

2. Split Dataset:
  - Partition the dataset into train and test sets.
  - Ensure that future values are not mixed into the training data to prevent data leakage.

3. Declare Possible Models:
  - Identify and declare several potential regression models for evaluation.

4. Train and Predict:
  - Train the selected models using the train set.
  - Predict the target variable using the test set.
  - Calculate metrics such as MAPE and RMSLE to assess model performance.

5. Model Evaluation:
  - Analyze the results to determine the best-performing model.
  - Save the best model in a pickle file format.

6. Deployment:
  - Retrieve the saved model from the pickle file.
  - Deploy the model as an API for real-time predictions or integration with other systems.

By following this structured ML pipeline, researchers and practitioners can effectively develop, evaluate, and deploy regression models for timeseries data, ensuring reliable and accurate predictions in various applications.

== Feature Engineering

The `create_sliding_window` function is designed to generate sliding window features for a given timeseries dataset. Sliding window features are an essential technique in time series analysis that capture temporal patterns and dependencies in the data. The function takes two parameters: `df`, which represents the timeseries dataset, and `window_size`, which specifies the size of the sliding window.

To create the sliding window features, the function first sorts the data to ensure chronological order within each group. It then applies the sliding window operation within each group defined by the "location_id" column. Starting from 1 up to the specified `window_size`, the function creates new columns named "trip_count_backward_i", where "i" represents the index of the sliding window. Each column contains the lagged values of the "trip_count" variable shifted by "i" time steps.

To ensure consistency in the dataset, the function removes the first rows within each group that contain NaN values resulting from the shifting operation. This step is necessary to avoid introducing biased or incomplete data into the subsequent analysis.

Sliding window features are crucial in time series analysis as they provide valuable information about the historical behavior and trends in the data. By incorporating lagged values as additional input features, the model can learn from the past to make predictions about future values. These features enable the model to capture temporal dependencies, seasonality, and other patterns that may influence the target variable. Therefore, the sliding window function plays a pivotal role in extracting relevant features and enhancing the predictive capabilities of time series models.

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
```python
def create_sliding_window(df, window_size):
    # Sort the data to ensure chronological order within each group
    tmp_data = df.copy()
    tmp_data = tmp_data.sort_values(
        ["location_id", "day_of_year", "hour"], ascending=True
    )

    # Apply sliding window to create new columns within each group
    grouped = tmp_data.groupby("location_id")
    for i in range(1, window_size + 1):
        col_name = f"trip_count_backward_{i}"
        tmp_data[col_name] = grouped["trip_count"].shift(i)

    # Remove the first rows within each group that contain NaN values due to shifting
    tmp_data = (
        tmp_data.groupby("location_id")
        .apply(lambda x: x.iloc[window_size:])
        .reset_index(drop=True)
    )
    return tmp_data
```)

== Train-Test Split

The train-test split is a crucial step in machine learning to evaluate the performance of a model on unseen data. In the provided code snippet, the dataset is split into training and testing sets for regression analysis.

To prevent mixing future values into the training data and ensure the integrity of the analysis, the shuffle parameter is set to False in the train_test_split function. This ensures that the data is split sequentially, maintaining the temporal order of the observations. By avoiding shuffling, the model is trained on historical data and tested on future data, simulating real-world scenarios where predictions are made based on past information.

Before splitting the data, preprocessing steps are applied to handle categorical columns. One-hot encoding is employed to expand categorical columns such as location_id and weather_code into numeric representations. This technique converts each category into binary columns, indicating the presence or absence of a specific category. The resulting encoded features are stored in `X_num`.

However, it is worth noting that for certain models, like CatBoost, there is no need to perform one-hot encoding explicitly. CatBoost is a gradient boosting algorithm that natively handles categorical features. Hence, for an alternative version using CatBoost, the categorical columns do not require one-hot encoding, and the original `X_cat` can be used directly.

The resulting splits consist of `X_train_cat`, `X_test_cat`, `X_train_num`, and `X_test_num`, representing the categorical and numerical features of the training and testing sets, respectively. The target variable y is split accordingly into `y_train` and `y_test`.

By performing the train-test split with attention to the sequential order and applying appropriate preprocessing techniques, we can evaluate the model's performance accurately and make predictions on unseen data, reflecting real-world scenarios.

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
```python
y = df_for_reg["trip_count"]
X_cat = df_for_reg.drop(["trip_count"], axis=1)
X_num = pd.get_dummies(X_cat, drop_first=True)
X_train_cat, X_test_cat, y_train, y_test = train_test_split(
    X_cat, y, test_size=0.2, shuffle=False
)
X_train_num, X_test_num, y_train, y_test = train_test_split(
    X_num, y, test_size=0.2, shuffle=False
)
```)


== Model Training Pipeline

We use three regression models for evaluation: CatBoost, XGBoost, and Random Forest. The models are trained using the training set and evaluated using the test set. The evaluation metrics include MAPE and RMSLE.

#block(
  width: 100%,
  clip: false,
  fill: luma(90%),
```python
# Define the regressors
regressors = {
    "CatBoost": CatBoostRegressor(
        cat_features=["location_id", "weathercode"],
        iterations=1000,
        learning_rate=0.1,
        verbose=0,
    ),
    "XGBRegressor": XGBRegressor(),
    "RandomForestRegressor": RandomForestRegressor(n_estimators=20, n_jobs=-1),
}

# Create the pipelines
pipelines = []
for regressor_name, regressor in regressors.items():
    pipeline = Pipeline([(regressor_name, regressor)])
    pipelines.append(pipeline)
```)

== Serving API

We use fastAPI to deploy the model as an API for real-time predictions or integration with other systems. The API can be deployed easily using Docker. The Dockerfile is provided in the `ml/service/Dockerfile`.

Simply run the following command to build the Docker image:

```bash
docker build -t fastapi-deployment .
docker run -p 8000:80 fastapi-deployment
```

The API can be accessed at `http://localhost:8000/docs`. Or can be tested using the following command:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
    {
        "location_id": "location_id_0082",
        "weathercode": "weather_code_0003",
        "temperature_2m_max": 16.5,
        "temperature_2m_min": 8.6,
        "temperature_2m_mean": 12.6,
        "precipitation_sum": 0.0,
        "rain_sum": 0.0,
        "day_of_year": 131,
        "day_of_month": 11,
        "day_of_week": 1,
        "is_weekend": 0,
        "year": 2021,
        "month": 5,
        "hour": 22,
        "trip_count_backward_1": 1.0,
        "trip_count_backward_2": 2.0,
        "trip_count_backward_3": 1.0,
        "trip_count_backward_4": 1.0,
        "trip_count_backward_5": 1.0,
        "trip_count_backward_6": 3.0,
        "trip_count_backward_7": 1.0
    },
    {
        "location_id": "location_id_0065",
        "weathercode": "weather_code_0061",
        "temperature_2m_max": 33.5,
        "temperature_2m_min": 25.1,
        "temperature_2m_mean": 28.6,
        "precipitation_sum": 3.0,
        "rain_sum": 3.0,
        "day_of_year": 219,
        "day_of_month": 7,
        "day_of_week": 6,
        "is_weekend": 1,
        "year": 2022,
        "month": 8,
        "hour": 11,
        "trip_count_backward_1": 6.0,
        "trip_count_backward_2": 1.0,
        "trip_count_backward_3": 3.0,
        "trip_count_backward_4": 2.0,
        "trip_count_backward_5": 6.0,
        "trip_count_backward_6": 2.0,
        "trip_count_backward_7": 1.0
    }
]'
```

= Results Evaluation

== Feature Importance

The top 5 most important features for each model in training our dataset have been identified as below:

#figure(
  image("catboost_feature_importance.png", width: 100%),
  caption: [CatBoost Feature Importance],
)

#figure(
  image("xgboost_feature_importance.png", width: 100%),
  caption: [RandomForestRegressor Feature Importance],
)

#figure(
  image("rf_feature_importance.png", width: 100%),
  caption: [RandomForestRegressor Feature Importance],
)

It is observed that the demand in the previous hours has the greatest influence on predicting the demand for a specific hour on a specific day. Additionally, the time of day is also a significant factor in determining the need for taxi usage across all three models. This implies that when predicting demand for a future day that is distant from the current day, the accuracy of the predictions may significantly decrease. To improve accuracy, it is recommended to update the input and make predictions on an hourly basis.

There is a wide range of loss functions available for evaluating regression models, and there is no universally optimal function for all scenarios. The choice of the appropriate loss function is critical and depends on the specific characteristics of the data. Each loss function has its own unique properties. Several factors come into play when selecting a suitable loss function, such as the algorithm employed, the presence of outliers in the data, the requirement for differentiability, and more. In this section, we will explore various approaches to loss functions and determine which set of metrics will be utilized to assess our models.

== Used Metrics

=== Mean Absolute Error (MAE)

MAE (Mean Absolute Error) is a commonly used metric for evaluating time series models. It measures the average magnitude of errors between predicted and actual values. MAE is suitable for time series analysis as it provides a measure of the average absolute deviation from the true values over a given period.

Pros:
-	Intuitive interpretation: MAE represents the average absolute deviation of the predictions from the actual values, making it easy to understand and interpret.
-	Robust to outliers: MAE is less sensitive to outliers compared to other metrics like RMSE, which makes it suitable for handling extreme values often present in time series data.
-	Reflects magnitude of errors: MAE captures the magnitude of errors without considering their direction, providing insights into the overall accuracy of the model's predictions.

Cons:
-	Ignores error direction and patterns: MAE treats positive and negative errors equally, disregarding the direction of errors and potential patterns such as over- or under-predictions. This can be a limitation if the direction of errors is important in the specific time series analysis.
-	Equal weighting of errors: MAE assigns equal weight to all errors, which may not be desirable in cases where certain errors should be penalized more heavily.

=== Root Mean Squared Error (RMSE)

Root Mean Squared Error (RMSE) is a commonly used metric for evaluating the performance of models. It measures the average magnitude of the errors between the predicted and actual values, giving higher weight to larger errors

Pros:
-	RMSE provides a measure of the overall model accuracy, taking into account both the bias and variability of the errors.
-	It is widely used and easy to interpret since it is in the same unit as the target variable.
-	RMSE penalizes large errors more heavily, which will emphasize the outliers.

Cons:
-	RMSE is sensitive to outliers, meaning that extreme values can disproportionately influence the metric.
-	It does not provide a direct interpretation of the percentage of error, making it less intuitive for non-technical audiences.
-	RMSE treats positive and negative errors equally, which may not be desirable in all cases.

=== Mean Absolute Percentage Error (MAPE)

Mean Absolute Percentage Error is commonly used metric for evaluating the performance of time series models. It measures the average percentage difference between the predicted and actual values.

Pros:
-	MAPE provides a measure of the average relative error, which is helpful for understanding the accuracy of the predictions in percentage terms.
-	It is a scale-independent metric, making it suitable for comparing the performance of models across different datasets and variables.
-	MAPE is easy to interpret and understand, as it represents the average percentage deviation from the actual values.

Cons:
-	MAPE can be sensitive to zero or close-to-zero actual values, as the percentage calculation may become undefined or very large.
-	It may not be suitable for situations where small errors are more important than larger errors.
-	MAPE does not account for the direction of the errors, treating over-predictions and under-predictions equally.

=== Root Mean Squared Logarithmic Error (RMSLE)

Root Mean Squared Logarithmic Error measures the root mean squared logarithmic difference between the predicted and actual values.

Pros:
-	RMLSE penalizes large errors more than MAE or RMSE, making it more sensitive to outliers.
-	It is a scale-independent metric, making it suitable for comparing models across different datasets and variables.
-	RMLSE handles zero and negative values gracefully by applying a logarithmic transformation, preventing undefined values.

Cons:
-	RMLSE can be sensitive to small actual values, as the logarithmic transformation can amplify the differences.
-	It may not be suitable for situations where small errors are more important than larger errors.
-	RMLSE does not provide a direct interpretation in the same way as MAE or MAPE.

=== Mean Under-Prediction (MUP) and Mean Over-Prediction (MOP)

MUP and MOP provide insights into the average magnitude of under-predictions and over-predictions made by the model. A higher MUP value indicates that the model tends to under-predict the values, on average. It signifies that the predicted values are consistently lower than the actual values. And vice versa, for MOP, A higher MOP value indicates that the model tends to over-predict the values, on average.

Pros:
-	Reflects the tendency of the model to over or under-estimate the target variable.
-	Helps identify potential biases or inaccuracies in the model that consistently lead to over and under-estimation.
-	Can be used to assess the impact of over and under-estimation on decision-making or resource allocation.

Cons:
-	May not provide a comprehensive understanding of the overall model performance.
-	As they are independent metrics, each separated metric could ignore the instances where the model accurately predicts or underpredicts the target variable.

=== Conclusion

In our dataset, the demand for taxis varies significantly across different locations. This variation in demand makes it challenging to directly compare the Mean Absolute Error (MAE) or Root Mean Squared Error (RMSE) values between areas with low demand and those with high demand. To address this issue, it is more appropriate to use metrics such as Mean Absolute Percentage Error (MAPE) or Root Mean Squared Logarithmic Error (RMSLE). Among these metrics, MAPE is preferred as it is easier to understand and present to stakeholders due to its simplicity.

Additionally, when planning resources based on the model predictions, it is crucial to consider both overestimation and underestimation. Therefore, we will use a set of metrics consisting of MAPE, Mean Over-Prediction (MOP), and Mean Under-Prediction (MUP) for evaluating and selecting the best model.Im summary, the set of metrics: MAPE, MOP, MUP will be used for model evaluation and selection.

#align(center)[#table(
  columns: 4,
  align: (col, row) => (auto,auto,auto,auto,).at(col),
  inset: 6pt,
  text(size: 8pt, fill: blue, weight: "medium")[Pipeline], text(size: 8pt, fill: blue, weight: "medium")[CatBoost], text(size: 8pt, fill: blue, weight: "medium")[RandomForestRegressor], text(size: 8pt, fill: blue, weight: "medium")[XGBRegressor],
  [Train MAE],
  [5.103079],
  [1.953024],
  [5.10299],
  [Test MAE],
  [17.980025],
  [10.632502],
  [10.63064],
  [Train RMSE],
  [10.613764],
  [4.413968],
  [10.410122],
  [Test RMSE],
  [32.466774],
  [20.388465],
  [20.283713],
  [Train MAPE],
  [46.503349],
  [16.171341],
  [49.441491],
  [Test MAPE],
  [67.235588],
  [36.444995],
  [42.934687],
  [Train RMSLE],
  [0.373687],
  [0.15279],
  [0.38029],
  [Test RMSLE],
  [0.788658],
  [0.369841],
  [0.390765],
  [Train MOP],
  [2.571882],
  [0.994603],
  [2.551493],
  [Test MOP],
  [1.275124],
  [4.758648],
  [4.215477],
  [Train MUP],
  [-2.531197],
  [-0.958421],
  [-2.551497],
  [Test MUP],
  [-16.704901],
  [-5.873854],
  [-6.415163],
)
]

Analyzing the provided results table, we observe that the RandomForestRegressor model performs the best in terms of MAPE and MUP on the test set. This model optimizes accuracy and minimizes underestimation, which is crucial for ensuring sufficient resources are allocated to the respective areas. In this context, prioritizing customer satisfaction over profit, a relatively higher overestimation is acceptable.

Based on these considerations, we will choose the RandomForestRegressor model to predict future demand in the target area.
