import dash
from dash import html, dcc, callback, Output, Input, State, no_update

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
                _dash_stat("0", "Képek klasszifikálva"),
                _dash_stat("—", "Utolsó osztályozás"),
                _dash_stat("0", "Összes feltöltés"),
            ],
        ),

        # Upload section placeholder
        html.Div(
            className="upload-section glass-card",
            children=[
                html.Div(
                    className="upload-placeholder",
                    children=[
                        html.Div("Feltöltés", className="upload-icon"),
                        html.H3("Kép klasszifikálása"),
                        html.P(
                            "Tölts fel képet Klasszifikáláshoz. "
                            "PLACEHOLDER!",
                            className="upload-description",
                        ),
                        html.Button(
                            "Kép Feltöltése (PLACEHOLDER)",
                            className="btn btn-primary btn-lg",
                            disabled=True,
                            style={"opacity": "0.5", "cursor": "not-allowed"},
                        ),
                    ],
                ),
            ],
        ),
    ]), no_update


def _dash_stat(icon: str, value: str, label: str):
    return html.Div(
        className="dash-stat glass-card",
        children=[
            html.Div(icon, className="dash-stat-icon"),
            html.Div(value, className="dash-stat-value"),
            html.Div(label, className="dash-stat-label"),
        ],
    )
