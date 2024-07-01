import os
import gdown
import pandas as pd
from glob import glob


# Function to download files from Google Drive
def download_files_from_gdrive(folder_url="https://drive.google.com/drive/folders/1Z1rhdOypBQJgUC_ohV2iNj0RMGt8DgJv?usp=sharing"):
    os.makedirs("stockSenseData", exist_ok=True)
    gdown.download_folder(folder_url, quiet=False, output="stockSenseData")


