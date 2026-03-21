import os
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from dotenv import load_dotenv

load_dotenv()

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Vadvilág - Dashboard",
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "Vadvilág - Dashboard"},
    ],
)

server = app.server
server.secret_key = os.getenv("DASH_SECRET_KEY", "dev-secret-key-change-me")

app.layout = html.Div([
    #Auth sess
    dcc.Store(id="auth-store", storage_type="session"),

    #URL handler
    dcc.Location(id="url", refresh=True),

    #Nav bar
    html.Nav(
        className="navbar",
        children=[
            html.Div(
                className="nav-container",
                children=[
                    html.A(
                        children=[
                            html.Span("Vadvilág - Dashboard", className="nav-title"),
                        ],
                        href="/",
                        className="nav-brand",
                    ),
                    html.Div(id="nav-links", className="nav-links"),
                ],
            ),
        ],
    ),

    #f msg
    html.Div(id="flash-message", className="flash-container"),

    html.Div(
        className="page-container",
        children=[dash.page_container],
    ),

])






@callback(
    Output("nav-links", "children"),
    Input("auth-store", "data"),
)
def update_nav(auth_data):
    
    if auth_data and auth_data.get("access_token"):
        return [
            html.A("Dashboard", href="/dashboard", className="nav-link"),
            html.A("Logout", href="/logout", className="nav-link nav-link-outline"),
        ]
    return [
        html.A("Login", href="/login", className="nav-link"),
        html.A("Register", href="/register", className="nav-link nav-link-primary"),
    ]


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
