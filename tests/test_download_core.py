import pytest
from unittest.mock import patch, MagicMock
from aria_tools.core.download import Downloader


@pytest.fixture
def config_dict(sample_config):
    # Extend sample_config to use known state
    sample_config.update({
        "output": "count",
        "start": "20200101",
        "end": "20200201",
        "baseline_range": [0, 100],
    })
    return sample_config


def test_downloader_initialization(config_dict):
    downloader = Downloader(config_dict)
    assert downloader.cfg["output"] == "count"
    assert downloader.cfg["daysgt"] == 0
    assert downloader.cfg["dayslt"] == 999999


@patch("aria_tools.core.download.Downloader.query_asf")
@patch("aria_tools.core.download.parse_asf_results")
def test_downloader_run_count_mode(mock_parse, mock_query, config_dict):
    mock_query.return_value = ["mock_scene1", "mock_scene2"]
    mock_parse.return_value = (
        ["mock_scene1", "mock_scene2"],
        ["20200101_20200115", "20200115_20200201"],
        False,
    )
    config_dict["output"] = "count"

    downloader = Downloader(config_dict)
    downloader.filter_by_version = lambda urls: urls  # skip version filtering
    downloader.filter_scenes = lambda s, u, i, _: (s, u, i)

    downloader.run()


@patch("aria_tools.core.download.Downloader.query_asf")
@patch("aria_tools.core.download.parse_asf_results")
@patch("aria_tools.core.download.Downloader.write_urls")
def test_downloader_run_url_mode(mock_write, mock_parse, mock_query, config_dict):
    mock_query.return_value = ["mock_scene"]
    mock_parse.return_value = (["mock_scene"], ["20200101_20200201"], False)
    config_dict["output"] = "url"

    downloader = Downloader(config_dict)
    downloader.filter_by_version = lambda urls: urls
    downloader.filter_scenes = lambda s, u, i, _: (s, u, i)

    downloader.run()
    mock_write.assert_called_once()


@patch("aria_tools.core.download.Downloader.query_asf")
@patch("aria_tools.core.download.parse_asf_results")
@patch("aria_tools.core.download.Downloader.download_scenes")
def test_downloader_run_download_mode(mock_download, mock_parse, mock_query, config_dict):
    mock_query.return_value = ["mock_scene"]
    mock_parse.return_value = (["mock_scene"], ["20200101_20200201"], False)
    config_dict["output"] = "download"

    downloader = Downloader(config_dict)
    downloader.filter_by_version = lambda urls: urls
    downloader.filter_scenes = lambda s, u, i, _: (s, u, i)

    downloader.run()
    mock_download.assert_called_once()
