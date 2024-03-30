import warnings

from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets
# import matplotlib as mpl
from matplotlib.colors import rgb2hex
from matplotlib.cm import get_cmap

import pytextrank

from extract_entities import news_with_entities, nlp
from generate_networks import generate_kg
from utils import entity_types_list
from network_options.options import default_options_
from sections.header import header


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
nlp.add_pipe("textrank")
# Initia KG
colors = get_cmap('tab20').colors
data_for_kg, media_names = generate_kg(
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
                        html.P("Visualiza los protagonistas de las noticias de hoy", className='text-light')
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
                            size='md'
                        )
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
                        )
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

# Callbacks

# @callback(
#     Output('network-1', 'children'),
#     Input('dropdown-1', 'value')
# )
# def generate_kg(media_name):
#     all_entities = []
#     for entity_list in [ent for ent in [l['entities'] for l in news_with_entities]]:
#         for ent in entity_list:
#             all_entities.append(ent['entity'])
#     all_entities = set(all_entities)
#     news_ids = [n['id'] for n in news_with_entities]
#     max_news_id = max(news_ids)
#     entity_ids = {ent: i for i, ent in enumerate(all_entities, max_news_id + 1)}
#     max_entities_id = max(entity_ids.values())
#     media_names = set([n['media'] for n in news_with_entities])
#     media_ids = {media: i for i, media in enumerate(media_names, max_entities_id + 1)}
    
#     colors_for_nodes = {
#         ent_label: mpl.colors.rgb2hex(c) for ent_label, c in zip(entity_types_list, mpl.cm.get_cmap('tab20').colors)
#     }
#     # usar algún método chain para crear nodos con sus ids?
#     nodes = []
#     edges = []
#     for media in media_names:
#         media_dict = {
#             'id': media_ids[media],
#             'label': media,
#             'title': media,
#             'group': 'MEDIA',
#             'color': colors_for_nodes['MEDIA'],
#             'shape': 'dot',
#             'font': {
#                 'color': 'white',
#                 'size': 17
#             }
#         }
#         nodes.append(media_dict)
#     for news_dict in news_with_entities:
#         entity_news_dict = {
#             'id': news_dict['id'],
#             'title': news_dict['url'],
#             'label': news_dict['body_text'][:20],
#             'group': 'NEWS',
#             'color': colors_for_nodes['NEWS'],
#             'shape': 'dot',
#             'font': {
#                 'color': 'white',
#                 'size': 17
#             }
#         }
#         edges.append(
#             {
#                 'label': 'PUBLICADO_POR',
#                 'from': news_dict['id'],
#                 'to': media_ids[news_dict['media']],
#                 'arrows': 'to',
#                 'font': {
#                     'color': '#D3D3D3',
#                     'size': 12,
#                     'strokeWidth': 0
#                 }
#             }
#         )
#         nodes.append(entity_news_dict)
#         for ent in news_dict['entities']:
#             if not ent['entity'] in [node['label'] for node in nodes]:
#                 entity_ent_dict = {
#                     'id': entity_ids[ent['entity']],
#                     'label': ent['entity'],
#                     'group': 'ENTITY',
#                     'title': ent['entity_label'],
#                     'color': colors_for_nodes[ent['entity_label']],
#                     'shape': 'dot',
#                     'font': {
#                         'color': 'white',
#                         'size': 17
#                     }
#                 }
#                 nodes.append(entity_ent_dict)
#             edges.append(
#                 {
#                     'label': 'MENCIONADO_EN',
#                     'from': entity_ids[ent['entity']],
#                     'to': news_dict['id'],
#                     'arrows': 'to',
#                     'font': {
#                     'color': '#D3D3D3',
#                     'size': 12,
#                     'strokeWidth': 0
#                 }
#                 }
#             )
    
#     network = DashNetwork(
#         id='kg_news-1',
#         style={
#             'height': '800px',
#             'width': '100%',
#             'background': "#222222"
#         },
#         data={
#             'nodes': nodes,
#             'edges': edges
#         }
#     )
    
#     return data


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
        selected_node = [node_dict for node_dict in data_for_kg['nodes'] if node_dict['id'] == node_selected_id][0]
        if selected_node['title']:
            return f"{selected_node['title']}"
        else:
            return ''
    else:
        return no_update
    
    
@callback(
    Output('dropdown-2', 'options'),
    Output('dropdown-2', 'value'),
    Input('kg_news-1', 'selectNode'),
    prevent_initial_call=True
)
def get_keywords(selected_node_dict):
    n = 5
    node_selected_id = selected_node_dict['nodes'][0]
    selected_news = [news_dict for news_dict in news_with_entities if news_dict['id'] == node_selected_id][0]
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
    Input('dropdown-1', 'value'),
    prevent_initial_call=True
)
def update_kg_1(selected_media):
    if selected_media == 'Todos':
        return {'nodes': data_for_kg['nodes'], 'edges': data_for_kg['edges']}
    else:
        news_with_entities_filtered = [
            news_dict for news_dict in news_with_entities if news_dict['media'] == selected_media 
        ]
        data, _ = generate_kg(
            news_list=news_with_entities_filtered,
            entity_types=entity_types_list,
            colors=colors,
            color_converter=rgb2hex
        )
    
        return {'nodes': data['nodes'], 'edges': data['edges']}
    
    
if __name__ == '__main__':
    app.run(debug=True, port='8050')