import os
import re
import shutil
import tempfile
import wave
from unicodedata import normalize

import ffmpeg
import librosa
import numpy as np
import webrtcvad
from dotenv import load_dotenv
from minio import Minio
from tqdm.auto import tqdm

# Load environment variables from .env file
load_dotenv()

ENGERY_THRESHOLD = 500  # energy threshold for voice activity detection
CLIP_DURATION = 5  # seconds
SAMPLE_RATE = 16000


def check_audio_threshold(audio_path: str, threshold: float) -> bool:
    # Load audio file
    audio, _ = librosa.load(audio_path, sr=None)

    # Calculate energy using squared signal
    energy = np.sum(np.square(audio))

    # Check if all frames are above the threshold
    is_above_threshold = energy > threshold
    return is_above_threshold


def generate_voice_clips(
    input_file: str, output_folder: str, clip_duration: int
) -> bool:
    try:
        # Normalize the input file name for creating clip names
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        base_name = re.sub(r"\W+", "", base_name.lower())
        base_name = (
            normalize("NFKD", base_name).encode("ascii", "ignore").decode()
        )

        # Open the input wave file
        with wave.open(input_file, "rb") as wav:
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            num_frames = wav.getnframes()
            pcm_data = wav.readframes(num_frames)

        # Initialize the WebRTC VAD
        vad = webrtcvad.Vad()
        vad.set_mode(
            3
        )  # Set the aggressiveness level of the VAD (0 to 3, 3 being the most aggressive)

        # Calculate the number of frames for the desired clip duration
        clip_frames = int(sample_rate * clip_duration)

        # Set the frame duration for the VAD
        frame_duration = 10  # ms
        frame_size = int(
            sample_rate * frame_duration / 1000
        )  # Convert frame duration to samples

        # Find voice activity and generate voice clips
        start_frame = 0
        clip_count = 1
        while start_frame < num_frames:
            # Find the start frame of the voice activity
            end_frame = min(start_frame + clip_frames, num_frames)
            num_frames_processed = start_frame
            while num_frames_processed < end_frame:
                frame_end = min(num_frames_processed + frame_size, end_frame)
                frame = pcm_data[
                    num_frames_processed
                    * sample_width : frame_end
                    * sample_width
                ]
                if vad.is_speech(frame, sample_rate):
                    start_frame = num_frames_processed
                    break
                num_frames_processed += frame_size

            # Check if voice activity is found
            if start_frame is not None:
                # Calculate the end frame based on the clip duration
                end_frame = min(start_frame + clip_frames, num_frames)

                # Extract the voice clip data
                clip_data = pcm_data[
                    start_frame * sample_width : end_frame * sample_width
                ]

                # Write the voice clip to the output file
                clip_file = os.path.join(
                    output_folder, f"{base_name}_{clip_count:03d}.wav"
                )
                with wave.open(clip_file, "wb") as wav_out:
                    wav_out.setparams(
                        (
                            1,
                            sample_width,
                            sample_rate,
                            len(clip_data),
                            "NONE",
                            "not compressed",
                        )
                    )
                    wav_out.writeframes(clip_data)

                # Check if the clip is above the energy threshold
                if not check_audio_threshold(clip_file, ENGERY_THRESHOLD):
                    os.remove(clip_file)
                    print(
                        f"Voice clip {clip_count} is below the energy threshold. Removing..."
                    )

                # Update the start frame for the next iteration
                start_frame = end_frame
                clip_count += 1
            else:
                print("No voice activity found in the input file.")
                break
        return True
    except Exception as ex:
        print(ex)
        return False
    finally:
        # Clean up
        os.remove(input_file)


def convert_audio_format(obj) -> str:
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as temp_file:
            local_file_path = temp_file.name

            # Download the file to the temporary file
            minio_client.fget_object(
                bucket_name, obj.object_name, local_file_path
            )

            # Perform any necessary operations with the downloaded file
            audio_output_path = (
                "tts-lab/voice-conversion/bk-dataset/{}.wav".format(
                    "/".join(
                        obj.object_name.replace(".wav", "").split("/")[-2:]
                    )
                )
            )

            # Convert audio format using ffmpeg
            (
                ffmpeg.input(local_file_path)
                .output(
                    audio_output_path,
                    format="wav",
                    ar=SAMPLE_RATE,
                    ac=1,
                    af="afftdn=nr=10:nf=-40,dynaudnorm=p=0.95",
                )
                .run(
                    cmd=os.path.join(os.path.expanduser("~"), "ffmpeg/ffmpeg"),
                    overwrite_output=True,
                    quiet=True,
                )
            )
            return audio_output_path
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    # Download audio files from MinIO #
    # Configure MinIO client
    minio_client = Minio(
        "remote.tqtensor.com:9000",
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False,  # Change to True if you're using SSL/TLS
    )

    for source in ["binh_dinh_male", "binh_dinh_female", "kon_tum_male"]:
        # Create the output folder if it doesn't exist
        voice_clips_path = os.path.join(
            "tts-lab/voice-conversion/bk-dataset", source
        )
        if not os.path.exists(voice_clips_path):
            os.makedirs(voice_clips_path)
        else:
            shutil.rmtree(voice_clips_path)
            os.makedirs(voice_clips_path)

        bucket_name = "bk-imp"
        objects = minio_client.list_objects(
            bucket_name,
            prefix=os.path.join("tts-lab/recordings", source),
            recursive=True,
        )
        objects = [obj for obj in objects if obj.object_name.endswith(".wav")]

        for obj in tqdm(
            objects, total=len(objects), desc="Generating voice clips"
        ):
            if os.path.exists(
                "tts-lab/voice-conversion/bk-dataset/voice-clips.txt"
            ):
                processed_objects = (
                    open(
                        "tts-lab/voice-conversion/bk-dataset/voice-clips.txt",
                        "r",
                    )
                    .read()
                    .splitlines()
                )
            else:
                processed_objects = []

            if obj.object_name.replace(".wav", "") not in processed_objects:
                audio_output_path = convert_audio_format(obj=obj)
                successful = generate_voice_clips(
                    audio_output_path,
                    f"tts-lab/voice-conversion/bk-dataset/{source}",
                    CLIP_DURATION,
                )
                if successful:
                    with open(
                        "tts-lab/voice-conversion/bk-dataset/voice-clips.txt",
                        "a",
                    ) as f:
                        f.write(
                            "{}\n".format(obj.object_name.replace(".wav", ""))
                        )
