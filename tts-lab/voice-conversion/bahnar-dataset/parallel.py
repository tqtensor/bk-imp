import glob
from collections import defaultdict


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

    print("Duplicate files:")
    for duplicate, speakers in duplicates.items():
        if len(speakers) == 1:
            continue
        else:
            regions = set([get_region(speaker) for speaker in speakers])

            if len(regions) == 1:
                # print("Speakers come from the same region.")
                continue
            else:
                print("Speakers come from different regions.")
                print("File name:", duplicate)
                print("Speakers:", speakers)
            print("_" * 50)
