import os

from dotenv import load_dotenv
from minio import Minio

import tempfile
import ffmpeg
import shutil
import wave
import webrtcvad


import re

# Load environment variables from .env file
load_dotenv()


def generate_voice_clips(input_file, output_folder, clip_duration):
    # Normalize the input file name for creating clip names
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    base_name = re.sub(r"\W+", "", base_name.lower())

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
                num_frames_processed * sample_width : frame_end * sample_width
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
            print(f"Voice clip generated: {clip_file}")

            # Update the start frame for the next iteration
            start_frame = end_frame
            clip_count += 1
        else:
            print("No voice activity found in the input file.")
            break

    # Clean up
    os.remove


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
            print(f"File downloaded: {local_file_path}")

            # Perform any necessary operations with the downloaded file
            audio_output_path = "tts-lab/vtv5/audio/{}.wav".format(
                obj.object_name.replace(".mp4", "")
            )

            # Convert audio format using ffmpeg
            (
                ffmpeg.input(local_file_path)
                .output(audio_output_path, format="wav", ar=8000, ac=1)
                .run(cmd="/home/terrabot/ffmpeg/ffmpeg", overwrite_output=True)
            )
            print(f"Audio saved as: {audio_output_path}")
            return audio_output_path
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    ## Download audio files from MinIO ##
    # Configure MinIO client
    minio_client = Minio(
        "11.11.1.100:9000",
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False,  # Change to True if you're using SSL/TLS
    )

    # Create the output folder if it doesn't exist
    if not os.path.exists("tts-lab/vtv5/audio"):
        os.makedirs("tts-lab/vtv5/audio")
    if not os.path.exists("tts-lab/vtv5/audio/voice_clips"):
        os.makedirs("tts-lab/vtv5/audio/voice_clips")
    else:
        shutil.rmtree("tts-lab/vtv5/audio/voice_clips")
        os.makedirs("tts-lab/vtv5/audio/voice_clips")

    bucket_name = "tts-lab"
    objects = minio_client.list_objects(bucket_name, recursive=True)

    for obj in objects:
        audio_output_path = convert_audio_format(obj=obj)
        generate_voice_clips(
            audio_output_path, "tts-lab/vtv5/audio/voice_clips", 15
        )
