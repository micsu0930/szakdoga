import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import sign_in

dash.register_page(__name__, path="/login", title="Login - Vadvilág - Dashboard")

layout = html.Div(
    className="auth-page",
    children=[
        html.Div(
            className="auth-card",
            children=[
                html.Div(
                    className="auth-header",
                    children=[
                        html.Div("Bejelentkezés", className="auth-icon"),
                        html.H2("Üdvözöljük"),
                        html.P("Jelentkezzen be fiókjába"),
                    ],
                ),

                # Error message display
                html.Div(id="login-error", className="auth-message auth-error"),

                # Login form
                html.Div(
                    className="auth-form",
                    children=[
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Email", htmlFor="login-email"),
                                dcc.Input(
                                    id="login-email",
                                    type="email",
                                    placeholder="minta@minta.hu",
                                    className="form-input",
                                    autoComplete="email",
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Jelszó", htmlFor="login-password"),
                                dcc.Input(
                                    id="login-password",
                                    type="password",
                                    placeholder="********",
                                    className="form-input",
                                    autoComplete="current-password",
                                ),
                            ],
                        ),
                        html.Button(
                            "Bejelentkezés",
                            id="login-button",
                            className="btn btn-primary btn-full",
                            n_clicks=0,
                        ),
                    ],
                ),

                html.Div(
                    className="auth-footer",
                    children=[
                        html.Span("Nincs fiókod? "),
                        html.A("Regisztráció", href="/register", className="auth-link"),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("auth-store", "data", allow_duplicate=True),
    Output("login-error", "children"),
    Output("url", "href", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def handle_login(n_clicks, email, password):

    if not n_clicks:
        return no_update, no_update, no_update

    if not email or not password:
        return no_update, "Please fill in all fields.", no_update

    result = sign_in(email.strip(), password)

    if result["success"]:
        return result["session"], "", "/dashboard"
    else:
        return no_update, result["message"], no_update
