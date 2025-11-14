import pytest
import numpy as np
from backend.main import _parse_single


def test_parse_single_dict_with_keys():
    payload = {"velocity": 50.0, "angle_deg": 45.0}
    result = _parse_single(payload)

    assert result.shape == (1, 2)
    assert result[0, 0] == 50.0
    assert result[0, 1] == 45.0
    assert result.dtype == np.float32


def test_parse_single_dict_with_instance():
    payload = {"instance": {"velocity": 30.5, "angle_deg": 60.2}}
    result = _parse_single(payload)

    assert result.shape == (1, 2)
    assert result[0, 0] == 30.5
    assert result[0, 1] == 60.2


def test_parse_single_list():
    payload = [40.0, 55.0]
    result = _parse_single(payload)

    assert result.shape == (1, 2)
    assert result[0, 0] == 40.0
    assert result[0, 1] == 55.0


def test_parse_single_tuple():
    payload = (25.5, 35.8)
    result = _parse_single(payload)

    assert result.shape == (1, 2)
    assert result[0, 0] == 25.5
    assert result[0, 1] == 35.8


def test_parse_single_missing_velocity():
    payload = {"angle_deg": 45.0}

    with pytest.raises(ValueError, match="Missing 'velocity' or 'angle_deg'"):
        _parse_single(payload)


def test_parse_single_missing_angle():
    payload = {"velocity": 50.0}

    with pytest.raises(ValueError, match="Missing 'velocity' or 'angle_deg'"):
        _parse_single(payload)


def test_parse_single_invalid_list_length():
    payload = [40.0, 55.0, 60.0]

    with pytest.raises(ValueError, match="Only a single vector"):
        _parse_single(payload)


def test_parse_single_invalid_type():
    payload = "invalid string"

    with pytest.raises(ValueError, match="Payload must be a dict"):
        _parse_single(payload)


def test_parse_single_type_conversion():
    payload = {"velocity": 50, "angle_deg": 45}
    result = _parse_single(payload)

    assert result.dtype == np.float32
    assert isinstance(result[0, 0], np.float32)