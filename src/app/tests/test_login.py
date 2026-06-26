import pytest
import dash
from dash import no_update
from unittest.mock import patch

from pages.login import handle_login

def test_handle_login_empty_fields():
    """Test login behavior when fields are empty."""
    auth_data, err, redir = handle_login(1, "", "")
    assert "Please fill in all fields" in err
    assert auth_data == no_update
    assert redir == no_update

@patch('pages.login.sign_in')
def test_handle_login_success(mock_sign_in):
    """Test login behavior on successful sign in."""
    mock_session = {"access_token": "token", "user_id": "123"}
    mock_sign_in.return_value = {"success": True, "session": mock_session}
    
    auth_data, err, redir = handle_login(1, "test@test.com", "123456")
    
    assert auth_data == mock_session
    assert err == ""
    assert redir == "/dashboard"

@patch('pages.login.sign_in')
def test_handle_login_failure(mock_sign_in):
    """Test login behavior on sign in failure."""
    mock_sign_in.return_value = {"success": False, "message": "Invalid credentials"}
    
    auth_data, err, redir = handle_login(1, "test@test.com", "wrongpassword")
    
    assert auth_data == no_update
    assert err == "Invalid credentials"
    assert redir == no_update
