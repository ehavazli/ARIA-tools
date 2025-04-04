import re
from aria_tools.utils.file_ops import format_output_path

def test_format_output_path_basic(tmp_path):
    out_path = format_output_path(
        output_dir=tmp_path,
        output_type="url",
        track="004",
        bbox="36.75 37.225 -76.655 -75.928"
    )
    assert out_path.suffix == ".txt"
    assert out_path.exists() is False
    assert re.search(r"track004_bbox.*\.txt$", out_path.name)

def test_format_output_path_increment(tmp_path):
    # Simulate existing files to test incrementing
    first = format_output_path(tmp_path, "count")
    first.touch()
    second = format_output_path(tmp_path, "count")
    assert first != second
    assert second.name.endswith("_1.txt")
