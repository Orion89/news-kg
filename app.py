from datetime import datetime
from datetime import timedelta
import os
from pytz import timezone
import warnings

from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets
# import matplotlib as mpl
from matplotlib.colors import rgb2hex
from matplotlib.cm import get_cmap

import pytextrank

from config.db import conn
from extract.extract_entities import news_with_entities, nlp, extract_entities_spacy
from extract.extract_news import get_news, conn_postgresql, get_media_in_db
from generate_networks import generate_kg
from utils.utils import entity_types_list
from utils.get_size import getsize
from network_options.options import default_options_
from sections.header import header
from sections.modals import modal, modal_no_news


warnings.filterwarnings("ignore")

app = Dash(
    __name__,
    title='news graph',
    external_stylesheets=[
        dbc.themes.YETI,
        dbc.icons.BOOTSTRAP,
        stylesheets.VIS_NETWORK_STYLESHEET
    ],
    meta_tags=[
        {'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'}
    ],
    # suppress_callback_exceptions=True
)

app.css.config.serve_locally = True
server = app.server
nlp.add_pipe("textrank")
# Initia KG
colors = get_cmap('tab20').colors
data_for_kg, _ = generate_kg(
    news_list=news_with_entities,
    entity_types=entity_types_list,
    colors=colors,
    color_converter=rgb2hex
)
network_1 = DashNetwork(
            id='kg_news-1',
            style={
                'height': '800px',
                'width': '100%',
                'background': "#222222"
            },
            data={
                'nodes': data_for_kg['nodes'],
                'edges': data_for_kg['edges']
            },
            options=default_options_,
            enableHciEvents=True,
        enablePhysicsEvents=False,
        enableOtherEvents=False
)

today = datetime.today()
tz = timezone('UTC')
today = today.replace(tzinfo=tz)
time_delta = timedelta(days=7, hours=today.hour, minutes=today.minute)
media_names = get_media_in_db(conn, year=today.year, month=today.month, day=(today - time_delta).day)

# Layout
app.layout = dbc.Container(
    [
      dbc.Row(
        [
            dbc.Col(
                [
                    html.H1('Desentraña la red de noticias', className='text-center text-primary fw-bolder')
                ],
                width={'size': 8, 'offset': 0}
            ),
            dbc.Col(
                [
                    header
                ]
            )
        ],
        class_name='mt-2 mb-3'
    ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Haz zoom y/o selecciona un nodo para ver más información.", className='text-light'),
                        modal
                    ],
                    width={'size': 3, 'offset': 0}
                ),
                dbc.Col(
                    [
                        html.P(
                            id='text-url-1',
                            className='fs-6 text-white text-end'
                        )
                    ],
                    width={'size': 9},
                    align='end'
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Spinner(
                            children=[html.Div(
                                    id='network-1',
                                    children=[network_1]
                                )],
                            id='spiner-1',
                            color='primary',
                            delay_show=5_000,
                            size='md'
                        ),
                        modal_no_news
                    ],
                    width={'size': 12}
                )
            ],
            class_name='mt-1 mb-3'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='dropdown-1',
                            options=[{'label': 'Todos', 'value': 'Todos'}] + [
                                {'label': str(m), 'value': str(m)} for m in media_names
                            ],
                            # value='Todos',
                            placeholder="Selecciona un medio"
                        ),
                        dcc.Store(id='store-1', storage_type='session')
                    ],
                    width={'size': 4, 'offset': 0}
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='dropdown-2',
                            clearable=False,
                            multi=True,
                            searchable=False,
                            placeholder='Keywords de noticia seleccionada'
                        )
                    ]
                )
            ]
        ),
        dbc.Row( # FOOTER
            [
                dbc.Col(
                    [
                        # html.Div(id='user-info', className='invisible m-0'),
                        dbc.Card(
                            [
                                dbc.CardFooter(
                                    [
                                        html.P([
                                            html.A(
                                                children=[html.I(className="bi bi-github")],
                                                disable_n_clicks=True,
                                                href='https://github.com/Orion89',
                                                title="GitHub profile"
                                            ),
                                            "  ",
                                            html.A(
                                                children=[html.I(className="bi bi-linkedin")],
                                                disable_n_clicks=True,
                                                href='https://www.linkedin.com/in/leonardo-molina-v-68a601183/',
                                                title="LinkedIn profile"
                                            ),
                                            " 2024 Leonardo Molina V."
                                            ],
                                            className='fs-5 text-light'
                                        ),
                                        html.P(
                                            'Proyecto académico. El autor no se hace responsable del mal uso del contenido.',
                                            className='text-light'
                                        )
                                    ]
                                    
                                )
                            ],
                            style={
                                'background': '#222222'
                            }
                        )
                    ],
                    class_name='mt-4',
                    width={'size': 12},
                )
            ],
            align='center',
            class_name='text-end',
            style={
                'background': '#222222'
            }
        )
    ],
    fluid=True,
    style={
        'background': '#222222'
    }
    # class_name='bg-dark'
)


