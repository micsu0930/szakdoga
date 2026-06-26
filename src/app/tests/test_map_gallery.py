import pytest
import dash
from dash import no_update
from unittest.mock import patch, MagicMock

# Import the callbacks to test
from pages.map_gallery import render_gallery, update_selected_details

def test_render_gallery_no_auth():
    """Test that render_gallery redirects to login when no auth data is provided."""
    layout, redirect = render_gallery(None)
    assert redirect == "/login"
    assert layout == no_update

    layout, redirect = render_gallery({})
    assert redirect == "/login"
    assert layout == no_update

def test_render_gallery_with_auth(mock_supabase_client, sample_auth_data):
    """Test that render_gallery renders the map and gallery when authenticated."""
    
    # Mock the database response
    mock_data = [
        {
            "id": 1,
            "latitude": 47.5,
            "longitude": 19.0,
            "predicted_class": "Test Species",
            "confidence": 0.95,
            "image_data": "data:image/png;base64,testdata"
        }
    ]
    mock_supabase_client.table().select().execute.return_value = MagicMock(data=mock_data)
    
    layout, redirect = render_gallery(sample_auth_data)
    
    assert redirect == no_update
    assert layout is not None
    # Check that it contains "Klasszifikált Állatok Térképe"
    assert "Klasszifikált Állatok Térképe" in str(layout)

@patch('dash.callback_context')
def test_update_selected_details_no_trigger(mock_ctx):
    """Test detail update with no trigger."""
    mock_ctx.triggered = []
    uploads = []
    
    result = update_selected_details(None, None, uploads)
    assert "Kattints egy markerre" in str(result)

@patch('dash.callback_context')
def test_update_selected_details_with_trigger(mock_ctx):
    """Test detail update when a marker or gallery item is clicked."""
    mock_ctx.triggered = [{"prop_id": '{"index":1,"type":"map-marker"}.n_clicks'}]
    
    uploads = [
        {
            "id": 1,
            "latitude": 47.5,
            "longitude": 19.0,
            "predicted_class": "Test Species",
            "confidence": 0.95,
            "image_data": "data:image/png;base64,testdata"
        }
    ]
    
    result = update_selected_details(1, None, uploads)
    
    assert "Test Species" in str(result)
    assert "Confidence: 95.0%" in str(result)
    assert "Coordinates: 47.5" in str(result)
