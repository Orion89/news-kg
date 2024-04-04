import dash_bootstrap_components as dbc
from dash import html

modal = dbc.Modal(
    [
        dbc.ModalHeader(
                html.P("Cargando visualización...", className='fw-bold mb-0 text-info'),
                class_name='bg-dark'
            ),
        dbc.ModalBody(
            [
                html.P("El proceso de carga del grafo puede tardar unos minutos.", className='text-light'),
                html.P('Puedes cerrar este cuadro.', className='text-light')
            ],
            class_name='bg-dark'
        ),
        dbc.ModalFooter(
            dbc.Button("Cerrar", id="modal-close", className="ml-auto text-info", n_clicks=0),
            class_name='bg-dark'
        ),
    ],
    id="modal-1",
    is_open=True,
)