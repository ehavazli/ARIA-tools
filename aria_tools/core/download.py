import requests
from aria_tools.utils.file_operations import ensure_directory_exists, get_filename_from_url
from aria_tools.utils.logging_utils import setup_logger

logger = setup_logger()

ASF_API_URL = "https://api.daac.asf.alaska.edu/services/search/param"

def search_asf_api(bbox, start_date, end_date, orbit):
    """Search ASF DAAC API for GUNW products."""
    params = {
        "platform": "Sentinel-1",
        "processingLevel": "GUNW",
        "intersectsWith": bbox,
        "start": start_date,
        "end": end_date,
        "relativeOrbit": orbit,
        "output": "json"
    }
    
    logger.info(f"Searching ASF DAAC API with parameters: {params}")
    response = requests.get(ASF_API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"API request failed with status {response.status_code}")
        return None

def download_file(url, output_dir="."):
    """Downloads a file from ASF DAAC to the output directory."""
    ensure_directory_exists(output_dir)
    filename = get_filename_from_url(url)
    filepath = f"{output_dir}/{filename}"

    logger.info(f"Downloading from {url} to {filepath}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        logger.info(f"Download complete: {filepath}")
        return filepath
    else:
        logger.error(f"Failed to download {url}. HTTP Status {response.status_code}")
        return None

