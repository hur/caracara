#!/usr/bin/env python3
r"""Caracara Examples Collection.

find_iocs.py

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. When no search is provided, all
IOCs are returned.

The example demonstrates how to use the IOC API.
"""
import logging
from typing import Dict, List

from caracara import Client
from examples.common import (
    NoIocsFound,
    Timer,
    caracara_example,
    parse_filter_list,
    pretty_print,
)


@caracara_example
def find_iocs(**kwargs):
    """Find IOCS matching a filter (default: type=domain)."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    settings: Dict = kwargs["settings"]
    timer: Timer = Timer()

    filters = client.FalconFilter(dialect="iocs")
    if "filters" in settings:
        filter_list: List[Dict] = settings["filters"]
        parse_filter_list(filter_list, filters)

    if filters.filters:
        logger.info("Getting a list of IOCs that match the FQL string %s", filters.get_fql())
    else:
        logger.info("No filter provided; getting a list of all IOCs within the tenant")

    with client:
        response = client.ioc.describe_iocs(filters)
    for ioc_data in response:
        logger.info("%s", pretty_print(ioc_data.dump()))

    logger.info("Found %d IOCs in %f seconds", len(response), float(timer))
    if not response:
        raise NoIocsFound(filters.get_fql())


if __name__ in ["__main__", "examples.ioc.find_iocs"]:
    try:
        find_iocs()
        raise SystemExit
    except NoIocsFound as no_iocs:
        raise SystemExit(no_iocs) from no_iocs
