import dash
from dash import html

dash.register_page(__name__, path="/", title="Vadvilág - Dashboard")


def _feature_card(icon: str, title: str, description: str):
    return html.Div(
        className="feature-card",
        children=[
            html.Div(icon, className="feature-icon"),
            html.H3(title, className="feature-title"),
            html.P(description, className="feature-description"),
        ],
    )


def _stat_card(value: str, label: str):
    return html.Div(
        className="stat-card",
        children=[
            html.Div(value, className="stat-value"),
            html.Div(label, className="stat-label"),
        ],
    )


layout = html.Div(
    className="landing-page",
    children=[
        html.Section(
            className="hero",
            children=[
                html.Div(
                    className="hero-content",
                    children=[
                        html.Div(className="hero-glow"),
                        html.H1(
                            children=[
                                html.Span("Vadvilág indentifikálás", className="hero-title-main"),
                                html.Br(),
                                html.Span("mesterséges intelligenciával", className="hero-title-accent"),
                            ],
                        ),
                        html.P(
                            "Tölts fel egy képet egy európai vadállatról "
                            "és az AI azonosítja neked!",
                            className="hero-subtitle",
                        ),
                        html.Div(
                            className="hero-buttons",
                            children=[
                                html.A(
                                    "Regisztráció",
                                    href="/register",
                                    className="btn btn-primary btn-lg",
                                ),
                                html.A(
                                    "Belépés",
                                    href="/login",
                                    className="btn btn-outline btn-lg",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),

        html.Section(
            className="features",
            children=[
                html.H2("Hogyan Működik?", className="section-title"),
                html.Div(
                    className="features-grid",
                    children=[
                        _feature_card(
                            "",
                            "Feltöltés",
                            "Készíts egy képet egy vadállatról és töltsd fel",
                        ),
                        _feature_card(
                            "",
                            "AI analízis",
                            "Az AI elemzi a képet és azonosítja a vadállatot",
                        ),
                        _feature_card(
                            "",
                            "Klasszifikáció",
                            "Az AI megadja az állat faját valószínüségi pontal",
                        ),
                    ],
                ),
            ],
        ),

        # ─── Stats Section ────────────────────────────
        html.Section(
            className="stats-section",
            children=[
                html.Div(
                    className="stats-grid",
                    children=[
                        _stat_card("10+", "Species"),
                        _stat_card("95%+", "Accuracy"),
                        _stat_card("< 2s", "Response"),
                        _stat_card("24/7", "Available"),
                    ],
                ),
            ],
        ),
    ],
)
