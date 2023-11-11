import os

import librosa
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def find_closest_timestamp(timestamps: list, target: float):
    return np.argmin(np.abs(np.asarray(timestamps) - target))


# --------------------------------------------------------------------------- #
# Generate training and testing data
labels = pd.read_csv("bahnaric/labels.csv")

train, test = train_test_split(labels, test_size=0.2, random_state=42)


def gen_dataset(subset: pd.DataFrame, label: str) -> pd.DataFrame:
    dataset = []
    for _, row in subset.iterrows():
        # Load computed features
        file_name = row["file_name"]
        features_file_name = os.path.join(
            "bahnaric/features",
            os.path.basename(row["file_name"]).replace("TextGrid", "parquet"),
        )
        if not os.path.exists(features_file_name):
            print(f"File {features_file_name} not found")
            continue
        features = pd.read_parquet(
            features_file_name.replace("TextGrid", "parquet").replace(
                "dataset", "features"
            )
        )
        # Recreate index for features
        features.index = np.arange(len(features))

        # Set label to 0
        features[label] = 0

        # Translate marked labels from timestamp to frame index
        signal, sr = librosa.load(
            file_name.replace("TextGrid", "wav"), sr=16000
        )

        # Break audio into frames
        frame_length = int(sr * 0.005)  # 5ms
        hop_length = int(sr * 0.001)  # 1ms
        frames = librosa.util.frame(
            signal, frame_length=frame_length, hop_length=hop_length
        )

        # Calculate the timestamp of each frame
        timestamps = np.arange(frames.shape[1]) * hop_length / sr
        assert len(timestamps) == len(features)

        # label index
        label_index = find_closest_timestamp(
            timestamps=timestamps,
            target=row["start"] if label == "ov" else row["end"],
        )
        # Relax the condition by allowing the label to be within 15 frames
        label_index = np.arange(
            max(label_index - 15, 0), min(label_index + 15, len(timestamps))
        )
        features.loc[features.index[label_index], label] = 1

        # Assuming ov and op appear in the (25%) beginning and end of the timestamps
        # remove index in the middle
        if label == "ov":
            middle_index = np.arange(int(0.25 * len(features)), len(features))
        else:
            middle_index = np.arange(0, int(0.75 * len(features)))
        features = features.drop(features.index[middle_index])

        dataset.append(features)
    dataset = pd.concat(dataset)
    return dataset


# --------------------------------------------------------------------------- #
# Training

label = "op"
training_set = gen_dataset(train, label)
testing_set = gen_dataset(test, label)

X_train = training_set.drop(label, axis=1)
y_train = training_set[label]
print(X_train.shape, y_train.shape)
X_val = testing_set.drop(label, axis=1)
y_val = testing_set[label]
print(X_val.shape, y_val.shape)

lgb_train = lgb.Dataset(X_train, y_train)
lgb_val = lgb.Dataset(X_val, y_val, reference=lgb_train)

params = {
    "boosting_type": "gbdt",
    "objective": "binary",
    "metric": "auc",
    "num_leaves": 60,
    "learning_rate": 0.01,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": 0,
    "num_threads": os.cpu_count(),
}

model = lgb.train(params, lgb_train, num_boost_round=1000, valid_sets=lgb_val)

y_pred = model.predict(X_val, num_iteration=model.best_iteration)
y_pred = [
    1 if p >= 0.5 else 0 for p in y_pred
]  # convert probabilities to class labels

precision = precision_score(y_val, y_pred)
recall = recall_score(y_val, y_pred)
accuracy = accuracy_score(y_val, y_pred)

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"Accuracy: {accuracy}")
