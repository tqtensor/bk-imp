import itertools
import json
import math
import multiprocessing
import os
import tempfile

import numpy as np
import parselmouth
import soundfile as sf
from parselmouth.praat import call
from pymcd.mcd import Calculate_MCD
from tqdm.auto import tqdm

mcd_toolbox = Calculate_MCD(MCD_mode="dtw")
sampling_frequency = 16000


def change_gender(
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

    return (
        np.array(tuned_sound.values.T),
        formant_shift_ratio,
        new_pitch_median,
        pitch_range_factor,
    )


def change_gender_wrapper(args):
    # Unpack the arguments
    sound_input, sampling_frequency, *params = args

    # Call the change_gender function with the reconstructed sound object and other parameters
    tuned_audio = change_gender(sound_input, sampling_frequency, *params)

    return tuned_audio


def calculate_mcd_distance(args):
    ref_file, target_file, params = args
    mcd = mcd_toolbox.calculate_mcd(ref_file, target_file)

    return mcd, params


if __name__ == "__main__":
    # Generate the pitch candidates
    num_candidates = 10000
    num_steps = np.ceil(math.pow(num_candidates, 1 / 3))
    formant_shift_ratio = (1.0, 1.3)
    new_pitch_median = (180, 220)
    pitch_range_factor = (1.0, 1.3)
    x = 0

    for param in [
        "formant_shift_ratio",
        "new_pitch_median",
        "pitch_range_factor",
    ]:
        x = eval(param)
        x = list(np.arange(x[0], x[1], (x[1] - x[0]) / num_steps))
        exec(f"{param} = x")

    # Default params
    pitch_min = [75]
    pitch_max = [600]
    duration_factor = [1]

    # Generate the search space
    search_space = list(
        itertools.product(
            *[
                pitch_min,
                pitch_max,
                formant_shift_ratio,
                new_pitch_median,
                pitch_range_factor,
                duration_factor,
            ]
        )
    )

    # Generate training data
    training_data = {}
    training_data = json.load(
        open("tts-lab/voice-conversion/praat/parallel_voices.json", "r")
    )

    for source, target in training_data.items():
        source = os.path.join(
            "tts-lab/voice-conversion/bahnar-dataset", source
        )
        target = os.path.join(
            "tts-lab/voice-conversion/bahnar-dataset", target
        )
        # Load the source audio
        source_audio = parselmouth.Sound(source).resample(
            new_frequency=sampling_frequency
        )

        # Prepare the arguments for the change_gender function
        args = [
            (
                np.array(source_audio.values.T),
                int(source_audio.sampling_frequency),
                *params,
            )
            for params in search_space
        ]

        pool = multiprocessing.Pool(
            processes=max(1, multiprocessing.cpu_count() - 2)
        )

        # Use tqdm to track the progress of multiprocessing
        tuned_voices = []
        with tqdm(total=len(args), desc="Processing") as pbar:
            # Use multiprocessing imap to apply the change_gender function to each combination
            for result in pool.imap(change_gender_wrapper, args):
                tuned_voices.append(result)
                pbar.update()

        # Close the pool of worker processes
        pool.close()
        pool.join()

        print(f"Finished processing {source}")

        # Load the target voice recording
        target_audio = parselmouth.Sound(target).resample(
            new_frequency=sampling_frequency
        )
        target_tmp_file = tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ).name
        target_audio.save(target_tmp_file, "WAV")

        # Prepare the arguments for MCD calculation
        args = []
        for i in range(len(tuned_voices)):
            audio, *params = tuned_voices[i]
            tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp_file.name, audio, sampling_frequency)
            args.append((target_tmp_file, tmp_file.name, params))

        pool = multiprocessing.Pool(
            processes=max(1, multiprocessing.cpu_count() - 2)
        )

        # Use tqdm to track the progress of multiprocessing
        mcd_distances = []
        with tqdm(total=len(args), desc="Processing") as pbar:
            # Use multiprocessing imap to apply the calculate_mcd_distance function to each argument
            for result in pool.imap(calculate_mcd_distance, args):
                mcd_distances.append(result)
                pbar.update()

        # Close the pool of worker processes
        pool.close()
        pool.join()

        # Find the minimum MCD and its corresponding parameters
        min_mcd = float("inf")
        best_params = None
        for mcd, params in mcd_distances:
            if mcd < min_mcd:
                min_mcd = mcd
                best_params = params

        # Print the minimum MCD and its corresponding parameters
        print("Minimum MCD: {}".format(min_mcd))
        print("Best parameters: {}".format(best_params))

        # Persist the best parameters
        if not os.path.exists("tts-lab/voice-conversion/praat/params.json"):
            with open("tts-lab/voice-conversion/praat/params.json", "w") as f:
                json.dump({"dummy": "dummy"}, f)
        else:
            with open("tts-lab/voice-conversion/praat/params.json", "r") as f:
                params = json.load(f)
            params[target.split("/")[-2] + "_" + target.split("/")[-1]] = {
                "min_mcd": min_mcd,
                "params": best_params,
            }
            with open("tts-lab/voice-conversion/praat/params.json", "w") as f:
                json.dump(params, f)

        # Save the generated voice
        sound = parselmouth.Sound(source).resample(
            new_frequency=sampling_frequency
        )

        # Tune according to min MCD params
        tuned_audio, *params = change_gender(
            np.array(sound.values.T),
            sampling_frequency,
            75,
            600,
            *best_params,
            1,
        )

        # Save the tuned audio
        if not os.path.exists("tts-lab/voice-conversion/praat/generated"):
            os.makedirs("tts-lab/voice-conversion/praat/generated")
        sf.write(
            "tts-lab/voice-conversion/praat/generated/{}".format(
                target.split("/")[-2] + "_" + target.split("/")[-1]
            ),
            tuned_audio,
            sampling_frequency,
        )
