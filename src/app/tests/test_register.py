import pytest
import dash
from dash import no_update
from unittest.mock import patch

from pages.register import handle_register

def test_handle_register_empty_fields():
    """Test register behavior when fields are empty."""
    err, succ, redir = handle_register(1, "", "", "")
    assert "Please fill in all fields" in err
    assert succ == ""
    assert redir == no_update

def test_handle_register_short_password():
    """Test register behavior with a short password."""
    err, succ, redir = handle_register(1, "test@test.com", "123", "123")
    assert "Jelszava legyen legalább 6 karakter" in err
    assert succ == ""
    assert redir == no_update

def test_handle_register_password_mismatch():
    """Test register behavior when passwords don't match."""
    err, succ, redir = handle_register(1, "test@test.com", "123456", "1234567")
    assert "Jelszavak nem egyeznek" in err
    assert succ == ""
    assert redir == no_update

@patch('pages.register.sign_up')
def test_handle_register_success(mock_sign_up):
    """Test register behavior on successful sign up."""
    mock_sign_up.return_value = {"success": True, "message": "Success message"}
    err, succ, redir = handle_register(1, "test@test.com", "123456", "123456")
    
    assert err == ""
    assert succ == "Success message"
    assert redir == "/login"

@patch('pages.register.sign_up')
def test_handle_register_failure(mock_sign_up):
    """Test register behavior on sign up failure."""
    mock_sign_up.return_value = {"success": False, "message": "Error message"}
    err, succ, redir = handle_register(1, "test@test.com", "123456", "123456")
    
    assert err == "Error message"
    assert succ == ""
    assert redir == no_update
