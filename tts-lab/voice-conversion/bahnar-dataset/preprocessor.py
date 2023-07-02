import glob
import os
import re
import shutil
import zipfile

from pydub import AudioSegment, effects

SAMPLING_RATE = 24000


def standardize_audio(audio_path: str, target_sr: int = 16000):
    try:
        # Load the audio using PyDub
        rawsound = AudioSegment.from_file(audio_path, "wav")

        # Convert to mono using PyDub
        mono_sound = rawsound.set_channels(1)

        # Resample using PyDub
        resampled_sound = mono_sound.set_frame_rate(target_sr)

        # Normalize using PyDub
        normalized_sound = effects.normalize(resampled_sound)

        # Export the normalized audio using PyDub
        normalized_sound.export(audio_path, format="wav")
    except Exception as e:
        print(e)
        print(audio_path)
        os.remove(audio_path)


def extract_cleaned_strings(input_string: str):
    alpha_pattern = r"[a-zA-Z]"
    digit_pattern = r"\d"

    cleaned_alpha = "".join(re.findall(alpha_pattern, input_string))
    cleaned_digits = "".join(re.findall(digit_pattern, input_string))

    return cleaned_alpha, cleaned_digits


if __name__ == "__main__":
    for speaker in ["MGL1", "FGL1", "MBD1", "FBD1"]:
        # Unzip the files
        with zipfile.ZipFile(
            f"tts-lab/voice-conversion/bahnar-dataset/raw/{speaker}.zip", "r"
        ) as zip_ref:
            zip_ref.extractall(
                f"tts-lab/voice-conversion/bahnar-dataset/raw/{speaker}"
            )

        if not os.path.exists(
            f"tts-lab/voice-conversion/bahnar-dataset/cleaned/{speaker}"
        ):
            os.makedirs(
                f"tts-lab/voice-conversion/bahnar-dataset/cleaned/{speaker}"
            )

        for file_path in glob.glob(
            f"tts-lab/voice-conversion/bahnar-dataset/raw/{speaker}/*/*/*/*"
        ):
            try:
                # Move the file to the cleaned directory
                components = file_path.split("/")
                prefix = components[-2]
                suffix = components[-1].replace("-", "_")

                cleaned_alpha, cleaned_digits = extract_cleaned_strings(prefix)
                prefix = cleaned_alpha.upper() + "_" + cleaned_digits

                if "wav" not in suffix:
                    file_index = suffix.split("_")[-1]
                elif len(components[-1].split(".")) == 2:
                    file_index = suffix.split(".")[0].split("_")[-1]
                suffix = str(int(file_index)).zfill(4) + ".wav"

                new_file_path = f"tts-lab/voice-conversion/bahnar-dataset/cleaned/{speaker}/{prefix}_{suffix}"
                shutil.move(file_path, new_file_path)

                # Standardize the audio
                standardize_audio(new_file_path, SAMPLING_RATE)
            except Exception as e:
                print(e)
                print(file_path)
                os.remove(file_path)
