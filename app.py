from datetime import datetime
from datetime import timedelta
import os
from pytz import timezone
from urllib.parse import urlparse
import warnings
from dotenv import load_dotenv

load_dotenv()

from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets

# import matplotlib as mpl
from matplotlib.colors import rgb2hex
from matplotlib.cm import get_cmap

import pytextrank
from pymongo import MongoClient

from config.db import conn
from config.mongo import settings_for_mongo
from extract.extract_entities import (
    news_with_entities_spacy,
    nlp,
    extract_entities_spacy,
    extract_entities_llm,
    news_with_entities_llm,
)
from extract.extract_news import get_news_from_table, get_media_in_db, today, time_delta
from generate_networks import (
    generate_kg_spacy,
    generate_kg_llm,
)
from utils.utils import entity_types_list
from utils.get_size import getsize
from network_options.options import default_options_
from sections.header import header
from sections.modals import modal, modal_no_news
from sections.footer import main_footer


warnings.filterwarnings("ignore")

# news_with_entities_llm, news_ids_without_llm_entities = extract_entities_llm(
#     client=mongo_client, delta_days=1
# )

news_loaded = os.getenv("NEWS_LOADED")
print(f"News loaded?: {news_loaded}")
print(f"News processed with LLM: {len(news_with_entities_llm)}")
print(f"News processed with Spacy: {len(news_with_entities_spacy)}")
print("========== examples ==========")
print(news_with_entities_llm[0])
print()
# print(news_with_entities_llm[-1])
print("==============================")
# extraction types: LLM, SPACY, LLM+SPACY
ENTITY_EXTRACTION_TYPE = "LLM"

mongo_client = MongoClient(settings_for_mongo.MONGO_URL)

