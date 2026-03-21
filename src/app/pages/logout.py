import dash
from dash import html, dcc, callback, Output, Input

dash.register_page(__name__, path="/logout", title="Kijelentkezés - Vadvilág - Dashboard")

layout = html.Div(
    className="auth-page",
    children=[
        dcc.Location(id="logout-redirect", refresh=True),
        html.Div(
            className="auth-card",
            style={"textAlign": "center"},
            children=[
                html.Div("👋", className="auth-icon"),
                html.H2("Kijelentkezés..."),
                html.P("Sikeresen kijelentkezett.", className="auth-subtitle"),
            ],
        ),
    ],
)


@callback(
    Output("auth-store", "data", allow_duplicate=True),
    Output("logout-redirect", "href"),
    Input("logout-redirect", "pathname"),
    prevent_initial_call=True,
)
def handle_logout(pathname):
    return None, "/"
