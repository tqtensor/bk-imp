import os
import shutil
import zipfile

import gdown

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Download the Bahnaric dataset
if not os.path.exists("bahnaric.zip"):
    gdown.download(
        "https://drive.google.com/uc?id=19VZ4LLKih0DiyjIecy8ROAv3fsDw6Qs9",
        "bahnaric.zip",
    )

# Unzip the ZIP file
with zipfile.ZipFile("bahnaric.zip", "r") as zip_file:
    zip_file.extractall()
if os.path.exists("bahnaric/dataset/Bana_1321_1650"):
    shutil.rmtree("bahnaric/dataset/Bana_1321_1650")
shutil.move("Bana_1321_1650", "bahnaric/dataset")
