import logging
from datetime import datetime
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_ifg_dates(ifg_id: str, is_nisar: bool) -> Tuple[datetime, datetime]:
    """
    Parse interferogram start/end dates from an IFG ID.

    Parameters
    ----------
    ifg_id : str
        Interferogram ID (e.g., '20180712_20180724' or Sentinel-1 style)
    is_nisar : bool
        Whether this is a NISAR-formatted product

    Returns
    -------
    (end, start) : Tuple[datetime, datetime]
        Parsed datetime objects for start and end dates

    Raises
    ------
    ValueError
        If the date string is malformed
    """
    try:
        dates = ifg_id.split("_")
        if is_nisar:
            start = datetime.strptime(dates[0], "%Y%m%d")
            end = datetime.strptime(dates[1], "%Y%m%d")
        else:
            end = datetime.strptime(dates[0], "%Y%m%d")
            start = datetime.strptime(dates[1], "%Y%m%d")
        return end, start
    except Exception as e:
        raise ValueError(f"Failed to parse IFG ID '{ifg_id}': {e}") from e


def match_specific_ifg(start: datetime, end: datetime, ifg_query: str) -> bool:
    """
    Match an IFG against a specific query (e.g., from --ifg arg)

    Parameters
    ----------
    start : datetime
        Start date of the IFG
    end : datetime
        End date of the IFG
    ifg_query : str
        IFG string to match, in format 'YYYYMMDD_YYYYMMDD'

    Returns
    -------
    bool
        Whether the IFG matches the query exactly (order-insensitive)
    """
    try:
        dates = sorted(
            datetime.strptime(d, "%Y%m%d").date() for d in ifg_query.split("_")
        )
        return dates[0] == start.date() and dates[1] == end.date()
    except Exception as e:
        logger.warning(f"Could not parse --ifg value '{ifg_query}': {e}")
        return False


def match_date_window(
    start: datetime,
    end: datetime,
    window_start: datetime,
    window_end: datetime,
    days_gt: int,
    days_lt: int,
) -> bool:
    """
    Check if the IFG falls within a given date window and baseline range.

    Parameters
    ----------
    start : datetime
    end : datetime
    window_start : datetime
    window_end : datetime
    days_gt : int
        Minimum days between IFG start and end
    days_lt : int
        Maximum days between IFG start and end

    Returns
    -------
    bool
        True if IFG is within temporal bounds
    """
    valid_range = window_start <= start and end <= window_end
    delta_days = (end - start).days
    valid_duration = days_gt <= delta_days <= days_lt
    return valid_range and valid_duration
