import os

from dotenv import load_dotenv
from minio import Minio
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Configure MinIO client
minio_client = Minio(
    "11.11.1.100:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False,  # Change to True if you're using SSL/TLS
)

# Directory path containing the files to upload
directory_path = "tts-lab/crawler/vtv5"

# Name of the bucket in MinIO
bucket_name = "tts-lab"

# Upload files to MinIO

# Create the bucket if it doesn't exist
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

# Get the list of files in the directory
file_names = [
    file_name
    for file_name in os.listdir(directory_path)
    if file_name.endswith(".mp4")
]

# Iterate over the files and upload them
for file_name in tqdm(
    file_names, total=len(file_names), desc="Uploading files"
):
    file_path = os.path.join(directory_path, file_name)

    try:
        # Upload the file to the bucket
        minio_client.fput_object(bucket_name, file_name, file_path)
    except Exception as ex:
        print(f"Error occurred while uploading files: {ex}")

print("Files uploaded successfully!")
