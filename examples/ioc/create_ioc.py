#!/usr/bin/env python3
r"""Caracara Examples Collection.

create_ioc.py

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. When no search is provided, all
IOCs are returned.

The example demonstrates how to use the IOC API.
"""
import logging
from typing import Dict, List

from caracara import Client
from caracara.modules.ioc.ioc import IOC
from examples.common import (
    NoIocsFound,
    Timer,
    caracara_example,
    parse_filter_list,
    pretty_print,
)


@caracara_example
def create_ioc(**kwargs):
    """Create a new IOC."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]
    settings: Dict = kwargs["settings"]
    timer: Timer = Timer()

    ioc = IOC(
        type="domain", 
        value="example.com",
        action="no_action", 
        description="Caracara Example IOC",
        applied_globally=True,
        platforms=["linux"],
    )

    with client:
        response = client.ioc.create(
            ioc, 
            comment="Caracara Example IOC creation", 
            retrodetects=False, 
            ignore_warnings=False
        )

    logger.info("%s", pretty_print(response.dump()))



if __name__ in ["__main__", "examples.ioc.create_ioc"]:
    try:
        create_ioc()
        raise SystemExit
    except NoIocsFound as no_iocs:
        raise SystemExit(no_iocs) from no_iocs
