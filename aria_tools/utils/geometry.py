import logging
from pathlib import Path
from typing import Optional, Union

import fiona
import shapely.geometry

logger = logging.getLogger(__name__)


def open_shp(shp_path: str) -> shapely.geometry.Polygon:
    """
    Read the first polygon geometry from a shapefile.

    Parameters
    ----------
    shp_path : str
        Path to the shapefile

    Returns
    -------
    Polygon
        Shapely polygon extracted from the first feature

    Raises
    ------
    Exception if the file cannot be read or does not contain a polygon.
    """
    path = Path(shp_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Shapefile not found: {shp_path}")

    with fiona.open(path, "r") as src:
        feature = next(iter(src))
        geom = shapely.geometry.shape(feature["geometry"])

        if not isinstance(geom, shapely.geometry.Polygon):
            raise ValueError(f"Geometry is not a Polygon: {geom.geom_type}")

        logger.debug("Loaded polygon from shapefile: %s", shp_path)
        return geom


def make_bbox(inp_bbox: Optional[str]) -> Optional[shapely.geometry.Polygon]:
    """
    Converts a bounding box string or shapefile path into a Shapely Polygon.
    """
    if inp_bbox is None:
        return None

    path = Path(inp_bbox).expanduser().resolve()

    if path.exists():
        return _parse_shapefile(path)

    return _parse_snwe_string(inp_bbox)


def _parse_shapefile(path: Union[str, Path]) -> shapely.geometry.Polygon:
    try:
        geom = open_shp(str(path))
        if not isinstance(geom, shapely.geometry.Polygon):
            raise ValueError(f"Expected Polygon geometry, got {type(geom)}")
        logger.info("Loaded polygon from shapefile: %s", path)
        return geom
    except Exception as e:
        raise ValueError(f"Failed to read polygon from shapefile: {path}") from e


def _parse_snwe_string(bbox_str: str) -> shapely.geometry.Polygon:
    try:
        S, N, W, E = [float(x) for x in bbox_str.strip().split()]
    except Exception:
        raise ValueError(
            f"Could not parse SNWE coordinates from string: '{bbox_str}'. "
            f"Expected format: 'S N W E'"
        )

    # Fix coordinate conventions
    if W > 180:
        W -= 360
        logger.info("Adjusted west longitude > 180 to degrees west.")

    if E > 180:
        E -= 360
        logger.info("Adjusted east longitude > 180 to degrees west.")

    if N <= S or E <= W:
        raise ValueError(f"Invalid bounding box: S={S}, N={N}, W={W}, E={E}")

    return shapely.geometry.Polygon([(W, N), (W, S), (E, S), (E, N)])
