#!/usr/bin/env python3
import sys

import click

from aria_tools.core.download import download_file, search_asf_api
from aria_tools.utils.logging_utils import setup_logger

logger = setup_logger()

@click.command()
@click.option(
    '-o', '--output', default='Download', type=click.Choice(['Download', 'Count', 'Url'], case_sensitive=False),
    help='Output type. Default="Download". Use "Url" for ingestion to aria*.py')
@click.option(
    '-t', '--track', required=True, type=str,
    help='track to download; single number (including leading zeros) or comma separated')
@click.option(
    '-b', '--bbox', required=True, type=str,
    help='Lat/Lon Bounding SNWE, or GDAL-readable file containing POLYGON geometry.')
@click.option(
    '-w', '--workdir', 'wd', default='./products', type=str,
    help='Specify directory to deposit all outputs. Default is "products" in local directory.')
@click.option(
    '-s', '--start', default='20100101', type=str,
    help='Start date as YYYYMMDD; default: 20100101.')
@click.option(
    '-e', '--end', default='21000101', type=str,
    help='End date as YYYYMMDD; default: 21000101.')
@click.option(
    '-u', '--user', default=None, type=str,
    help='NASA Earthdata URS user login. Ensure GRFN Door and ASF Datapool Products access.')
@click.option(
    '-p', '--pass', 'passw', default=None, type=str,
    help='NASA Earthdata URS password. Ensure GRFN Door and ASF Datapool Products access.')
@click.option(
    '--mission', default='S1', type=click.Choice(['S1', 'NISAR'], case_sensitive=False),
    help='Sentinel-1 (S1) or NISAR. Default is S1.')
@click.option(
    '-l', '--daysless', 'dayslt', default=999999, type=int,
    help='Take pairs with temporal baseline less than this number of days.')
@click.option(
    '-m', '--daysmore', 'daysgt', default=0, type=int,
    help='Take pairs with temporal baseline greater than this number of days.')
@click.option(
    '-nt', '--num_threads', default='1', type=str,
    help='Number of threads for multiprocessing download. "All" = all available.')
@click.option(
    '-i', '--ifg', default=None, type=str,
    help='Retrieve one interferogram by its start/end date: YYYYMMDD_YYYYMMDD.')
@click.option(
    '-d', '--direction', 'flightdir', default=None, type=str,
    help='Flight direction: ascending, a, descending, d')
@click.option(
    '--version', default=None, type=str,
    help='Specific product version to download (e.g., 2_0_4). Default = all.')
@click.option(
    '-v', '--verbose', is_flag=True,
    help='Print products to be downloaded to stdout.')
@click.option(
    '--log-level', default='info', type=str,
    help='Logger log level.')

def cli_download(track, bbox, start, end, orbit, output):
    """CLI entry for downloading ASF DAAC data."""
    results = search_asf_api(bbox, start, end, orbit)
    if results and "feed" in results and "entry" in results["feed"]:
        download_url = results["feed"]["entry"][0]["url"]
        download_file(download_url, output)
    else:
        logger.warning("No results found for the given search parameters.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_download()
    else:
        logger.warning("Usage: python ariaDownload.py --bbox <W,S,E,N> --start YYYY-MM-DD --end YYYY-MM-DD --orbit <orbit>")

