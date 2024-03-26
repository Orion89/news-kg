from dash import Dash, html, dcc, Input, Output, callback, no_update
import dash
import dash_bootstrap_components as dbc
from dashvis import DashNetwork
import matplotlib as mpl

from extract_entities import news_with_entities
from utils import entity_types_list

app = Dash(
    __name__,
    title='news graph',
    external_stylesheets=[
        dbc.themes.YETI,
        dbc.icons.BOOTSTRAP
    ],
     meta_tags=[
        {'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'}
    ]
)

app.layout = dbc.Container(
    [
      dbc.Row(
        [
            dbc.Col(
                [
                    html.H1('Desentraña la red de noticias', className='text-center')
                ],
                width={'size': 10, 'offset': 1}
            )
        ],
        class_name='mt-1 mb-3 bg-light'
    ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Visualiza los protagonistas de las noticias de hoy")
                    ],
                    width={'size': 3, 'offset': 0}
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id='network-1')
                    ],
                    width={'size': 12}
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='dropdown-1',
                            options=[
                                {'label': 'El Mercurio', 'value': 'El Mercurio'},
                                {'label': 'La Discursión', 'value': 'La Discusión'}
                            ],
                            value='El Mercurio'
                        )
                    ],
                    width={'size': 4, 'offset': 0}
                )
            ]
        )
    ],
    fluid=True
)

# print(len(news_with_entities))
# print(news_with_entities[2])

@callback(
    Output('network-1', 'children'),
    Input('dropdown-1', 'value')
)
def generate_kg(media_name):
    all_entities = []
    for entity_list in [ent for ent in [l['entities'] for l in news_with_entities]]:
        for ent in entity_list:
            all_entities.append(ent['entity'])
    all_entities = set(all_entities)
    news_ids = [n['id'] for n in news_with_entities]
    max_news_id = max(news_ids)
    entity_ids = {ent: i for i, ent in enumerate(all_entities, max_news_id + 1)}
    max_entities_id = max(entity_ids.values())
    media_names = set([n['media'] for n in news_with_entities])
    media_ids = {media: i for i, media in enumerate(media_names, max_entities_id + 1)}
    
    colors_for_nodes = {
        ent_label: mpl.colors.rgb2hex(c) for ent_label, c in zip(entity_types_list, mpl.cm.get_cmap('tab20').colors)
    }
    # usar algún método chain para crear nodos con sus ids?
    nodes = []
    edges = []
    for media in media_names:
        media_dict = {
            'id': media_ids[media],
            'label': media,
            'title': media,
            'group': 'MEDIA',
            'color': colors_for_nodes['MEDIA'],
            'shape': 'dot',
            'font': {'color': 'white'}
        }
        nodes.append(media_dict)
    for news_dict in news_with_entities:
        entity_news_dict = {
            'id': news_dict['id'],
            'title': news_dict['url'],
            'label': news_dict['body_text'][:20],
            'group': 'NEWS',
            'color': colors_for_nodes['NEWS'],
            'shape': 'dot',
            'font': {'color': 'white'}
        }
        edges.append(
            {
                'label': 'PUBLICADO_POR',
                'from': news_dict['id'],
                'to': media_ids[news_dict['media']],
                'arrows': 'to'
            }
        )
        nodes.append(entity_news_dict)
        for ent in news_dict['entities']:
            if not ent['entity'] in [node['label'] for node in nodes]:
                entity_ent_dict = {
                    'id': entity_ids[ent['entity']],
                    'label': ent['entity'],
                    'group': 'ENTITY',
                    'title': ent['entity_label'],
                    'color': colors_for_nodes[ent['entity_label']],
                    'shape': 'dot',
                    'font': {'color': 'white'}
                }
                nodes.append(entity_ent_dict)
            edges.append(
                {
                    'label': 'MENCIONADO_EN',
                    'from': entity_ids[ent['entity']],
                    'to': news_dict['id'],
                    'arrows': 'to'
                }
            )
    
    network = DashNetwork(
        id='kg_news-1',
        style={
            'height': '800px',
            'width': '100%'
        },
        data={
            'nodes': nodes,
            'edges': edges
        }
    )
    
    return network
    
    
if __name__ == '__main__':
    app.run(debug=True, port='8050')