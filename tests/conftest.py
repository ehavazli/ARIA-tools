import pytest
from datetime import datetime


@pytest.fixture
def sample_config():
    """
    Minimal config dictionary for downloader tests.
    Can be extended as needed for specific cases.
    """
    return {
        "mission": "S1",
        "track": "004",
        "bbox": "36.75 37.225 -76.655 -75.928",
        "start": "20190101",
        "end": "20190201",
        "output": "Count",
        "wd": "./products",
        "version": None,
        "num_threads": "1",
        "user": None,
        "passw": None,
        "verbose": False,
        "log_level": "info",
        "ifg": None,
        "baseline_range": None,
        "flightdir": None,
    }
