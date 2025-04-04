from datetime import datetime

from aria_tools.utils.date_filters import (
    parse_ifg_dates,
    match_specific_ifg,
    match_date_window,
)


def test_parse_ifg_dates_s1():
    ifg = "20200101_20200201"
    is_nisar = False
    end, start = parse_ifg_dates(ifg, is_nisar)
    assert start == datetime(2020, 2, 1)
    assert end == datetime(2020, 1, 1)


def test_match_specific_ifg_match():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 2, 1)
    assert match_specific_ifg(start, end, "20200101_20200201")


def test_match_specific_ifg_no_match():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 2, 1)
    assert not match_specific_ifg(start, end, "20200101_20200301")


def test_match_date_window_in_range():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 2, 1)
    date_start = datetime(2019, 12, 1)
    date_end = datetime(2020, 12, 1)
    assert match_date_window(start, end, date_start, date_end, 10, 40)


def test_match_date_window_out_of_range_date():
    start = datetime(2018, 1, 1)
    end = datetime(2018, 2, 1)
    date_start = datetime(2019, 1, 1)
    date_end = datetime(2020, 1, 1)
    assert not match_date_window(start, end, date_start, date_end, 10, 40)


def test_match_date_window_out_of_range_baseline():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 6, 1)
    date_start = datetime(2019, 1, 1)
    date_end = datetime(2021, 1, 1)
    assert not match_date_window(start, end, date_start, date_end, 10, 60)
