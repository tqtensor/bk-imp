import constants as c
import librosa
import numpy as np
import pandas as pd


def extract_mfcc_feature_means(
    audio_file_name: str,
    signal: np.ndarray,
    sample_rate: int,
    number_of_mfcc: int,
) -> pd.DataFrame:
    mfcc_alt = librosa.feature.mfcc(
        y=signal, sr=sample_rate, n_mfcc=number_of_mfcc
    )
    delta = librosa.feature.delta(mfcc_alt)
    accelerate = librosa.feature.delta(mfcc_alt, order=2)

    mfcc_features = {
        "file_name": audio_file_name,
    }

    for i in range(0, number_of_mfcc):
        # MFCC coefficient
        key_name = "".join(["mfcc", str(i)])
        mfcc_value = np.mean(mfcc_alt[i])
        mfcc_features.update({key_name: mfcc_value})

        # MFCC delta coefficient
        key_name = "".join(["mfcc_delta_", str(i)])
        mfcc_value = np.mean(delta[i])
        mfcc_features.update({key_name: mfcc_value})

        # MFCC accelerate coefficient
        key_name = "".join(["mfcc_accelerate_", str(i)])
        mfcc_value = np.mean(accelerate[i])
        mfcc_features.update({key_name: mfcc_value})

    df = pd.DataFrame.from_records(data=[mfcc_features])
    return df


def extract_feature_means(audio_file_path: str) -> pd.DataFrame:
    # Config settings
    number_of_mfcc = c.NUMBER_OF_MFCC

    # 1. Importing 1 file
    y, sr = librosa.load(audio_file_path)

    # Trim leading and trailing silence from an audio signal (silence before
    # and after the actual audio)
    signal, _ = librosa.effects.trim(y)

    # 2. Fourier Transform
    n_fft = c.NUMBER_FFT  # FFT window size
    hop_length = (
        c.HOP_LENGTH
    )  # number audio of frames between STFT columns (looks like a good default)

    # Short-time Fourier transform (STFT)
    d_audio = np.abs(
        librosa.stft(y=signal, n_fft=n_fft, hop_length=hop_length)
    )

    # 3. Spectrogram
    db_audio = librosa.amplitude_to_db(S=d_audio, ref=np.max)

    # 4. Create the Mel Spectrograms
    s_audio = librosa.feature.melspectrogram(y=signal, sr=sr)
    s_db_audio = librosa.amplitude_to_db(s_audio, ref=np.max)

    # 5. Zero crossings

    # 6. Harmonics and Perceptrual
    y_harm, y_perc = librosa.effects.hpss(signal)

    # 7. Spectral Centroid
    spectral_centroids = librosa.feature.spectral_centroid(y=signal, sr=sr)[0]
    spectral_centroids_delta = librosa.feature.delta(spectral_centroids)
    spectral_centroids_accelerate = librosa.feature.delta(
        spectral_centroids, order=2
    )

    # 8. Chroma Frequencies
    hop_length = c.HOP_LENGTH
    chromagram = librosa.feature.chroma_stft(
        y=signal, sr=sr, hop_length=hop_length
    )

    # 9. Tempo BPM (beats per minute)
    tempo_y, _ = librosa.beat.beat_track(y=signal, sr=sr)

    # 10. Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y=signal, sr=sr)[0]
    onset_env = librosa.onset.onset_strength(y=signal, sr=sr)

    # 11. Spectral Bandwidth
    spectral_bandwidth_2 = librosa.feature.spectral_bandwidth(y=signal, sr=sr)[
        0
    ]
    spectral_bandwidth_3 = librosa.feature.spectral_bandwidth(
        y=signal, sr=sr, p=3
    )[0]
    spectral_bandwidth_4 = librosa.feature.spectral_bandwidth(
        y=signal, sr=sr, p=4
    )[0]

    audio_features = {
        "file_name": audio_file_path,
        "zero_crossing_rate": np.mean(
            librosa.feature.zero_crossing_rate(signal)[0]
        ),
        "zero_crossings": np.sum(librosa.zero_crossings(signal, pad=False)),
        "spectrogram": np.mean(db_audio[0]),
        "mel_spectrogram": np.mean(s_db_audio[0]),
        "harmonics": np.mean(y_harm),
        "perceptual_shock_wave": np.mean(y_perc),
        "spectral_centroids": np.mean(spectral_centroids),
        "spectral_centroids_delta": np.mean(spectral_centroids_delta),
        "spectral_centroids_accelerate": np.mean(
            spectral_centroids_accelerate
        ),
        "chroma1": np.mean(chromagram[0]),
        "chroma2": np.mean(chromagram[1]),
        "chroma3": np.mean(chromagram[2]),
        "chroma4": np.mean(chromagram[3]),
        "chroma5": np.mean(chromagram[4]),
        "chroma6": np.mean(chromagram[5]),
        "chroma7": np.mean(chromagram[6]),
        "chroma8": np.mean(chromagram[7]),
        "chroma9": np.mean(chromagram[8]),
        "chroma10": np.mean(chromagram[9]),
        "chroma11": np.mean(chromagram[10]),
        "chroma12": np.mean(chromagram[11]),
        "tempo_bpm": tempo_y,
        "spectral_rolloff": np.mean(spectral_rolloff),
        "spectral_flux": np.mean(onset_env),
        "spectral_bandwidth_2": np.mean(spectral_bandwidth_2),
        "spectral_bandwidth_3": np.mean(spectral_bandwidth_3),
        "spectral_bandwidth_4": np.mean(spectral_bandwidth_4),
    }

    # Extract MFCC feature
    mfcc_df = extract_mfcc_feature_means(
        audio_file_path, signal, sample_rate=sr, number_of_mfcc=number_of_mfcc
    )

    df = pd.DataFrame.from_records(data=[audio_features])
    df = pd.merge(df, mfcc_df, on="file_name")
    return df
