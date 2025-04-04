import pytest
from shapely.geometry import Polygon
from aria_tools.utils.geometry import make_bbox

def test_make_bbox_snwe_string():
    bbox_str = "36.75 37.225 -76.655 -75.928"
    poly = make_bbox(bbox_str)
    assert isinstance(poly, Polygon)
    assert len(poly.exterior.coords) >= 4
