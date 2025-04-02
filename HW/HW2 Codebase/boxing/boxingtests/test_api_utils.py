import pytest
from unittest.mock import patch
from boxing.api_utils import get_random

@patch("boxing.utils.api_utils.requests.get")
def test_get_random_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "0.75"

    result = get_random()
    assert result == 0.75

@patch("boxing.utils.api_utils.requests.get")
def test_get_random_invalid_response(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "not-a-number"

    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

@patch("boxing.utils.api_utils.requests.get", side_effect=Exception("Boom"))
def test_get_random_request_exception(mock_get):
    with pytest.raises(RuntimeError, match="Request to random.org failed"):
        get_random()

