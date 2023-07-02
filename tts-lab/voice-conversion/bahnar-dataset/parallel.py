import glob
import os
import shutil
from collections import defaultdict

import numpy as np
import soundfile as sf


def get_region(speaker_name: str):
    return speaker_name[-2:]


if __name__ == "__main__":
    # Detect duplicate files by name
    file_paths = glob.glob(
        "tts-lab/voice-conversion/bahnar-dataset/cleaned/*/*"
    )
    file_names = [file_path.split("/")[-1] for file_path in file_paths]

    duplicates = defaultdict(list)

    for file_path in file_paths:
        file_name = file_path.split("/")[-1]
        speaker = file_path.split("/")[-2]
        duplicates[file_name].append(speaker)

    if not os.path.exists("tts-lab/voice-conversion/bahnar-dataset/parallel"):
        os.makedirs("tts-lab/voice-conversion/bahnar-dataset/parallel")

    print("Duplicate files:")
    for duplicate, speakers in duplicates.items():
        if len(speakers) == 1:
            continue
        else:
            print("File name:", duplicate)
            print("Speakers:", speakers)
            lengths = []

            for speaker in speakers:
                file_path = f"tts-lab/voice-conversion/bahnar-dataset/cleaned/{speaker}/{duplicate}"
                audio, sample_rate = sf.read(file_path)
                duration = len(audio) / sample_rate
                lengths.append(duration)

            max_length = max(lengths)
            min_length = min(lengths)
            threshold = 3  # Threshold of 3 seconds

            if max_length - min_length > threshold:
                print(
                    "Skipped due to abnormal duration difference among speakers."
                )
                print("_" * 50)
                continue

            for i, speaker in enumerate(speakers):
                if not os.path.exists(
                    f"tts-lab/voice-conversion/bahnar-dataset/parallel/{speaker}"
                ):
                    os.makedirs(
                        f"tts-lab/voice-conversion/bahnar-dataset/parallel/{speaker}"
                    )
                shutil.copy(
                    f"tts-lab/voice-conversion/bahnar-dataset/cleaned/{speaker}/{duplicate}",
                    f"tts-lab/voice-conversion/bahnar-dataset/parallel/{speaker}/{duplicate}",
                )
        print("_" * 50)