# app initializing and options
app = Dash(
    __name__,
    title="news Knowledge Graph",
    external_stylesheets=[
        dbc.themes.YETI,
        dbc.icons.BOOTSTRAP,
        stylesheets.VIS_NETWORK_STYLESHEET,
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    # suppress_callback_exceptions=True
)

app.css.config.serve_locally = True
server = app.server
nlp.add_pipe("textrank")
# Initialize KG
# EXTRACTION_METHOD = 'spacy'
colors = get_cmap("tab20").colors
news_with_entities = (
    news_with_entities_spacy
    if ENTITY_EXTRACTION_TYPE == "SPACY"
    else news_with_entities_llm
)
if ENTITY_EXTRACTION_TYPE == "SPACY":
    data_for_kg, _ = generate_kg_spacy(
        news_list=news_with_entities_spacy,
        entity_types=entity_types_list,
        colors=colors,
        color_converter=rgb2hex,
    )
    media_names = get_media_in_db(
        conn, year=today.year, month=today.month, day=(today - time_delta).day
    )
elif ENTITY_EXTRACTION_TYPE == "LLM":
    data_for_kg = generate_kg_llm(news_data_llm=news_with_entities_llm)
    media_names = list(
        set([urlparse(news_dict["url"]).netloc for news_dict in news_with_entities_llm])
    )
elif ENTITY_EXTRACTION_TYPE == "LLM+SPACY":
    raise NotImplementedError("El método aún no se implementa.")

# network_1 = DashNetwork(
#     id="kg_news-1",
#     style={"height": "800px", "width": "100%", "background": "#222222"},
#     data={"nodes": data_for_kg["nodes"], "edges": data_for_kg["edges"]},
#     options=default_options_,
#     enableHciEvents=True,
#     enablePhysicsEvents=False,
#     enableOtherEvents=False,
# )

# Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Desentraña la red de noticias",
                            className="text-start text-primary fw-bolder",
                            id="title-1",
                        )
                    ],
                    width={"size": 8, "offset": 0},
                ),
                dbc.Col([header]),
            ],
            class_name="mt-0 mb-3 pt-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            children=[
                                "Haz zoom y/o selecciona un nodo para ver más información.",
                            ],
                            className="text-light",
                        ),
                        modal,
                    ],
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    [html.P(id="text-date-1", className="text-info text-center fs-5")],
                    width={"size": 2},
                    align="end",
                ),
                dbc.Col(
                    [html.P(id="text-url-1", className="fs-6 text-white text-end")],
                    width={"size": 8},
                    align="end",
                ),
            ]
        ),
        dbc.Row(
            [
                # dbc.Col(
                #     [
                #        dcc.Dropdown(
                #             id='dropdown-3',
                #             clearable=False,
                #             multi=True,
                #             searchable=False,
                #             placeholder='Keywords de noticia seleccionada',
                #             maxHeight=800,
                #             className='bg-opacity-0 z-3 position-absolute',
                #             style={
                #                 'backgroundColor': 'transparent',
                #                 'width': '250px'
                #             #     'opacity': 0,
                #                 # 'position': 'absolute',
                #                 # 'left': 0,
                #                 # 'width': '100%',
                #             }
                #         )
                #     ],
                #     width={'size': 2, 'offset': 0},
                #     class_name='bg-opacity-0',
                #     align="start"
                # ),
                dbc.Col(
                    [
                        dcc.Interval(
                            id="load_interval",
                            interval=1 * 1000,
                            n_intervals=0,
                            max_intervals=1,
                        ),
                        dcc.Interval(
                            id="load_interval-2",
                            interval=1 * 1000,
                            n_intervals=0,
                            max_intervals=7,
                        ),
                        dcc.Dropdown(
                            id="dropdown-2",
                            clearable=False,
                            multi=True,
                            searchable=False,
                            placeholder="Keywords noticia seleccionada",
                            maxHeight=800,
                            className="bg-opacity-0 z-3 position-absolute",
                            style={
                                "backgroundColor": "transparent",
                                "width": "250px",
                                #     'opacity': 0,
                                # 'position': 'absolute',
                                # 'left': 0,
                                # 'width': '100%',
                            },
                        ),
                        ### Legend
                        html.Div(
                            children=[
                                html.P(
                                    children=[
                                        html.I(
                                            className="bi bi-circle-fill",
                                            style={"color": "#FB7F81"},
                                        ),
                                        html.Span(
                                            " Entidades", style={"color": "#FB7F81"}
                                        ),
                                    ],
                                    className="bg-opacity-0 z-3 position-absolute",  # position-absolute
                                    style={
                                        "backgroundColor": "transparent",
                                        "width": "250px",
                                        "top": 120,  # 90
                                        "right": 1,
                                    },
                                ),
                                html.P(
                                    children=[
                                        html.I(
                                            className="bi bi-circle-fill",
                                            style={"color": "#98C2FC"},
                                        ),
                                        html.Span(
                                            " Noticias", style={"color": "#98C2FC"}
                                        ),
                                    ],
                                    className="bg-opacity-0 z-3 position-absolute",  # position-absolute
                                    style={
                                        "backgroundColor": "transparent",
                                        "width": "250px",
                                        "top": 70,  # 40
                                        "right": 1,
                                    },
                                ),
                                html.P(
                                    children=[
                                        html.I(
                                            className="bi bi-circle-fill",
                                            style={"color": "#F2E9D4"},
                                        ),
                                        html.Span(
                                            " Medios", style={"color": "#F2E9D4"}
                                        ),
                                    ],
                                    className="bg-opacity-0 z-3 position-absolute",  # position-absolute
                                    style={
                                        "backgroundColor": "transparent",
                                        "width": "250px",
                                        "top": 45,  # 65 | 15
                                        "right": 1,
                                    },
                                ),
                            ],
                            style={"backgroundColor": "transparent", "top": 70},
                            className="z-3",
                        ),
                        dbc.Spinner(
                            children=[
                                html.Div(
                                    # children=[network_1],
                                    id="network-1",
                                    className="mt-0",
                                )
                            ],
                            id="spiner-1",
                            color="primary",
                            delay_show=8_000,
                            size="md",
                        ),
                        modal_no_news,
                    ],
                    width={"size": 12, "offset": 0},
                    align="start",
                )
            ],
            class_name="mt-1 mb-3",
            style={"background": "#222222"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="dropdown-1",
                            # options=[
                            #     {
                            #         "label": html.Span(
                            #             [
                            #                 html.I(className="bi bi-book"),
                            #                 " "
                            #                 + str(
                            #                     node_dict["label"]
                            #                 ),  # f"{str(node_dict["label"])}"
                            #             ],
                            #             className="bg-opacity-0",
                            #             style={
                            #                 "color": "white",
                            #                 "font-size": 16,
                            #                 "backgroundColor": "transparent",
                            #             },
                            #         ),
                            #         "value": str(node_dict["label"]),
                            #     }
                            #     for node_dict in data_for_kg["nodes"]
                            # ],
                            # value='Todos',
                            clearable=True,
                            multi=False,
                            searchable=True,
                            placeholder="Selecciona o busca una entidad",
                            className="bg-opacity-0",
                            style={"backgroundColor": "#222222"},
                        ),
                        dcc.Store(
                            id="store-1", storage_type="session"
                        ),  # store-1 for raw news from db
                        dcc.Store(
                            id="store-2", storage_type="session"
                        ),  # store-2 for info from llm processed news
                    ],
                    width={"size": 5, "offset": 0},
                ),
                dbc.Col(
                    [
                        html.P(
                            children=[
                                "Nodos en tonos rojos representan entidades (extraídas con Mixtral 8x22B y Spacy) mencionadas en noticias. Las aristas uniendo entidades corresponden a relaciones extraídas por el LLM y se identifican por su etiqueta."
                            ],
                            className="text-light text-end",
                        )
                    ]
                ),
            ],
            style={"background": "#222222"},
        ),
        dbc.Row(  # FOOTER
            [
                dbc.Col(
                    [main_footer],
                    class_name="mt-4",
                    width={"size": 12},
                )
            ],
            align="center",
            class_name="text-end",
            style={"background": "#222222"},
        ),
    ],
    fluid=True,
    style={"background": "#222222"},
    # class_name='bg-dark'
)


