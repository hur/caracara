#!/usr/bin/env python3
r"""Caracara Examples Collection.

update_iocs.py

This example will use the API credentials configured in your config.yml file to
update the example IOC created by create_ioc.py within your Falcon tenant. 

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
def update_ioc(**kwargs):
    """Example of updating the IOC created by examples/create_ioc.py"""
    client: Client = kwargs["client"]
    logger: logging.Logger = kwargs["logger"]

    filters = client.FalconFilter(dialect="iocs")
    filters.create_new_filter("type", "domain")
    filters.create_new_filter("value", "example.com")

    if filters.filters:
        logger.info("Getting a list of IOCs that match the FQL string %s", filters.get_fql())
    else:
        logger.info("No filter provided; getting a list of all IOCs within the tenant")

    iocs = client.ioc.describe_iocs(filters)

    if iocs:
        logger.info("Updating matching IOCs")

    for ioc in iocs:
        if ioc.description == "Caracara Example IOC":
            ioc.description += "; modified by caracara examples/update_ioc.py"
    
    with client:
        response = client.ioc.update_batch(iocs)
    for ioc_data in response:
        logger.info("%s", pretty_print(ioc_data.dump()))


if __name__ in ["__main__", "examples.ioc.find_iocs"]:
    try:
        update_ioc()
        raise SystemExit
    except NoIocsFound as no_iocs:
        raise SystemExit(no_iocs) from no_iocs
