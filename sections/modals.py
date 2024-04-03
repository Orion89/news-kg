import dash_bootstrap_components as dbc
from dash import html

modal = dbc.Modal(
    [
        dbc.ModalHeader(html.P("Cargando visualización...", className='fw-bold mb-0')),
        dbc.ModalBody(
            [
                html.P("El proceso de carga del grafo puede tardar unos minutos."),
                html.P('Puedes cerrar este cuadro.')
            ]
            ),
        dbc.ModalFooter(
            dbc.Button("Cerrar", id="modal-close", className="ml-auto", n_clicks=0)
        ),
    ],
    id="modal-1",
    is_open=True,
)