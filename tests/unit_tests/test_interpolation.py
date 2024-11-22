"""Unit tests for `VariableInterpolator`"""
import os
from unittest import mock
from caracara.common.interpolation import VariableInterpolator


@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1"}, clear=True)
def test_interpolation_valid_input_simple():
    """Tests that `VariableInterpolator.interpolate()` interpolates correctly"""
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("${CLOUD_NAME}")
    assert cloud_name=="usgov1"

@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1", "CID": "test"}, clear=True)
def test_interpolation_valid_input_complex():
    """Tests that `VariableInterpolator.interpolate()` interpolates correctly"""
    interpolator = VariableInterpolator()
    interpolated = interpolator.interpolate("test${CID}data$example{}${CLOUD_NAME}")
    assert interpolated=="testtestdata$example{}usgov1"

@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1"}, clear=True)
def test_interpolation_double_dollars():
    """Tests `VariableInterpolator.interpolate()` handling of escaped dollar signs"""
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("$${CLOUD_NAME}")
    assert cloud_name == "${CLOUD_NAME}"

@mock.patch.dict(os.environ, {}, clear=True)
def test_interpolation_no_environment_match():
    """Tests how `VariableInterpolator.interpolate()` handles interpolation
    strings which have no associated environment variable to interpolate
    """
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("${CLOUD_NAME}")
    assert cloud_name == "${CLOUD_NAME}"

@mock.patch.dict(os.environ, {}, clear=True)
def test_interpolation_nothing_to_interpolate():
    """Tests `VariableInterpolator.interpolate()` with nothing to interpolate"""
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("do_not_interpolate_me")
    assert cloud_name == "do_not_interpolate_me"
