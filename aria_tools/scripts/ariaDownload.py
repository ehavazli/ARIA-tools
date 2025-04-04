#!/usr/bin/env python3
"""
Legacy CLI entry point for ARIA-tools download. Supports both CLI flags and config file input.
"""

import argparse
import datetime
import logging
from typing import Dict

from aria_tools.core.download import Downloader
from aria_tools.utils import log as log_util
from aria_tools.utils.config_loader import load_config_file, merge_config


def create_parser():
    parser = argparse.ArgumentParser(
        description="Download Sentinel-1/NISAR GUNW products from ASF.",
        epilog="Examples:\n"
        "  ariaDownload.py --track 004 --output Count\n"
        '  ariaDownload.py --bbox "36.75 37.225 -76.655 -75.928"\n'
        "  ariaDownload.py --config config.yml",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Config file
    config_grp = parser.add_argument_group("Configuration file")
    config_grp.add_argument(
        "--config", "-c", type=str, help="Path to YAML, JSON, or TOML config file."
    )

    # Filtering options
    io_grp = parser.add_argument_group("Scene filtering")
    io_grp.add_argument(
        "-t", "--track", type=str, help="Track number(s), comma-separated."
    )
    io_grp.add_argument(
        "-b", "--bbox", type=str, help="Bounding box (SNWE) or shapefile path."
    )
    io_grp.add_argument(
        "--mission",
        default="S1",
        type=str.upper,
        choices=("S1", "NISAR"),
        help="Mission type. Default=S1",
    )
    io_grp.add_argument(
        "-s", "--start", type=str, default="20100101", help="Start date (YYYYMMDD)."
    )
    io_grp.add_argument(
        "-e", "--end", type=str, default="21000101", help="End date (YYYYMMDD)."
    )
    io_grp.add_argument(
        "-i", "--ifg", type=str, help="Specific IFG to match: YYYYMMDD_YYYYMMDD"
    )
    io_grp.add_argument(
        "--baseline-range",
        nargs=2,
        type=int,
        metavar=("MIN", "MAX"),
        help="Min and max baseline duration in days. "
        "Example: --baseline-range 12 48.",
    )
    # Deprecated
    io_grp.add_argument(
        "-l",
        "--daysless",
        dest="dayslt",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    io_grp.add_argument(
        "-m",
        "--daysmore",
        dest="daysgt",
        type=int,
        default=None,
        help=argparse.SUPPRESS,
    )
    io_grp.add_argument(
        "-d",
        "--direction",
        dest="flightdir",
        type=str,
        help="Flight direction: a/ascending or d/descending.",
    )

    # Output & control
    out_grp = parser.add_argument_group("Output options")
    out_grp.add_argument(
        "-o",
        "--output",
        default="Download",
        type=str.title,
        choices=("Download", "Count", "Url"),
        help="Output mode.",
    )
    out_grp.add_argument(
        "-w",
        "--workdir",
        dest="wd",
        default="./products",
        type=str,
        help="Directory to write output to.",
    )
    out_grp.add_argument(
        "-nt",
        "--num_threads",
        default="1",
        type=str,
        help='Thread count or "All". Default=1.',
    )
    out_grp.add_argument(
        "--version", type=str, help="Product version filter (e.g., 2_0_4)."
    )

    # Auth
    auth_grp = parser.add_argument_group("Authentication")
    auth_grp.add_argument(
        "-u", "--user", type=str, help="NASA Earthdata Login username."
    )
    auth_grp.add_argument(
        "-p", "--pass", dest="passw", type=str, help="NASA Earthdata password."
    )

    # Logging
    log_grp = parser.add_argument_group("Logging")
    log_grp.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    log_grp.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Logging level. Default=info.",
    )

    return parser


def parse_dates_or_fail(config: Dict):
    try:
        config["start"] = datetime.datetime.strptime(config["start"], "%Y%m%d")
        config["end"] = datetime.datetime.strptime(config["end"], "%Y%m%d")
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")
    if config["start"] > config["end"]:
        raise ValueError(
            f"Start date {config['start']} is after end date {config['end']}."
        )


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Load config file if provided
    file_config = load_config_file(args.config) if args.config else {}
    cli_args = vars(args)
    config = merge_config(file_config, cli_args)

    # Setup logging
    log_level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }.get(config.get("log_level", "info").lower(), logging.INFO)
    logging.basicConfig(level=log_level, format=log_util.FORMAT)

    # Required input validation
    if (
        not config.get("track")
        and not config.get("bbox")
        and config.get("mission") != "NISAR"
    ):
        raise ValueError(
            "You must specify either --track or --bbox unless using --mission NISAR."
        )

    # Dates
    parse_dates_or_fail(config)

    # Handle baseline range
    if "baseline_range" in config and config["baseline_range"]:
        config["daysgt"], config["dayslt"] = config["baseline_range"]

    # Backward compatibility: old options
    if config.get("dayslt") is not None or config.get("daysgt") is not None:
        if "baseline_range" in config and config["baseline_range"]:
            logging.warning(
                "Both --baseline-range and deprecated --daysmore/less used. "
                "--baseline-range takes precedence."
            )
        else:
            logging.warning(
                "The options --daysmore and --daysless are deprecated. "
                "Use --baseline-range instead."
            )

    # Fallback defaults
    if "daysgt" not in config:
        config["daysgt"] = 0
    if "dayslt" not in config:
        config["dayslt"] = 999999

    # Run
    downloader = Downloader(config)
    downloader.run()


if __name__ == "__main__":
    main()
