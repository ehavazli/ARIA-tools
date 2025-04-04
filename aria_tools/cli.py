import datetime
import logging

import click

from aria_tools.core.download import Downloader
from aria_tools.utils.config_loader import load_config_file, merge_config
from aria_tools.utils.log import FORMAT as LOG_FORMAT


def validate_dates(config):
    try:
        config["start"] = datetime.datetime.strptime(config["start"], "%Y%m%d")
        config["end"] = datetime.datetime.strptime(config["end"], "%Y%m%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

    if config["start"] > config["end"]:
        raise ValueError(
            f"Start date {config['start']} is after end date {config['end']}."
        )


def normalize_baseline_range(config):
    if config.get("baseline_range"):
        config["daysgt"], config["dayslt"] = config["baseline_range"]

    if config.get("daysgt") is None:
        config["daysgt"] = 0
    if config.get("dayslt") is None:
        config["dayslt"] = 999999


@click.group()
def cli():
    """ARIA-tools CLI"""
    pass


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Path to config file (.yml, .json, .toml)",
)
@click.option("--track", "-t", type=str, help="Track numbers (comma-separated)")
@click.option("--bbox", "-b", type=str, help="Bounding box (SNWE) or shapefile path")
@click.option(
    "--mission", type=click.Choice(["S1", "NISAR"]), default="S1", show_default=True
)
@click.option("--start", "-s", type=str, help="Start date (YYYYMMDD)")
@click.option("--end", "-e", type=str, help="End date (YYYYMMDD)")
@click.option("--ifg", "-i", type=str, help="Specific IFG name to download")
@click.option(
    "--baseline-range",
    nargs=2,
    type=int,
    metavar=("MIN", "MAX"),
    help="Min and max IFG days",
)
@click.option(
    "--flightdir", "-d", type=str, help="Flight direction: ascending / descending"
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["download", "count", "url"]),
    default="download",
)
@click.option(
    "--workdir",
    "-w",
    type=str,
    default="./products",
    show_default=True,
    help="Working/output directory",
)
@click.option("--version", type=str, help="Product version filter")
@click.option("--num_threads", "-nt", type=str, default="1")
@click.option("--user", "-u", type=str, help="Earthdata username")
@click.option("--passw", "-p", type=str, help="Earthdata password")
@click.option("--verbose", "-v", is_flag=True)
@click.option("--log-level", default="info", help="Log level: debug/info/warning/error")
def download(**kwargs):
    """Download Sentinel-1/NISAR GUNW products from ASF"""
    config_file = kwargs.pop("config", None)
    file_config = load_config_file(config_file) if config_file else {}
    config = merge_config(file_config, kwargs)

    log_level = getattr(logging, config.get("log_level", "info").upper(), logging.INFO)
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    if config.get("verbose"):
        logging.getLogger().setLevel(logging.DEBUG)

    if (
        not config.get("track")
        and not config.get("bbox")
        and config.get("mission") != "NISAR"
    ):
        raise click.UsageError(
            "You must provide --track or --bbox unless mission is NISAR"
        )

    validate_dates(config)
    normalize_baseline_range(config)

    downloader = Downloader(config)
    downloader.run()
