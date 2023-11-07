import os

import librosa
import numpy as np
import pandas as pd
import parselmouth
from acoustic_features import extract_feature_means
from praatio.utilities import textgrid_io

# --------------------------------------------------------------------------- #
# Generate acoustic features

# file_path = "bahnaric/dataset/pham/KT_Bana_F1_part2_pham_2_pham.wav"
# signal, sr = librosa.load(file_path, sr=16000)

# feature_dfs = []
# for k in range(10):
#     # Define window size
#     k = 75 + (1 + k) * 10
#     assert k % 2 == 1, "k must be odd"

#     # Break audio into frames
#     frame_length = int(sr * 0.005)  # 5ms
#     hop_length = int(sr * 0.001)  # 1ms
#     print(f"Frame length: {frame_length}, hop length: {hop_length}")
#     frames = librosa.util.frame(
#         signal, frame_length=frame_length, hop_length=hop_length
#     )
#     print(f"Frames shape: {frames.shape}")

#     # Calculate the timestamp of each frame
#     timestamps = np.arange(frames.shape[1]) * hop_length / sr
#     print(f"Timestamps shape: {timestamps.shape}")

#     # Pad frames at the beginning and end
#     padding = (k - 1) // 2
#     padded_frames = np.pad(frames, ((0, 0), (padding, padding)), mode="edge")

#     # Calculate features on sliding window of k frames
#     features = []
#     for i in range(padding, len(padded_frames[0]) - padding):
#         window = padded_frames[:, i - padding : i + padding + 1]
#         feature = extract_feature_means(signal=window.flatten(), sr=sr)
#         features.append(feature)

#     features = pd.concat(features, axis=0)
#     features.columns = [
#         f"{col}_w{str(k).zfill(3)}" for col in features.columns
#     ]
#     feature_dfs.append(features)

# features = pd.concat(feature_dfs, axis=1)
# print(features.head())

# --------------------------------------------------------------------------- #
# Parse TextGrid

textgrid_data = parselmouth.Data.read(
    "/home/terrabot/bk-imp/tts-lab/phoneme-segmentation/bahnaric/dataset/pham/KT_Bana_F1_part1_pham_2_pham.TextGrid"
)
textgrid_data.save_as_text_file("/tmp/textgrid.txt")

textgrid_data = textgrid_io.parseTextgridStr(
    open("/tmp/textgrid.txt", "r").read(), includeEmptyIntervals=False
)