# @callback(
#     Output('text-url-1', 'children'),
#     Input('kg_news-1', 'selectNode'),
#     prevent_initial_call=True
# )
# def show_news_node_info(selected_node_dict):
#     if selected_node_dict:
#         # print(selected_node_dict)
#         node_selected_id = selected_node_dict['nodes'][0]
#         # print(node_selected_id)
#         selected_node = [node_dict for node_dict in data_for_kg['nodes'] if node_dict['id'] == node_selected_id]
#         if selected_node:
#             selected_node = selected_node[0]
#             if selected_node['title'] not in entity_types_list:
#                 return html.A(children=[f"{selected_node['title']}"], href=f"{selected_node['title']}", target='_blank')
#             else:
#                 return ''
#         else:
#             return ''
#     else:
#         return '' # no_update


@callback(
    # Output("kg_news-1", "data"),
    Output("network-1", "children"),
    Output("store-2", "data"),
    Output("dropdown-1", "options"),
    Input("load_interval", "n_intervals"),
)
def load_kg(n_intervals):
    news_with_entities_llm, _ = extract_entities_llm(client=mongo_client, delta_days=2)
    data_for_kg = generate_kg_llm(news_data_llm=news_with_entities_llm)
    kg_vis = DashNetwork(
        id="kg_news-1",
        style={"height": "800px", "width": "100%", "background": "#222222"},
        data={"nodes": data_for_kg["nodes"], "edges": data_for_kg["edges"]},
        options=default_options_,
        enableHciEvents=True,
        enablePhysicsEvents=False,
        enableOtherEvents=False,
    )
    # data for store-2
    news_info_processed_by_llm = {
        "ids": [news_dict["_id"] for news_dict in news_with_entities_llm],
        "urls": [news_dict["url"] for news_dict in news_with_entities_llm],
    }
    # options for dropdown-1
    options = [
        {
            "label": html.Span(
                [
                    html.I(className="bi bi-book"),
                    " " + str(node_dict["label"]),  # f"{str(node_dict["label"])}"
                ],
                className="bg-opacity-0",
                style={
                    "color": "white",
                    "font-size": 16,
                    "backgroundColor": "transparent",
                },
            ),
            "value": str(node_dict["id"]),
        }
        for node_dict in data_for_kg["nodes"]
    ]
    print(f"from load_kg: ids from mongo: {news_info_processed_by_llm['ids']}")
    return kg_vis, news_info_processed_by_llm, options


