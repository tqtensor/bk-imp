import os

import ffmpeg
import numpy as np
from dtw import dtw
from librosa.feature import mfcc
from pydub import AudioSegment
from tqdm.auto import tqdm

SAMPLE_RATE = 41000


def preprocess_audio(file_path):
    # Convert audio format using ffmpeg
    (
        ffmpeg.input(file_path)
        .output(
            file_path.lower().replace(".wav", "_processed.wav"),
            format="wav",
            ar=SAMPLE_RATE,
            ac=1,
            af="afftdn=nr=10:nf=-40,dynaudnorm=p=0.95",
        )
        .run(
            cmd=os.path.join(os.path.expanduser("~"), "ffmpeg/ffmpeg"),
            overwrite_output=True,
            quiet=False,
        )
    )
    return file_path.lower().replace(".wav", "_processed.wav")


def extract_mfcc(audio_data, sample_rate):
    # Convert audio data to floating-point format
    audio_data = audio_data.astype(np.float32)

    # Extract MFCC features from audio data
    mfcc_features = mfcc(y=audio_data, sr=sample_rate)
    return mfcc_features


def break_into_sentences(audio_file, sound_marker):
    # Load the audio file
    sound = AudioSegment.from_file(audio_file)
    sound_data = np.array(sound.get_array_of_samples())
    sample_rate = sound.frame_rate

    # Convert the sound marker to numpy array
    marker_data = np.array(sound_marker.get_array_of_samples())

    # Extract MFCC features from the sound marker
    marker_mfcc = extract_mfcc(marker_data, sample_rate)

    # Calculate distances between the marker and each chunk of audio
    sentences, distances = [], []
    for i in tqdm(range(len(sound))):
        chunk_data = np.asarray(sound_data[i : i + len(marker_data)])
        if len(chunk_data) < len(marker_data):
            break
        chunk_mfcc = extract_mfcc(chunk_data, sample_rate)

        # Calculate the distance between the marker MFCC and chunk MFCC
        alignment = dtw(marker_mfcc, chunk_mfcc, distance_only=True)
        distance = alignment.distance
        distances.append(distance)

        if distance < 2750:  # Adjust this threshold as needed
            sentence = sound_data[i : i + len(marker_data)]
            sentences.append(sentence)

    print(min(distances), max(distances), np.mean(distances))
    return sentences


# Example usage
audio_file = "tts-lab/voice-conversion/bk-dataset/kon_tum_male/kh-cn_bai_3.wav"
sound_marker_file = (
    "tts-lab/voice-conversion/bk-dataset/kon_tum_male/KTM1_end_marker.wav"
)

audio_file = preprocess_audio(audio_file)
sound_marker_file = preprocess_audio(sound_marker_file)

sound_marker = AudioSegment.from_wav(sound_marker_file)
sentences = break_into_sentences(audio_file, sound_marker)
for i, sentence in enumerate(sentences):
    sentence.export(f"sentence_{i}.wav", format="wav")
