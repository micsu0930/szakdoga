import pytest
from dash import no_update
from unittest.mock import patch, MagicMock

from pages.tensorboard_viewer import render_tb


def test_render_tb_no_auth():
    """Test redirect to login when no auth data is present."""
    layout, redirect = render_tb(None)
    assert redirect == "/login"
    assert layout == no_update

    layout, redirect = render_tb({})
    assert redirect == "/login"
    assert layout == no_update


@patch('pages.tensorboard_viewer.requests')
def test_render_tb_with_scalars(mock_requests, sample_auth_data):
    """Test that an iframe is rendered when TensorBoard has scalar data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"train": ["epoch_acc"]}
    mock_requests.get.return_value = mock_resp

    layout, redirect = render_tb(sample_auth_data)

    assert redirect == no_update
    # Layout is a list [header, content]; content should be an Iframe
    assert len(layout) == 2
    assert "Iframe" in str(type(layout[1]))


@patch('pages.tensorboard_viewer.requests')
def test_render_tb_no_scalars(mock_requests, sample_auth_data):
    """Test that a placeholder is shown when TensorBoard has no scalar data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {}  # empty -> no scalars
    mock_requests.get.return_value = mock_resp

    layout, redirect = render_tb(sample_auth_data)

    assert redirect == no_update
    assert "No training data yet" in str(layout)


@patch('pages.tensorboard_viewer.requests')
def test_render_tb_tensorboard_unreachable(mock_requests, sample_auth_data):
    """Test that a placeholder is shown when TensorBoard service is down."""
    mock_requests.get.side_effect = Exception("Connection refused")

    layout, redirect = render_tb(sample_auth_data)

    assert redirect == no_update
    assert "No training data yet" in str(layout)