@callback(
    # Output("kg_news-1", "data"),
    Output("store-1", "data"),
    Input("load_interval", "n_intervals"),
    State("store-2", "data"),
    prevent_initial_call=True,
)
def load_data(n_intervals, data):
    news_with_entities_llm, _ = extract_entities_llm(client=mongo_client, delta_days=2)
    # data_for_kg = generate_kg_llm(news_data_llm=news_with_entities_llm)
    news_ids_from_mongo = data["ids"]
    raw_news_from_db = get_news_from_table(connection=conn, delta_days=2)
    raw_news_filterd_by_id = list(
        filter(lambda news_dict: news_dict[0] in news_ids_from_mongo, raw_news_from_db)
    )
    print(
        f"from load_data: len of raw_news_filtered_by_id: {len(raw_news_filterd_by_id)}"
    )
    return raw_news_filterd_by_id


@callback(
    Output("kg_news-1", "moveTo"),
    Input("load_interval-2", "n_intervals"),
    State("kg_news-1", "getViewPosition"),
)
def set_initial_move_and_zoom(n_intervals, pos):
    if n_intervals > 6:
        return {
            "options": {
                "position": {"x": pos["x"], "y": pos["y"]},
                "scale": 0.7,
                "offset": {"x": 0, "y": 0},
                "locked": False,
                "animation": (
                    {
                        "duration": 1500,
                        "easingFunction": "lienar",
                    }
                ),
            }
        }
    else:
        no_update


@callback(
    Output("text-url-1", "children"),
    Input("kg_news-1", "selectNode"),
    State("store-1", "data"),
    prevent_initial_call=True,
)
def show_news_node_info(selected_node_dict, data):
    data = data if data else news_with_entities
    if selected_node_dict:
        print(f"selected node from show_news_node_info: {selected_node_dict}")
        # print(selected_node_dict)
        node_selected_id = selected_node_dict["nodes"][0]
        # print(node_selected_id)
        selected_node = [
            node_dict for node_dict in data if node_dict["_id"] == node_selected_id
        ]
        if selected_node:
            selected_node = selected_node[0]
            return html.A(
                children=[f"{selected_node['url']}"],
                href=f"{selected_node['url']}",
                target="_blank",
            )
        else:
            return ""
    else:
        return ""  # no_update


@callback(
    Output("kg_news-1", "focus"),
    Input("dropdown-1", "value"),
    prevent_initial_call=True,
)
def focus_on_selected_entity(selected_node):
    print(f"from focus_on_selected_entity: {selected_node}")
    if not selected_node:
        return no_update
    # nodes = data_for_kg["nodes"]
    # selected_node_info = [
    #     node_dict for node_dict in nodes if node_dict["label"] == selected_node
    # ][0]
    # print(selected_node_info)
    return {
        "nodeId": str(selected_node),
        "options": {
            "scale": 0.4,
            "offset": {"x": 0.01, "y": 0.01},
            "locked": False,
            "animation": {"duration": 2000, "easingFunction": "linear"},
        },
    }


@callback(
    Output("text-date-1", "children"),
    Input("kg_news-1", "selectNode"),
    State("store-1", "data"),
    prevent_initial_call=True,
)
def show_news_date(selected_node_dict, data):
    if not selected_node_dict:
        return ""
    print(f"selected node from show_news_date: {selected_node_dict}")
    data = data if data else news_with_entities
    # print(f"data from show_news_data: {data[:5]}")
    if selected_node_dict and data:
        node_selected_id = selected_node_dict["nodes"][0]
        selected_node_dict = [
            node_dict for node_dict in data if node_dict["_id"] == node_selected_id
        ]
        if selected_node_dict:
            try:
                selected_node_dict = selected_node_dict[0]
                print(f"Noticias obtenidas: {len(news_with_entities_llm)}")
                date_text = (
                    f'Noticia del {selected_node_dict["date"].strftime("%d-%m-%Y")}'
                )
            except Exception as e:
                return ""
            else:
                return date_text
        else:
            return ""
    else:
        return ""  # no_update


