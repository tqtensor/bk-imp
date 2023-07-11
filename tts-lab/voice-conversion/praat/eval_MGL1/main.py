import glob
import os
import tempfile

import numpy as np
import parselmouth
import soundfile as sf
from parselmouth.praat import call


def voice_conversion(
    sound_input: np.ndarray,
    sampling_rate: int,
    pitch_min: float,
    pitch_max: float,
    formant_shift_ratio: float,
    new_pitch_median: float,
    pitch_range_factor: float,
    duration_factor: float,
) -> np.ndarray:
    """
    Changes the gender of the input audio using Praat's 'Change gender' algorithm.

    Args:
        sound_input (np.ndarray): The input audio data as a NumPy array.
        sampling_rate (int): The sampling rate of the input audio.
        pitch_min (float): Minimum pitch (Hz) below which pitch candidates will not be considered.
        pitch_max (float): Maximum pitch (Hz) above which pitch candidates will be ignored.
        formant_shift_ratio (float): Ratio determining the frequencies of formants in the newly created audio.
            A ratio of 1.0 indicates no frequency shift, while 1.1 approximates female formant characteristics.
            A ratio of 1/1.1 approximates male formant characteristics.
        new_pitch_median (float): Median pitch (Hz) of the new audio. The pitch values in the new audio
            are calculated by multiplying them by new_pitch_median / old_pitch_median.
            Default: 0.0 (same as original).
        pitch_range_factor (float): Scaling factor for the new pitch values around the new pitch median.
            A factor of 1.0 implies no additional pitch modification (except for the median adjustment).
            A factor of 0.0 monotonizes the new sound to the new pitch median.
            Default: 1.0.
        duration_factor (float): Factor by which the sound will be lengthened.
            Values less than 1.0 result in a shorter sound, while values larger than 3.0 are not supported.
            Default: 1.0.

    Returns:
        np.ndarray: The processed audio data as a NumPy array with the gender changed.

    Raises:
        AssertionError: If pitch_min is greater than pitch_max or if duration_factor is larger than 3.0.
    """
    assert (
        pitch_min <= pitch_max
    ), "pitch_min should be less than or equal to pitch_max"
    assert duration_factor <= 3.0, "duration_factor cannot be larger than 3.0"

    # Save the input audio to a temporary file
    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp_file, sound_input, sampling_rate)

    # Load the source audio
    sound = parselmouth.Sound(tmp_file.name)

    # Tune the audio
    tuned_sound = call(
        sound,
        "Change gender",
        pitch_min,
        pitch_max,
        formant_shift_ratio,
        new_pitch_median,
        pitch_range_factor,
        duration_factor,
    )

    # Remove the temporary file
    tmp_file.close()
    return np.array(tuned_sound.values.T)


if __name__ == "__main__":
    if not os.path.exists(
        "tts-lab/voice-conversion/praat/eval_MGL1/generated"
    ):
        os.makedirs("tts-lab/voice-conversion/praat/eval_MGL1/generated")

    for source_file in glob.glob(
        "tts-lab/voice-conversion/praat/eval_MGL1/source/*.wav"
    ):
        sound = parselmouth.Sound(source_file).resample(new_frequency=16000)
        converted_sound = voice_conversion(
            sound_input=np.array(sound.values.T),
            sampling_rate=int(sound.sampling_frequency),
            pitch_min=75,
            pitch_max=600,
            formant_shift_ratio=1.03,
            new_pitch_median=192,
            pitch_range_factor=1.09,
            duration_factor=1.0,
        )
        sf.write(
            os.path.join(
                "tts-lab/voice-conversion/praat/eval_MGL1/generated",
                source_file.split("/")[-1],
            ),
            converted_sound,
            16000,
        )
