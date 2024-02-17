import os

import gdown

# Change to current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Dataset:
    def __init__(self, dataset: str) -> None:
        if dataset == "ds-1000":
            if not os.path.exists("ds-1000"):
                os.makedirs("ds-1000")

                # Download dataset
                gdown.download(
                    id="1sR0Bl4pVHCe9UltBVyhloE8Reztn72VD",
                    output="ds-1000.zip",
                    quiet=False,
                )
                os.system("unzip ds-1000.zip -d ds-1000")
                os.system("rm ds-1000.zip")
        else:
            raise ValueError("Invalid dataset name")