@callback(
    Output("dropdown-2", "options"),
    Output("dropdown-2", "value"),
    Input("kg_news-1", "selectNode"),
    State("store-1", "data"),
    prevent_initial_call=True,
)
def get_keywords(selected_node_dict, data):
    # print(selected_node_dict)
    if not selected_node_dict:
        return [{"label": "", "value": ""}], [""]
    if not data:
        data = news_with_entities  # return [{'label': '', 'value': ''}], ['']
    print(f"selected node from get_keywords: {selected_node_dict}")
    # print(f"data from get_keywords: {data[:5]}")
    n = 5
    node_selected_id = selected_node_dict["nodes"][0]
    selected_news = [
        news_dict for news_dict in data if news_dict["_id"] == node_selected_id
    ]
    if selected_news:
        selected_news = selected_news[0]
    else:
        return [{"label": "", "value": ""}], [""]
    if selected_news["body_text"]:
        doc_ = nlp(selected_news["body_text"])
        options = []
        value = []
        for kw in doc_._.phrases[:n]:
            if kw.text not in [token for token in doc_ if not token.is_stop]:
                options.append({"label": kw.text, "value": kw.text})
                value.append(kw.text)
        return options, value
    else:
        return [{"label": "", "value": ""}], [""]


# @callback(
#     Output("kg_news-1", "data"),
#     Output("store-1", "data"),
#     Output("modal-2", "is_open", allow_duplicate=True),
#     Input("dropdown-1", "value"),
#     prevent_initial_call=True,
# )
# def update_kg_1(selected_media):
#     if selected_media == "Todos":
#         return (
#             {"nodes": data_for_kg["nodes"], "edges": data_for_kg["edges"]},
#             news_with_entities,
#             False,
#         )
#     else:
#         print(f"Se ha seleccionado un medio: {selected_media}")
#         # news_with_entities_filtered = [
#         #     news_dict for news_dict in news_with_entities if news_dict['media'] == selected_media
#         # ]
#         n = 100
#         today = datetime.today()
#         tz = timezone("UTC")
#         today = today.replace(tzinfo=tz)
#         extracted_raw_news = get_news(
#             connection=conn,
#             table_name="news_chile",
#             delta_days=1,
#             media_name=selected_media,
#             n=n,
#         )
#         try:
#             if ENTITY_EXTRACTION_TYPE == "SPACY":
#                 news_with_entities_filtered = extract_entities_spacy(
#                     extracted_raw_news=extracted_raw_news, nlp=nlp
#                 )
#             elif ENTITY_EXTRACTION_TYPE == "LLM":
#                 news_with_entities_filtered = [
#                     news_dict
#                     for news_dict in news_with_entities_llm
#                     if news_dict["media"] == selected_media
#                 ]
#         except Exception as e:
#             print(f"An error has ocurred in getting news from {selected_media}:\n{e}")
#             return no_update, no_update, True
#         if len(news_with_entities_filtered) == 0:
#             print(f"\t{selected_media} sin artículos disponibles")
#             return no_update, no_update, True

#         if ENTITY_EXTRACTION_TYPE == "SPACY":
#             data, _ = generate_kg_spacy(
#                 news_list=news_with_entities_filtered,
#                 entity_types=entity_types_list,
#                 colors=colors,
#                 color_converter=rgb2hex,
#             )
#         elif ENTITY_EXTRACTION_TYPE == "LLM":
#             data = generate_kg_llm(news_data_llm=news_with_entities_filtered)

#         return (
#             {"nodes": data["nodes"], "edges": data["edges"]},
#             news_with_entities_filtered,
#             False,
#         )


@callback(
    Output("modal-1", "is_open"),
    Input("modal-close-1", "n_clicks"),
    prevent_initial_call=True,
)
def control_modal_1(click_button):
    if click_button:
        return False


@callback(
    Output("modal-2", "is_open"),
    Input("modal-close-2", "n_clicks"),
    prevent_initial_call=True,
)
def control_modal_2(click_button):
    if click_button:
        return False


if __name__ == "__main__":
    app.run(
        debug=False,
        host=os.getenv("HOST", default="0.0.0.0"),
        port=os.getenv("PORT", default="8050"),
    )  # host=os.getenv("HOST", default='0.0.0.0'),
