#!/usr/bin/env python3
# ARIA-tools Downloader Core Logic
# =============================================================================

import concurrent.futures
import getpass
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import asf_search
import tqdm
from requests.exceptions import RequestException

from aria_tools.utils.date_filters import (
    match_date_window,
    match_specific_ifg,
    parse_ifg_dates,
)
from aria_tools.utils.file_ops import format_output_path
from aria_tools.utils.geometry import make_bbox
from aria_tools.utils.parsing import parse_asf_results
from aria_tools.utils.versioning import url_versions

logger = logging.getLogger(__name__)


class Downloader:
    """
    Download ASF GUNW products using user-supplied configuration.

    Supports both Sentinel-1 and NISAR missions and performs search,
    filtering, and download using the ASF API and Earthdata credentials.
    """

    def __init__(self, config: Dict):
        """Initialize the downloader with user configuration."""
        self.cfg = self._validate_and_normalize_config(config)

    def _validate_and_normalize_config(self, cfg: Dict) -> Dict:
        """Clean up and normalize configuration values."""
        cfg["output"] = str(cfg.get("output", "download")).lower()
        cfg["wd"] = str(Path(cfg.get("wd", "./products")).resolve())
        Path(cfg["wd"]).mkdir(parents=True, exist_ok=True)

        cfg["start"] = self._parse_date(cfg.get("start", "20100101"))
        cfg["end"] = self._parse_date(cfg.get("end", "21000101"))

        cfg["daysgt"] = int(cfg.get("daysgt") or 0)
        cfg["dayslt"] = int(cfg.get("dayslt") or 999999)

        cfg["verbose"] = bool(cfg.get("verbose", False))
        cfg["num_threads"] = str(cfg.get("num_threads", "1"))

        cfg["mission"] = str(cfg.get("mission", "S1")).upper()
        if cfg["mission"] not in {"S1", "NISAR"}:
            raise ValueError(f"Unsupported mission: {cfg['mission']}")

        logger.setLevel(logging.DEBUG if cfg["verbose"] else logging.INFO)
        return cfg

    @staticmethod
    def _parse_date(val):
        if isinstance(val, datetime):
            return val
        return datetime.strptime(val, "%Y%m%d")

    def run(self):
        """Main entry point: query, filter, and process data."""
        logger.info("Starting ASF query")

        scenes = self.query_asf()
        urls, ifgs, is_nisar = parse_asf_results(scenes)

        scenes, urls, ifgs = self.filter_scenes(scenes, urls, ifgs, is_nisar)

        count = len(scenes)
        logger.info("Found %d matching products.", count)

        if logger.isEnabledFor(logging.DEBUG):
            for url in urls:
                logger.debug("Match: %s", url)

        if self.cfg["output"] == "count":
            pass

        elif self.cfg["output"] == "url":
            logger.info("Writing %d product URLs to file.", count)
            self.write_urls(urls)

        elif self.cfg["output"] == "download":
            logger.info("Prepared to download %d files.", count)
            self.download_scenes(scenes)

    def query_asf(self):
        """Query ASF for scenes using spatial and temporal filters."""
        bbox = make_bbox(self.cfg.get("bbox"))
        bbox_wkt = bbox.wkt if bbox else None

        direction = self.cfg.get("flightdir")
        if direction:
            direction = (
                "ascending" if direction.lower().startswith("a") else "descending"
            )

        tracks = (
            [int(t) for t in self.cfg["track"].split(",")]
            if self.cfg.get("track")
            else None
        )

        start = self.cfg["start"] - timedelta(days=1)
        end = self.cfg["end"] + timedelta(days=1)

        logger.debug("Searching ASF archive with parameters:")
        logger.debug("  Flight Direction: %s", direction)
        logger.debug("  Start date: %s", start)
        logger.debug("  End date: %s", end)
        logger.debug("  Tracks: %s", tracks)
        logger.debug("  Bbox: %s", bbox_wkt)

        if self.cfg["mission"] == "S1":
            return asf_search.geo_search(
                collections=["C2859376221-ASF", "C1261881077-ASF"],
                dataset=asf_search.constants.ARIA_S1_GUNW,
                processingLevel=asf_search.constants.GUNW_STD,
                relativeOrbit=tracks,
                flightDirection=direction,
                intersectsWith=bbox_wkt,
                start=start,
                end=end,
            )

        session = asf_search.ASFSession()
        session.auth_with_token(getpass.getpass("EDL Token:"))
        logger.info("Authenticated with EDL token.")

        opts = asf_search.ASFSearchOptions(
            shortName="NISAR_L2_GUNW_BETA_V1",
            intersectsWith=bbox_wkt,
            start=start,
            end=end,
            session=session,
        )
        return asf_search.search(opts=opts, maxResults=250)

    def filter_scenes(self, scenes, urls, ifgs, is_nisar):
        """
        Filter scenes by version and date/ifg in a single pass.
        """
        logger.info("Filtering returned scene list by version and date range")
        filtered = []
        versioned_urls = set(url_versions(urls, self.cfg["version"],
                                          self.cfg["wd"]))

        for scene, url, ifg in zip(scenes, urls, ifgs):
            if url not in versioned_urls:
                continue

            end, start = parse_ifg_dates(ifg, is_nisar)

            if self.cfg.get("ifg"):
                if not match_specific_ifg(start, end, self.cfg["ifg"]):
                    continue
            elif not match_date_window(start, end, self.cfg["start"],
                                       self.cfg["end"], self.cfg["daysgt"],
                                       self.cfg["dayslt"]):
                continue

            filtered.append((scene, url, ifg))

        if not filtered:
            logger.warning("No scenes matched filtering criteria.")

        return zip(*filtered) if filtered else ([], [], [])

    def write_urls(self, urls: List[str]):
        """Save the list of filtered URLs to a text file."""
        dst = format_output_path(
            output_dir=self.cfg["wd"],
            output_type=self.cfg["output"],
            track=self.cfg.get("track"),
            bbox=self.cfg.get("bbox"),
        )
        with open(dst, "w") as f:
            for url in urls:
                f.write(f"{url}\n")
        logger.info("Saved %d product URLs to %s", len(urls), dst)

    def download_scenes(self, scenes):
        """Download product files in parallel using threads."""
        scenes = asf_search.ASFSearchResults(scenes)
        session = asf_search.ASFSession()

        if self.cfg.get("user"):
            session.auth_with_creds(self.cfg["user"], self.cfg["passw"])

        num_threads = (
            os.cpu_count()
            if self.cfg["num_threads"].lower() == "all"
            else int(self.cfg["num_threads"])
        )
        logger.info("Starting download with %d threads", num_threads)

        urls = [s.properties["url"] for s in scenes]

        pbar = tqdm.tqdm(
            total=len(urls),
            unit="file",
            desc="Downloading",
        )

        success_count = 0
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_threads
        ) as executor:
            futures = [
                executor.submit(self._download_file, session, url, pbar)
                for url in urls
            ]
            for f in concurrent.futures.as_completed(futures):
                if f.result():
                    success_count += 1

        pbar.close()
        logger.info(
            "Downloaded %d of %d files to: %s",
            success_count,
            len(scenes),
            self.cfg["wd"],
        )

    def _download_file(
        self,
        session,
        url,
        pbar,
        max_retries: int = 3,
        retry_delay: int = 5,
    ) -> Optional[str]:
        """Download a single file with retry logic and integrity check."""
        filename = Path(url).name
        filepath = Path(self.cfg["wd"]) / filename

        if filepath.exists():
            logger.info("Skipped existing file: %s", filepath)
            pbar.update(1)
            return str(filepath)

        for attempt in range(max_retries):
            try:
                response = session.get(url, stream=True)
                response.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(8192):
                        if chunk:
                            f.write(chunk)

                expected = int(response.headers.get("Content-Length", 0))
                actual = filepath.stat().st_size
                if expected and actual < expected:
                    logger.warning(
                        "Incomplete download: %s (%d/%d bytes)",
                        filepath,
                        actual,
                        expected,
                    )
                    filepath.unlink(missing_ok=True)
                    time.sleep(retry_delay)
                    continue

                pbar.update(1)
                return str(filepath)

            except RequestException as e:
                logger.error("Error downloading %s: %s", url, e)
                time.sleep(retry_delay)

        logger.error("Failed to download after retries: %s", url)
        return None
