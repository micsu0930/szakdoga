import pytest
from unittest.mock import MagicMock
import sys
import os

# Add src/app to sys.path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize the Dash app FIRST so that dash.register_page() calls inside
# page modules don't raise PageError (requires use_pages=True app to exist).
import app as _dash_app  # noqa: F401  (side-effect import)

@pytest.fixture
def mock_supabase_client(mocker):
    """
    Fixture to mock the Supabase client and its auth/table methods.
    """
    mock_client = MagicMock()
    # Mock auth methods
    mock_client.auth.sign_up.return_value = MagicMock(user=None)
    mock_client.auth.sign_in_with_password.return_value = MagicMock(session=None)
    
    # Mock table methods
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[])
    
    mocker.patch('auth.create_client', return_value=mock_client)
    return mock_client

@pytest.fixture
def sample_auth_data():
    """
    Sample authentication data stored in Dash auth-store.
    """
    return {
        "access_token": "fake-access-token",
        "refresh_token": "fake-refresh-token",
        "user_email": "test@example.com",
        "user_id": "test-user-id"
    }
