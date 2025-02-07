"""Unit tests for CustomIoaApiModule"""

import copy
import secrets
from typing import List
from unittest.mock import MagicMock

import attrs
import falconpy
import pytest

from caracara import Client
from caracara.modules.ioc.indicator import IOC
# We have to disable redefined-outer-name, as pytest fixtures break this linting check by design.
# pylint: disable=redefined-outer-name

# We also have to disabled redefined builtins, so we can mock falconpy functions that also redefine
# builtins
# pylint: disable=redefined-builtin


@pytest.fixture
def client():
    """Pytest fixture that provides a client with a mocked OAuth2 object, so no API credentials
    are needed.
    """
    auth = MagicMock(spec=falconpy.OAuth2, autospec=True)
    client = Client(falconpy_authobject=auth)
    return client


@pytest.fixture
def ioc_api(client):
    """Pytest fixture that provides a mocked `falconpy.CustomIOA` and applies to the `client` Pytest
    fixture as well."""
    ioc_api = MagicMock(autospec=falconpy.IOC)
    client.ioc.ioc_api = ioc_api
    return ioc_api

# Common mock functions

def mock_api_returns_ioc():
    return lambda **kwargs: {
        "body": {
            "resources": [mock_clouded_ioc()], 
            "errors": [],
            "meta": {"pagination": {"total": 1}}
        }
    }

def mock_api_returns_id():
    return lambda **kwargs: {
        "body": {
            "resources": [mock_clouded_ioc()["id"]], 
            "errors": [],
            "meta": {"pagination": {"total": 1}}
        }
    }

mock_clouded_ioc_type = "domain"
mock_clouded_ioc_value = "example.local"
mock_clouded_ioc_platforms = ["windows", "linux", "mac"]
mock_clouded_ioc_action = "detect"
mock_clouded_ioc_mobile_action = "no_action"
mock_clouded_ioc_tags = ["unit_test"]
mock_clouded_ioc_description = "unit testing mock"
mock_clouded_ioc_severity = "informational"
mock_clouded_ioc_host_groups = ["3f6b6cf07eed9ae5a194fdf356e9ef81"]
mock_clouded_ioc_applied_globally = False
mock_clouded_ioc_expiration = "2099-01-01T01:01:01Z"
mock_clouded_ioc_source = "unit testing"

def mock_clouded_ioc():
    return {
        "id": "42a404f15cb45a2963092ed7054b94990eb1a5e88bfc4e06773832ca0db72361",
        "type": mock_clouded_ioc_type,
        "value": mock_clouded_ioc_value,
        "platforms": mock_clouded_ioc_platforms,
        "action": mock_clouded_ioc_action,
        "mobile_action": mock_clouded_ioc_mobile_action,
        "metadata": {},
        "tags": mock_clouded_ioc_tags,
        "host_groups": mock_clouded_ioc_host_groups,
        "severity": mock_clouded_ioc_severity,
        "description": mock_clouded_ioc_description,
        "expired": False,
        "expiration": mock_clouded_ioc_expiration,
        "deleted": "False",
        "applied_globally": mock_clouded_ioc_applied_globally,
        "from_parent": False,
        "created_on": "2025-02-06T12:00:00Z",
        "created_by": "example.user@example.local",
        "modified_on": "2025-02-06T12:00:01Z",
        "modified_by": "example.user@example.local",
        "source": mock_clouded_ioc_source,
    }


def test_ioc_cannot_modify_readonly_fields():
    ioc = IOC._from_api_response(mock_clouded_ioc())
    for field in [
        "id", "expired", "deleted", "from_parent", "parent_cid_name", 
        "created_on", "created_by", "modified_on", "modified_by"
    ]:
         with pytest.raises(attrs.exceptions.FrozenAttributeError):
            setattr(ioc, field, "new_value")


def test_module_create_ioc(client: Client, ioc_api: falconpy.IOC):

    ioc_api.indicator_create.side_effect = mock_api_returns_ioc()

    iocs = client.ioc.create(
        type=mock_clouded_ioc_type,
        action=mock_clouded_ioc_action,
        value=mock_clouded_ioc_value,
        description=mock_clouded_ioc_description,
        platforms=mock_clouded_ioc_platforms,
        mobile_action = mock_clouded_ioc_mobile_action,
        tags=mock_clouded_ioc_tags,
        severity=mock_clouded_ioc_severity,
        host_group=mock_clouded_ioc_host_groups,
        applied_globally=mock_clouded_ioc_applied_globally,
        expiration=mock_clouded_ioc_expiration,
        source=mock_clouded_ioc_source,
    )

    ioc_api.indicator_create.assert_called_once_with(
        type=mock_clouded_ioc_type,
        action=mock_clouded_ioc_action,
        value=mock_clouded_ioc_value,
        description=mock_clouded_ioc_description,
        platforms=mock_clouded_ioc_platforms,
        mobile_action = mock_clouded_ioc_mobile_action,
        tags=mock_clouded_ioc_tags,
        severity=mock_clouded_ioc_severity,
        host_group=mock_clouded_ioc_host_groups,
        applied_globally=mock_clouded_ioc_applied_globally,
        expiration=mock_clouded_ioc_expiration,
        source=mock_clouded_ioc_source,
    )

    assert iocs[0] == IOC._from_api_response(mock_clouded_ioc())


def test_module_update_ioc(client: Client, ioc_api: falconpy.IOC):
    ioc = IOC._from_api_response(mock_clouded_ioc())

    ioc_api.indicator_update.side_effect = mock_api_returns_ioc()

    iocs = client.ioc.update(ioc, comment="unit test")

    ioc_api.indicator_update.assert_called_once_with(
        indicators=[ioc._to_api_request()],
        retrodetects=False,
        ignore_warnings=False,
        comment="unit test",
    )

    assert iocs[0] == IOC._from_api_response(mock_clouded_ioc())

def test_module_delete_ioc(client: Client, ioc_api: falconpy.IOC):
    ioc = IOC._from_api_response(mock_clouded_ioc())

    ioc_api.indicator_delete.side_effect = mock_api_returns_id()

    iocs = client.ioc.delete(ioc, comment="unit test")

    ioc_api.indicator_delete.assert_called_once_with(
        ids=[ioc.id],
        comment="unit test",
        from_parent=False,
    )

    assert iocs[0] == ioc.id

def test_module_describe_iocs(client: Client, ioc_api: falconpy.IOC):
    filters = client.FalconFilter(dialect="iocs")
    filters.create_new_filter("id", mock_clouded_ioc()["id"])
    ioc_api.indicator_search.side_effect = mock_api_returns_id()
    ioc_api.indicator_get.side_effect = mock_api_returns_ioc()

    iocs = client.ioc.describe_iocs(filters)

    assert iocs[0] == IOC._from_api_response(mock_clouded_ioc())