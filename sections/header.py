from dash import html

header = html.P(
    [
        html.A(
            children=[html.I(className="bi bi-github")],
            disable_n_clicks=True,
            href='https://github.com/Orion89',
            title="GitHub profile"
        ),
        "   ",
        html.A(
            children=[html.I(className="bi bi-linkedin")],
            disable_n_clicks=True,
            href='https://www.linkedin.com/in/leonardo-molina-v-68a601183/',
            title="LinkedIn profile"
        ) 
    ],
    className='text-info text-end fs-4'
)