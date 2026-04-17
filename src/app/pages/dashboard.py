import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import io
import base64
import os
try:
    import numpy as np
    from PIL import Image
except ImportError:
    pass

try:
    import tensorflow as tf
    MODEL_PATH = "/app/wildlife_classifier_final.keras"
except ImportError:
    tf = None
    MODEL_PATH = ""

model = None

try:
    from classes import CLASS_NAMES
except ImportError:
    CLASS_NAMES = []

dash.register_page(__name__, path="/dashboard", title="Vadvilág - Dashboard")

layout = html.Div(
    className="dashboard-page",
    children=[
        dcc.Location(id="dashboard-redirect", refresh=True),

        html.Div(
            id="dashboard-content",
            className="dashboard-container",
        ),
    ],
)


@callback(
    Output("dashboard-content", "children"),
    Output("dashboard-redirect", "href"),
    Input("auth-store", "data"),
)
def render_dashboard(auth_data):

    if not auth_data or not auth_data.get("access_token"):
        return no_update, "/login"

    user_email = auth_data.get("user_email", "User")

    return html.Div([
        html.Div(
            className="dashboard-header",
            children=[
                html.H1(
                    children=[
                        html.Span("Welcome, ", className="welcome-text"),
                        html.Span(user_email, className="welcome-email"),
                    ],
                ),
                html.P("Your wildlife classification dashboard", className="dashboard-subtitle"),
            ],
        ),

        # Quick stats
        html.Div(
            className="dashboard-stats",
            children=[
                _dash_stat("", "0", "Képek klasszifikálva", "stat-classified"),
                _dash_stat("", "—", "Utolsó osztályozás", "stat-last"),
                _dash_stat("", "0", "Összes feltöltés", "stat-total"),
            ],
        ),

        # Upload section placeholder
        html.Div(
            className="upload-section glass-card",
            children=[
                html.H3("Kép klasszifikálása", style={"textAlign": "center"}),
                dcc.Upload(
                    id="upload-image",
                    children=html.Div([
                        "Húzd ide a képet, vagy ",
                        html.A("Kattints a kiválasztáshoz", style={"color": "#4a90e2", "cursor": "pointer"})
                    ]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderColor": "#4a90e2",
                        "borderRadius": "8px",
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "backgroundColor": "rgba(255, 255, 255, 0.05)"
                    },
                    multiple=False,
                    accept="image/*"
                ),
                dcc.Loading(
                    id="loading-output",
                    type="circle",
                    color="#4a90e2",
                    children=html.Div(id="upload-output", style={"textAlign": "center", "minHeight": "200px"})
                )
            ],
        ),
    ]), no_update


@callback(
    Output("upload-output", "children"),
    Output("stat-classified", "children"),
    Output("stat-last", "children"),
    Output("stat-total", "children"),
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    State("stat-classified", "children"),
    State("stat-total", "children"),
    prevent_initial_call=True
)
def update_output(contents, filename, current_classified, current_total):
    global model
    if contents is not None:
        
        try:
            total_uploads = int(current_total) + 1
        except (ValueError, TypeError):
            total_uploads = 1

        if tf is None:
            return html.Div("Tensorflow could not be loaded.", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
            
        if model is None and os.path.exists(MODEL_PATH):
            try:
                model = tf.keras.models.load_model(MODEL_PATH)
            except Exception as e:
                print(f"Error loading model: {e}")
                
        if model is None:
            return html.Div("The AI model file could not be loaded or is not mounted properly.", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            img = Image.open(io.BytesIO(decoded)).convert('RGB')
            # 224x224 is standard for ConvNeXt
            img_resized = img.resize((224, 224))
            img_array = np.array(img_resized)
            img_array = np.expand_dims(img_array, axis=0)
            
            preds = model.predict(img_array, verbose=0)
            class_idx = np.argmax(preds[0])
            confidence = float(np.max(preds[0]))
            
            if class_idx < len(CLASS_NAMES):
                class_name = CLASS_NAMES[class_idx].replace('_', ' ')
            else:
                class_name = f"Unknown ({class_idx})"
                
            try:
                new_classified = int(current_classified) + 1
            except (ValueError, TypeError):
                new_classified = 1

            return html.Div([
                html.H3(f"Prediction: {class_name}", style={"color": "#2ecc71"}),
                html.H4(f"Confidence: {confidence * 100:.2f}%"),
                html.Img(src=contents, style={"maxWidth": "100%", "maxHeight": "400px", "borderRadius": "8px", "marginTop": "20px"})
            ]), str(new_classified), class_name, str(total_uploads)
            
        except Exception as e:
            return html.Div(f"Hiba történt a feldolgozás során: {e}", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
    return html.Div(), current_classified, "—", current_total


def _dash_stat(icon: str, value: str, label: str, val_id: str = None):
    return html.Div(
        className="dash-stat glass-card",
        children=[
            html.Div(icon, className="dash-stat-icon"),
            html.Div(value, className="dash-stat-value", id=val_id) if val_id else html.Div(value, className="dash-stat-value"),
            html.Div(label, className="dash-stat-label"),
        ],
    )