@callback(
    Output('text-url-1', 'children'),
    Input('kg_news-1', 'selectNode'),
    prevent_initial_call=True
)
def show_news_node_info(selected_node_dict):
    if selected_node_dict:
        # print(selected_node_dict)
        node_selected_id = selected_node_dict['nodes'][0]
        # print(node_selected_id)
        selected_node = [node_dict for node_dict in data_for_kg['nodes'] if node_dict['id'] == node_selected_id]
        if selected_node:
            selected_node = selected_node[0]
            if selected_node['title'] not in entity_types_list:
                return f"{selected_node['title']}"
            else:
                return ''
        else:
            return ''
    else:
        return '' # no_update
    
    
@callback(
    Output('dropdown-2', 'options'),
    Output('dropdown-2', 'value'),
    Input('kg_news-1', 'selectNode'),
    State('store-1', 'data'),
    prevent_initial_call=True
)
def get_keywords(selected_node_dict, data):
    if not data:
        data = news_with_entities # return [{'label': '', 'value': ''}], ['']
    n = 5
    node_selected_id = selected_node_dict['nodes'][0]
    selected_news = [news_dict for news_dict in data if news_dict['id'] == node_selected_id]
    if selected_news:
        selected_news = selected_news[0]
    else:
        return [{'label': '', 'value': ''}], ['']
    if selected_news['body_text']:
        doc_ = nlp(selected_news['body_text'])
        options = []
        value = []
        for kw in doc_._.phrases[:n]:
            if kw.text not in [token for token in doc_ if not token.is_stop]:
                options.append({'label': kw.text, 'value': kw.text})
                value.append(kw.text)
        return options, value
    else:
        return [{'label': '', 'value': ''}], ['']
    
    
@callback(
    Output('kg_news-1', 'data'),
    Output('store-1', 'data'),
    Output('modal-2', 'is_open', allow_duplicate=True),
    Input('dropdown-1', 'value'),
    prevent_initial_call=True
)
def update_kg_1(selected_media):
    if selected_media == 'Todos':
        return {'nodes': data_for_kg['nodes'], 'edges': data_for_kg['edges']}, news_with_entities, False
    else:
        print(f'Se ha seleccionado un medio: {selected_media}')
        # news_with_entities_filtered = [
        #     news_dict for news_dict in news_with_entities if news_dict['media'] == selected_media 
        # ]
        n = 100
        today = datetime.today()
        tz = timezone('UTC')
        today = today.replace(tzinfo=tz)
        time_delta = timedelta(days=4, hours=today.hour, minutes=today.minute)
        extracted_raw_news = get_news(
            connection=conn,
            table_name='news_chile',
            year=today.year,
            month=today.month,
            day=(today - time_delta).day,
            media_name=selected_media,
            n=n
        )
        try:
            news_with_entities_filtered = extract_entities_spacy(
                extracted_raw_news=extracted_raw_news,
                nlp=nlp
            )
        except Exception as e:
            print(f'An error has ocurred in getting news from {selected_media}:\n{e}')
            return no_update, no_update, True
        
        data, _ = generate_kg(
            news_list=news_with_entities_filtered,
            entity_types=entity_types_list,
            colors=colors,
            color_converter=rgb2hex
        )
    
        return {'nodes': data['nodes'], 'edges': data['edges']}, news_with_entities_filtered, False
    

@callback(
    Output('modal-1', 'is_open'),
    Input('modal-close-1', 'n_clicks'),
    prevent_initial_call=True
)
def control_modal_1(click_button):
    if click_button:
        return False

    
@callback(
    Output('modal-2', 'is_open'),
    Input('modal-close-2', 'n_clicks'),
    prevent_initial_call=True
)
def control_modal_2(click_button):
    if click_button:
        return False
    
    
if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", default='0.0.0.0'), port=os.getenv("PORT", default='8050'))