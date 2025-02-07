#!/usr/bin/env python3
r"""Caracara Examples Collection.

delete_ioc.py

This example will use the API credentials configured in your config.yml file to
find a specified device within your Falcon tenant. When no search is provided, all
IOCs are returned.

The example demonstrates how to use the IOC API.
"""
import logging

from caracara import Client
from examples.common import (
    NoIocsFound,
    caracara_example,
    pretty_print,
)


@caracara_example
def delete_ioc(**kwargs):
    """Delete an IOC."""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    filters = client.FalconFilter(dialect="iocs")
    filters.create_new_filter("type", "domain")
    filters.create_new_filter("value", "example.com")

    with client:
        iocs = client.ioc.describe_iocs(filters)
        response = client.ioc.delete(
            iocs, comment="Caracara Examples/delete_ioc.py"
        )

    logger.info("%s", pretty_print(response))


if __name__ in ["__main__", "examples.ioc.delete_ioc"]:
    try:
        delete_ioc()
        raise SystemExit
    except NoIocsFound as no_iocs:
        raise SystemExit(no_iocs) from no_iocs
