import os

def ensure_directory_exists(directory):
    """Ensures the specified directory exists."""
    os.makedirs(directory, exist_ok=True)

def get_filename_from_url(url):
    """Extracts the filename from a given URL."""
    return os.path.basename(url)

