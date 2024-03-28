import warnings

from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets
# import matplotlib as mpl
from matplotlib.colors import rgb2hex
from matplotlib.cm import get_cmap

from extract_entities import news_with_entities
from generate_networks import generate_kg
from utils import entity_types_list
from network_options.options import default_options_


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
                width={'size': 10, 'offset': 1}
            )
        ],
        class_name='mt-1 mb-3'
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
                )
            ]
        )
    ],
    fluid=True,
    class_name='bg-dark'
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
    # prevent_initial_call=True
)
def show_news_node_info(selected_node_dict):
    if selected_node_dict:
        # print(selected_node_dict)
        node_selected_id = selected_node_dict['nodes'][0]
        print(node_selected_id)
        for node_dict in data_for_kg['nodes']:
            if node_dict['id'] == node_selected_id and node_dict['title']:
                return f"{node_dict['title']}"
            else:
                return ''
    else:
        return no_update
    
    
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