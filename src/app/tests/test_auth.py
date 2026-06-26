import pytest
from auth import sign_up, sign_in, sign_out, get_supabase_client
from unittest.mock import MagicMock

def test_get_supabase_client(mocker):
    mock_create = mocker.patch('auth.create_client')
    get_supabase_client()
    mock_create.assert_called_once()

def test_sign_up_success(mock_supabase_client):
    # Setup mock response
    mock_user = MagicMock()
    mock_user.id = "new-user-id"
    mock_user.email = "new@example.com"
    mock_supabase_client.auth.sign_up.return_value = MagicMock(user=mock_user)
    
    result = sign_up("new@example.com", "password123")
    
    assert result["success"] is True
    assert "Sikeres regisztráció" in result["message"]
    assert result["data"]["user_id"] == "new-user-id"

def test_sign_up_failure(mock_supabase_client):
    mock_supabase_client.auth.sign_up.return_value = MagicMock(user=None)
    
    result = sign_up("fail@example.com", "short")
    
    assert result["success"] is False
    assert "Sikertelen regisztráció" in result["message"]

def test_sign_in_success(mock_supabase_client):
    mock_session = MagicMock()
    mock_session.access_token = "access"
    mock_session.refresh_token = "refresh"
    mock_user = MagicMock()
    mock_user.email = "user@example.com"
    mock_user.id = "user-id"
    
    mock_supabase_client.auth.sign_in_with_password.return_value = MagicMock(
        session=mock_session,
        user=mock_user
    )
    
    result = sign_in("user@example.com", "password")
    
    assert result["success"] is True
    assert result["session"]["access_token"] == "access"
    assert result["session"]["user_id"] == "user-id"

def test_sign_in_invalid_credentials(mock_supabase_client):
    mock_supabase_client.auth.sign_in_with_password.side_effect = Exception("invalid credentials")
    
    result = sign_in("wrong@email.com", "wrong")
    
    assert result["success"] is False
    assert "Invalid email or password" in result["message"]

def test_sign_up_already_exists(mock_supabase_client):
    mock_supabase_client.auth.sign_up.side_effect = Exception("User already exists")

    result = sign_up("existing@example.com", "password123")

    assert result["success"] is False
    assert "már tartozik" in result["message"]

def test_sign_up_password_error(mock_supabase_client):
    mock_supabase_client.auth.sign_up.side_effect = Exception("password too short")

    result = sign_up("new@example.com", "123")

    assert result["success"] is False
    assert "6 karakteresnek" in result["message"]

def test_sign_up_generic_error(mock_supabase_client):
    mock_supabase_client.auth.sign_up.side_effect = Exception("network timeout")

    result = sign_up("new@example.com", "password123")

    assert result["success"] is False
    assert "Registration error" in result["message"]

def test_sign_in_no_session(mock_supabase_client):
    """Test sign_in when response has no session (line 98)."""
    mock_supabase_client.auth.sign_in_with_password.return_value = MagicMock(session=None)

    result = sign_in("user@example.com", "wrongpassword")

    assert result["success"] is False
    assert "Sikertelen" in result["message"]

def test_sign_in_generic_error(mock_supabase_client):
    """Test sign_in generic exception path (line 107)."""
    mock_supabase_client.auth.sign_in_with_password.side_effect = Exception("network error")

    result = sign_in("user@example.com", "password123")

    assert result["success"] is False
    assert "Login error" in result["message"]

def test_sign_out(mock_supabase_client):
    result = sign_out("some-token")
    assert result["success"] is True
    mock_supabase_client.auth.sign_out.assert_called_once()
