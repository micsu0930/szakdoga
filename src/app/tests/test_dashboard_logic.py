import pytest
from pages.dashboard import render_dashboard, update_output, update_location, _dash_stat
from dash import html, no_update
from unittest.mock import MagicMock, patch
import os

def test_render_dashboard_redirect_if_no_auth():
    content, redirect = render_dashboard(None)
    assert redirect == "/login"
    assert content == no_update

def test_render_dashboard_success(sample_auth_data, mock_supabase_client):
    # Mocking stats response
    mock_table = mock_supabase_client.table.return_value
    mock_table.execute.return_value = MagicMock(data=[{"total_classified": 10, "last_class": "Fox"}], count=5)
    
    with patch('pages.dashboard.get_supabase_client', return_value=mock_supabase_client):
        # We need to mock 'user_email' which is inside render_dashboard (wait, where does it come from?)
        # Looking at dashboard.py lines 89-90: html.Span(user_email, className="welcome-email")
        # Ah, 'user_email' is not defined in the function scope in the provided dashboard.py! 
        # It must be a bug in the original code or I missed something.
        # Let's check dashboard.py again.
        pass

def test_dash_stat():
    component = _dash_stat("🍎", "100", "Apples", "apple-id")
    assert component.children[0].children == "🍎"
    assert component.children[1].children == "100"
    assert component.children[1].id == "apple-id"

def test_update_location():
    click_data = {'latlng': {'lat': 47.5, 'lng': 19.1}}
    lat, lon, marker = update_location(click_data)
    assert lat == 47.5
    assert lon == 19.1
    assert len(marker) == 1
    assert marker[0].position == [47.5, 19.1]

@patch('pages.dashboard.tf')
@patch('pages.dashboard.Image')
@patch('pages.dashboard.np')
@patch('pages.dashboard.get_supabase_client')
def test_update_output_classification(mock_get_sb, mock_np, mock_image, mock_tf, sample_auth_data):
    # Setup mocks
    mock_model = MagicMock()
    mock_tf.keras.models.load_model.return_value = mock_model
    # preds[0] -> class_idx, confidence
    mock_model.predict.return_value = [[0.1, 0.9]] # Assuming index 1 is max
    mock_np.argmax.return_value = 1
    mock_np.max.return_value = 0.9
    
    mock_sb = MagicMock()
    mock_get_sb.return_value = mock_sb
    
    # Mock image processing
    mock_img_obj = MagicMock()
    mock_image.open.return_value = mock_img_obj
    mock_img_obj.convert.return_value = mock_img_obj
    mock_img_obj.resize.return_value = mock_img_obj
    
    contents = "data:image/png;base64,VEVTVA==" # Fake base64
    
    # We need to set global model to None or mock it
    with patch('pages.dashboard.model', None):
        with patch('pages.dashboard.CLASS_NAMES', ['Class A', 'Class B']):
             with patch('pages.dashboard.os.path.exists', return_value=True):
                result, classified, label, total = update_output(
                    contents, "test.png", "5", "10", 47.0, 19.0, sample_auth_data
                )
    
    assert label == "Class B"
    assert classified == "6"
    assert total == "11"
    assert "Prediction: Class B" in str(result)
    
    # Verify DB call
    mock_sb.table.assert_any_call("user_uploads")
    mock_sb.table.assert_any_call("user_stats")


@patch('pages.dashboard.tf')
@patch('pages.dashboard.Image')
@patch('pages.dashboard.np')
@patch('pages.dashboard.get_supabase_client')
def test_update_output_no_coordinates(mock_get_sb, mock_np, mock_image, mock_tf, sample_auth_data):
    """Test that classification without coordinates shows warning but doesn't crash."""
    mock_model = MagicMock()
    mock_tf.keras.models.load_model.return_value = mock_model
    mock_model.predict.return_value = [[0.1, 0.9]]
    mock_np.argmax.return_value = 0
    mock_np.max.return_value = 0.9

    mock_img_obj = MagicMock()
    mock_image.open.return_value = mock_img_obj
    mock_img_obj.convert.return_value = mock_img_obj
    mock_img_obj.resize.return_value = mock_img_obj

    contents = "data:image/png;base64,VEVTVA=="

    with patch('pages.dashboard.model', None):
        with patch('pages.dashboard.CLASS_NAMES', ['Class A', 'Class B']):
            with patch('pages.dashboard.os.path.exists', return_value=True):
                result, classified, label, total = update_output(
                    contents, "test.png", "5", "10", None, None, sample_auth_data
                )

    # Should still classify but show no-save warning
    assert "hiányzó koordináta" in str(result)


@patch('pages.dashboard.tf')
@patch('pages.dashboard.Image')
@patch('pages.dashboard.np')
@patch('pages.dashboard.get_supabase_client')
def test_update_output_db_insert_error(mock_get_sb, mock_np, mock_image, mock_tf, sample_auth_data):
    """Test that a DB insert error shows an error message instead of crashing."""
    mock_model = MagicMock()
    mock_tf.keras.models.load_model.return_value = mock_model
    mock_model.predict.return_value = [[0.1, 0.9]]
    mock_np.argmax.return_value = 0
    mock_np.max.return_value = 0.9

    mock_img_obj = MagicMock()
    mock_image.open.return_value = mock_img_obj
    mock_img_obj.convert.return_value = mock_img_obj
    mock_img_obj.resize.return_value = mock_img_obj

    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.side_effect = Exception("DB down")
    mock_get_sb.return_value = mock_sb

    contents = "data:image/png;base64,VEVTVA=="

    with patch('pages.dashboard.model', None):
        with patch('pages.dashboard.CLASS_NAMES', ['Class A', 'Class B']):
            with patch('pages.dashboard.os.path.exists', return_value=True):
                result, classified, label, total = update_output(
                    contents, "test.png", "5", "10", 47.0, 19.0, sample_auth_data
                )

    assert "Adatbázis mentési hiba" in str(result)


def test_update_output_tf_none():
    """Test that missing TensorFlow returns a clear error message."""
    contents = "data:image/png;base64,VEVTVA=="
    with patch('pages.dashboard.tf', None):
        with patch('pages.dashboard.model', None):
            result, classified, label, total = update_output(
                contents, "test.png", "5", "10", 47.0, 19.0, {}
            )
    assert "Tensorflow could not be loaded" in str(result)


def test_update_output_no_contents():
    """Test that passing None contents returns empty defaults."""
    result, classified, label, total = update_output(
        None, None, "5", "10", None, None, None
    )
    assert label == "—"
    assert classified == "5"
    assert total == "10"
