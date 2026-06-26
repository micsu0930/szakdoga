import dash
from dash import html, dcc, callback, Output, Input, no_update
import requests
import os

dash.register_page(__name__, path='/tensorboard', title="Training Logs")

TENSORBOARD_URL = "http://wildlife-tensorboard:6006"

layout = html.Div(
    className="page-content dashboard-page",
    children=[
        dcc.Location(id="tb-redirect", refresh=True),
        html.Div(
            id="tb-content",
            className="dashboard-container card",
            style={"height": "85vh", "padding": "0"}
        )
    ]
)

@callback(
    Output("tb-content", "children"),
    Output("tb-redirect", "href"),
    Input("auth-store", "data"),
)
def render_tb(auth_data):
    """
    Megjeleníti a TensorBoard nézegető oldalt, ellenőrizve a naplók elérhetőségét.
    
    Args:
        auth_data (dict): Felhasználói munkamenet adatok.
        
    Returns:
        tuple: (tensorboard_layout, redirect_path)
    """
    if not auth_data or not auth_data.get("access_token"):
        return no_update, "/login"

    header = html.Div(
        className="card-header",
        children=[
            html.H2("Tréning Log-ok (TensorBoard)"),
            html.P(
                "A neurális hálózat pontosságának és veszteségének monitorozása.",
                className="text-muted"
            ),
        ]
    )


    has_scalars = False
    try:
        resp = requests.get(f"{TENSORBOARD_URL}/data/plugin/scalars/tags", timeout=3)
        if resp.status_code == 200 and resp.json():
            has_scalars = True
    except Exception:
        pass

    if has_scalars:
        content = html.Iframe(

            src="http://localhost:6006/#scalars",
            style={
                "width": "100%",
                "height": "100%",
                "border": "none",
                "borderBottomLeftRadius": "12px",
                "borderBottomRightRadius": "12px",
                "minHeight": "75vh",
            }
        )
    else:
        content = html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "height": "70vh",
                "gap": "16px",
                "color": "#888",
            },
            children=[
                html.Span("📊", style={"fontSize": "64px"}),
                html.H3("Még nincsenek tréning adatok", style={"margin": "0"}),
                html.P(
                    "Futtassa a tanító notebookot a metrikák generálásához. "
                    "A grafikonok itt fognak megjelenni, amint a tanítás elkezdődik.",
                    style={"textAlign": "center", "maxWidth": "400px"},
                ),
            ]
        )

    return [header, content], no_update
