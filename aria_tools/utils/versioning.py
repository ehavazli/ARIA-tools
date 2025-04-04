import logging
import os
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


def url_versions(urls: List[str], version: Optional[str], workdir: str) -> List[str]:
    """
    Filter ASF product URLs to only those that match a given version string.

    Parameters
    ----------
    urls : list of str
        ASF product URLs
    version : str or None
        Version string to match, e.g., "2_0_4"
    workdir : str
        Directory to save filtered URL list (log/debugging)

    Returns
    -------
    list of str
        Filtered URLs matching version, or all if version is None
    """
    if version is None:
        return urls

    logger.info("Filtering products by version: %s", version)
    matched_urls = []
    pattern = re.compile(rf"_v{re.escape(version)}_\d{{8}}T\d{{6}}")

    for url in urls:
        if pattern.search(url):
            matched_urls.append(url)

    out_path = os.path.join(workdir, f"filtered_versions_{version}.txt")
    try:
        with open(out_path, "w") as f:
            for u in matched_urls:
                f.write(u + "\n")
        logger.debug("Wrote filtered URLs to %s", out_path)
    except Exception as e:
        logger.warning("Could not write version log file: %s", e)

    logger.info(
        "Filtered %d products matching version '%s'.", len(matched_urls), version
    )
    return matched_urls
