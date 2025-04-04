import logging
import math
import os
import re
from pathlib import Path
from typing import Optional

from shapely.geometry import Polygon

from aria_tools.utils.geometry import make_bbox

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory: str) -> None:
    """Ensures the specified directory exists."""
    os.makedirs(directory, exist_ok=True)


def get_filename_from_url(url: str) -> str:
    """Extracts the filename from a given URL."""
    return os.path.basename(url)


def format_output_path(
    output_dir: str,
    output_type: str,
    track: Optional[str] = None,
    bbox: Optional[str] = None,
    extension_override: Optional[str] = None,
) -> Path:
    """
    Generate a unique output file path based on track, bbox, and output type.

    Parameters
    ----------
    output_dir : str
        Directory to save the file.
    output_type : str
        One of: 'Download', 'Count', 'Url', 'Kml'
    track : str, optional
        Comma-separated string of track numbers (e.g. '004,077')
    bbox : str, optional
        Bounding box string (SNWE) or shapefile path
    extension_override : str, optional
        Force file extension (e.g. '.json'). If None, inferred from output_type.

    Returns
    -------
    pathlib.Path
        Full path to a unique output file.
    """
    base_path = Path(output_dir).resolve()
    base_path.mkdir(parents=True, exist_ok=True)

    ext = extension_override or (".kmz" if output_type.lower() == "kml" else ".txt")

    parts = []

    if track:
        track_slug = re.sub(r"[^\w\-]", "_", track.replace(",", "-"))
        parts.append(f"track{track_slug}")

    if bbox:
        bbox_slug = _format_bbox_slug(bbox)
        if bbox_slug:
            parts.append(f"bbox{bbox_slug}")

    base_name = "_".join(parts) if parts else "output"
    filename = f"{base_name}{ext}"
    dst = base_path / filename

    count = 1
    while dst.exists():
        dst = base_path / f"{base_name}_{count}{ext}"
        count += 1

    logger.info(f"Saving output to: {dst}")
    return dst


def _format_bbox_slug(bbox_input: str) -> Optional[str]:
    """
    Generate a safe slug from bounding box input.

    Returns
    -------
    str or None
    """
    try:
        poly: Polygon = make_bbox(bbox_input)
        W, S, E, N = poly.bounds

        # Standard formatting: W/S round down, E/N round up
        return f"{math.floor(W)}W{math.floor(S)}S{math.ceil(E)}E{math.ceil(N)}N"
    except Exception as e:
        logger.warning(f"Could not parse bbox input: {bbox_input} ({e})")
        return None
