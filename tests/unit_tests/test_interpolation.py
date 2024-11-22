from caracara.common.interpolation import VariableInterpolator
import os
from unittest import mock

@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1"}, clear=True)
def test_interpolation_valid_input_simple():
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("${CLOUD_NAME}")
    assert cloud_name=="usgov1"

@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1", "CID": "test"}, clear=True)
def test_interpolation_valid_input_complex():
    interpolator = VariableInterpolator()
    interpolated = interpolator.interpolate("test${CID}data$example{}${CLOUD_NAME}")
    assert interpolated=="testtestdata$example{}usgov1"

@mock.patch.dict(os.environ, {"CLOUD_NAME": "usgov1"}, clear=True)
def test_interpolation_double_dollars():
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("$${CLOUD_NAME}")
    assert cloud_name == "${CLOUD_NAME}"

@mock.patch.dict(os.environ, {}, clear=True)
def test_interpolation_no_environment_match():
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("${CLOUD_NAME}")
    assert cloud_name == "${CLOUD_NAME}"

@mock.patch.dict(os.environ, {}, clear=True)
def test_interpolation_nothing_to_interpolate():
    interpolator = VariableInterpolator()
    cloud_name = interpolator.interpolate("do_not_interpolate_me")
    assert cloud_name == "do_not_interpolate_me"