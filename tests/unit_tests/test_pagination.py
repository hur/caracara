from caracara.common.pagination import all_pages_numbered_offset, all_pages_numbered_offset_parallel, all_pages_token_offset, generic_parallel_list_execution

from unittest import mock
from functools import partial

import pytest
import logging
import uuid

@pytest.fixture
def logger():
    """Initialize a logger for the unit test, as one is required
    by the pagination functions
    """
    return logging.getLogger(__name__)

TEST_DATA = [i for i in range(100)]
TOKENS = [uuid.uuid4().hex for _ in range(100)]

def mock_numerical_offset(body):
    """Mocks a paginated API endpoint according as expected by `all_pages_numbered_offset`"""
    return {
        "body" : {
            "resources": 
                TEST_DATA[body["offset"]:body["offset"]+body["limit"]]
            ,
            "meta": {
                "pagination": {
                    "limit": body["limit"],
                    "offset": body["offset"] + body["limit"],
                    "total": len(TEST_DATA),
                }
            }
        }
    }

def mock_numerical_offset_parallel(offset, limit):
    """Mocks a paginated API endpoint according as expected by `all_pages_numbered_offset_parallel`"""
    return {
        "body" : {
            "resources": 
                TEST_DATA[offset:offset+limit]
            ,
            "meta": {
                "pagination": {
                    "limit": limit,
                    "offset": offset + limit,
                    "total": len(TEST_DATA),
                }
            }
        }
    }

def mock_all_pages_token_offset(offset: str, limit: int):
    offset_idx = TOKENS.index(offset) if offset is not None else 0
    return {
        "body" : {
            "resources": 
                TEST_DATA[offset_idx:offset_idx+limit]
            ,
            "meta": {
                "pagination": {
                    "limit": limit,
                    "offset": TOKENS[offset_idx+limit] if offset_idx+limit < len(TOKENS) else "",
                    "total": len(TEST_DATA),
                }
            }
        }
    }

def mock_all_pages_token_offset_after(after: str, limit: int):
    offset_idx = TOKENS.index(after) if after is not None else 0
    return {
        "body" : {
            "resources": 
                TEST_DATA[offset_idx:offset_idx+limit]
            ,
            "meta": {
                "pagination": {
                    "limit": limit,
                    "after": TOKENS[offset_idx+limit] if offset_idx+limit < len(TOKENS) else "",
                    "total": len(TEST_DATA),
                }
            }
        }
    }

def mock_func_for_generic_parallel_list_execution(param):
    return {"body": {"resources": [param]}}

def test_all_pages_numbered_offset(logger):
    """Tests that `all_pages_numbered_offset` returns the correct data"""
    for limit in [1, 3, 5, 6, 10]:
        result = all_pages_numbered_offset(
            mock_numerical_offset, logger, limit=limit)
        assert result == TEST_DATA

def test_all_pages_numbered_offset_parallel(logger):
    """Tests that `all_pages_numbered_offset_parallel` returns the correct data"""
    for limit in [1, 3, 5, 6, 10]:
        result = all_pages_numbered_offset_parallel(
            mock_numerical_offset_parallel, logger, limit=limit)
        assert result == TEST_DATA

def test_all_pages_token_offset(logger):
    """Tests that `all_pages_token_offset` returns the correct data"""
    for limit in [1, 3, 5, 6, 10]:
        result = all_pages_token_offset(
            mock_all_pages_token_offset, logger, limit=limit
        )
        assert result == TEST_DATA

def test_all_pages_token_offset_after(logger):
    """Tests that `all_pages_token_offset(offset_key_named_after=True)` returns the correct data"""
    for limit in [1, 3, 5, 6, 10]:
        result = all_pages_token_offset(
            mock_all_pages_token_offset_after, logger, limit=limit, offset_key_named_after=True
        )
        assert result == TEST_DATA

def test_generic_parallel_list_execution(logger):
    """Tests that `generic_parallel_list_execution` returns the expected data"""
    result = generic_parallel_list_execution(
        mock_func_for_generic_parallel_list_execution,
        logger,
        param_name="param",
        value_list = ["uuid1", "uuid2", "uuid3"]
    )
    assert result == ["uuid1", "uuid2", "uuid3"]

