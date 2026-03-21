import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import sign_up

dash.register_page(__name__, path="/register", title="Regisztráció - Vadvilág - Dashboard")

layout = html.Div(
    className="auth-page",
    children=[
        html.Div(
            className="auth-card",
            children=[
                html.Div(
                    className="auth-header",
                    children=[
                        html.Div("Regisztráció", className="auth-icon"),
                        html.H2("Hozzon létre egy fiókot"),
                    ],
                ),

                html.Div(id="register-error", className="auth-message auth-error"),
                html.Div(id="register-success", className="auth-message auth-success"),

                html.Div(
                    className="auth-form",
                    children=[
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Email", htmlFor="register-email"),
                                dcc.Input(
                                    id="register-email",
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
                                html.Label("Jelszó", htmlFor="register-password"),
                                dcc.Input(
                                    id="register-password",
                                    type="password",
                                    placeholder="Jelszava legyen legalább 6 karakter",
                                    className="form-input",
                                    autoComplete="new-password",
                                ),
                            ],
                        ),
                        html.Div(
                            className="form-group",
                            children=[
                                html.Label("Jelszó megerősítése", htmlFor="register-confirm"),
                                dcc.Input(
                                    id="register-confirm",
                                    type="password",
                                    placeholder="Ismételje meg jelszavát",
                                    className="form-input",
                                    autoComplete="new-password",
                                ),
                            ],
                        ),
                        html.Button(
                            "Fiók létrehozása",
                            id="register-button",
                            className="btn btn-primary btn-full",
                            n_clicks=0,
                        ),
                    ],
                ),

                html.Div(
                    className="auth-footer",
                    children=[
                        html.Span("Már van fiókod? "),
                        html.A("Bejelentkezés", href="/login", className="auth-link"),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("register-error", "children"),
    Output("register-success", "children"),
    Output("url", "href", allow_duplicate=True),
    Input("register-button", "n_clicks"),
    State("register-email", "value"),
    State("register-password", "value"),
    State("register-confirm", "value"),
    prevent_initial_call=True,
)
def handle_register(n_clicks, email, password, confirm):

    if not n_clicks:
        return no_update, no_update, no_update

    if not email or not password or not confirm:
        return "Please fill in all fields.", "", no_update

    if len(password) < 6:
        return "Jelszava legyen legalább 6 karakter.", "", no_update

    if password != confirm:
        return "Jelszavak nem egyeznek.", "", no_update
    result = sign_up(email.strip(), password)

    if result["success"]:
        return "", result["message"], "/login"
    else:
        return result["message"], "", no_update
