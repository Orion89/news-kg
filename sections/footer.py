import dash_bootstrap_components as dbc
from dash import html

main_footer = dbc.Card(
    [
        dbc.CardFooter(
            [
                html.P(
                    [
                        html.A(
                            children=[html.I(className="bi bi-github")],
                            disable_n_clicks=True,
                            href="https://github.com/Orion89",
                            title="GitHub profile",
                        ),
                        "  ",
                        html.A(
                            children=[html.I(className="bi bi-linkedin")],
                            disable_n_clicks=True,
                            href="https://www.linkedin.com/in/leonardo-molina-v-68a601183/",
                            title="LinkedIn profile",
                        ),
                        " 2024 Leonardo Molina V.",
                    ],
                    className="fs-5 text-light",
                ),
                html.P(
                    "Proyecto académico. El autor no se hace responsable del mal uso del contenido.",
                    className="text-light",
                ),
            ]
        )
    ],
    style={"background": "#222222"},
)
