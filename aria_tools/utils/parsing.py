import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def parse_asf_results(scenes) -> Tuple[List[str], List[str], bool]:
    """
    Extract URLs and interferogram pair names from ASF scenes.

    Parameters
    ----------
    scenes : List[asf_search.ASFProduct]
        List of search result scenes from ASF API.

    Returns
    -------
    urls : List[str]
        Direct product URLs.
    ifgs : List[str]
        Interferogram pair names.
    is_nisar_file : bool
        True if these are NISAR GUNW products.
    """
    urls = []
    ifgs = []
    is_nisar_file = False

    for scene in scenes:
        props = scene.geojson().get("properties", {})

        url = props.get("url")
        file_id = props.get("fileID", "")

        if not url or not file_id:
            logger.warning("Missing URL or fileID in scene metadata.")
            continue

        urls.append(url)

        if file_id.startswith("NISAR_"):
            # NISAR pair name format from fileID
            parts = file_id.split("_")
            if len(parts) >= 14:
                pairname = f"{parts[11][:8]}_{parts[13][:8]}"
            else:
                logger.warning(f"Unexpected NISAR fileID format: {file_id}")
                pairname = "unknown"
            is_nisar_file = True
        else:
            # Sentinel-1: Extract from dash-separated fileID
            parts = file_id.split("-")
            if len(parts) >= 7:
                pairname = parts[6]
            else:
                logger.warning(f"Unexpected Sentinel-1 fileID format: {file_id}")
                pairname = "unknown"

        ifgs.append(pairname)

    return urls, ifgs, is_nisar_file
