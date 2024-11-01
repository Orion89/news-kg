from itertools import count
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse


# static_folder_path = Path("./static/")
node_type_to_icon = {
    "media": "static/newspaper-regular.svg",
    "news": "static/envelope-open-text-solid.svg",
    "Action": "static/arrows-alt-svgrepo-com.svg",  # rgb(219, 40, 73)
    "BioChemEntity": "static/flask-vial-solid.svg",
    "CreativeWork": "static/paintbrush-solid.svg",
    "Event": "static/calendar-check-regular.svg",
    "Intangible": "static/eye-solid.svg",
    "MedicalEntity": "static/notes-medical-solid.svg",
    "Organization": "static/organization-svgrepo-com.svg",  # rgb(177, 151, 252)
    "Person": "static/circle-user-solid.svg",
    "Place": "static/location-pin-svgrepo-com.svg",  # rgb(22, 171, 22)
    "Product": "static/product-workspace-svgrepo-com.svg",  # rgb(142, 203, 203)
    "Taxon": "static/category-list-solid-svgrepo-com.svg",  # rgb(0, 158, 219)
    "Boolean": "static/boolean-svgrepo-com.svg",  # rgb(143, 163, 188)
    "Date": "static/date-2-svgrepo-com.svg",  # rgb(143, 163, 188)
    "DateTime": "static/clock-svgrepo-com.svg",  # rgb(143, 163, 188)
    "Number": "static/number-sign-110-svgrepo-com.svg",  # rgb(143, 163, 188)
    "Text": "static/text-square-svgrepo-com.svg",  # rgb(143, 163, 188)
    "Time": "static/time-svgrepo-com.svg",  # rgb(143, 163, 188)
}


def generate_kg_spacy(
    news_list: list = None,
    entity_types: list = None,
    colors: list = None,
    color_converter=None,
) -> tuple:
    all_entities = []
    for entity_list in [ent for ent in [l["entities"] for l in news_list]]:
        for ent in entity_list:
            all_entities.append(ent["entity"])
    all_entities = set(all_entities)
    news_ids = [n["id"] for n in news_list]
    max_news_id = max(news_ids)
    entity_ids = {ent: i for i, ent in enumerate(all_entities, max_news_id + 1)}
    max_entities_id = max(entity_ids.values())
    media_names = set([n["media"] for n in news_list])
    media_ids = {media: i for i, media in enumerate(media_names, max_entities_id + 1)}

    colors_for_nodes = {
        ent_label: color_converter(c) for ent_label, c in zip(entity_types, colors)
    }
    # usar algún método chain para crear nodos con sus ids?
    nodes = []
    edges = []
    for media in media_names:
        media_dict = {
            "id": media_ids[media],
            "label": media,
            "title": media,
            "group": "MEDIA",
            "color": colors_for_nodes["MEDIA"],
            "shape": "dot",
            "font": {"color": "white", "size": 17},
        }
        nodes.append(media_dict)
    gen_id = count(1)
    for news_dict in news_list:
        entity_news_dict = {
            "id": news_dict["id"],
            "title": news_dict["url"],
            "label": f"{news_dict['body_text'][:26]}...",
            "group": "NEWS",
            "color": colors_for_nodes["NEWS"],
            "shape": "dot",
            "font": {"color": "white", "size": 17},
        }
        nodes.append(entity_news_dict)
        edge_id = next(gen_id)
        if (news_dict["id"], media_ids[news_dict["media"]]) not in set(
            [(edge_dict["from"], edge_dict["to"]) for edge_dict in edges]
        ):
            edges.append(
                {
                    "id": edge_id,
                    "label": "PUBLICADO_POR",
                    "from": news_dict["id"],
                    "to": media_ids[news_dict["media"]],
                    "arrows": "to",
                    "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                }
            )
        for ent in news_dict["entities"]:
            if not ent["entity"] in [node["label"] for node in nodes]:
                entity_ent_dict = {
                    "id": entity_ids[ent["entity"]],
                    "label": ent["entity"],
                    "group": "ENTITY",
                    "title": ent["entity_label"],
                    "color": colors_for_nodes[ent["entity_label"]],
                    "shape": "dot",
                    "font": {"color": "white", "size": 17},
                }
                nodes.append(entity_ent_dict)
            edge_id = next(gen_id)
            if (entity_ids[ent["entity"]], news_dict["id"]) not in set(
                [(edge_dict["from"], edge_dict["to"]) for edge_dict in edges]
            ):
                edges.append(
                    {
                        "id": next(gen_id),
                        "label": "MENCIONADO_EN",
                        "from": entity_ids[ent["entity"]],
                        "to": news_dict["id"],
                        "arrows": "to",
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                    }
                )

    data = {"nodes": nodes, "edges": edges}

    return data, list(media_names)


def generate_kg_llm_and_spacy(
    news_entities_llm=None,
    news_entities_spacy=None,
    news_ids_without_llm_entities: list = None,
) -> Dict[str, List]:
    news_data = news_entities_llm + news_entities_spacy  # solo placeholder, desarrollar
    nodes = []
    edges = []

    news_media = set([urlparse(news_dict["url"]).netloc for news_dict in news_data])
    news_ids = set([news_dict["_id"] for news_dict in news_data])
    media_ids = {media: i for i, media in enumerate(list(news_media))}
    for media_name in list(news_media):
        media_node = {
            "id": media_ids[media_name],
            "label": media_name,
            "title": media_name,
            "group": "MEDIA",
            "shape": "dot",
            "font": {"color": "white", "size": 17},
        }
        nodes.append(media_node)

    node_id_generator = count(max(news_ids) + 1)
    edge_id_generator = count(1)
    for data_dict in news_data:
        news_node = {
            "id": data_dict["_id"],
            "title": data_dict["url"],
            "label": f"noticia_{data_dict['_id']}",
            "group": "NEWS",
            # 'color': colors_for_nodes['NEWS'],
            "shape": "dot",
            "font": {"color": "white", "size": 17},
        }
        nodes.append(news_node)
        edge_id = next(edge_id_generator)
        news_to_media_edge = {
            "id": edge_id,
            "label": "PUBLICADO_POR",
            "from": data_dict["_id"],
            "to": media_ids[urlparse(data_dict["url"]).netloc],
            "arrows": "to",
            "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
        }
        edges.append(news_to_media_edge)
        for triple in data_dict["entities"]:
            if not triple["head"] in [node["label"] for node in nodes]:
                head_added = False
                tail_added = False
                head_id = next(node_id_generator)
                head_node = {
                    "id": head_id,
                    "label": triple["head"],
                    "title": triple["type_head"],
                    "group": "ENTITIES",
                    "shape": "dot",
                    "mass": 7,
                    "font": {"color": "white", "size": 17},
                }
                nodes.append(head_node)
                head_added = True
            if not triple["tail"] in [node["label"] for node in nodes]:
                tail_id = next(node_id_generator)
                tail_node = {
                    "id": tail_id,
                    "label": triple["tail"],
                    "title": triple["type_tail"],
                    "group": "ENTITIES",
                    "shape": "dot",
                    "mass": 7,
                    "font": {"color": "white", "size": 17},
                }
                nodes.append(tail_node)
                tail_added = True
            if head_added or tail_added:
                if (head_id, tail_id) not in [
                    (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
                ]:
                    edge_id = next(
                        edge_id_generator
                    )  # Filtrar edge para evitar edges duplicados
                    head_to_tail_edge = {
                        "id": edge_id,
                        "label": triple["relation"],
                        "from": head_id,
                        "to": tail_id,
                        "arrows": "to",
                        "length": 300,
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                    }
                    edges.append(head_to_tail_edge)
            if head_added:
                if (head_id, data_dict["_id"]) not in [
                    (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
                ]:
                    edge_id = next(edge_id_generator)
                    head_to_news_edge = {
                        "id": edge_id,
                        "label": "MENCIONADO_EN",
                        "from": head_id,
                        "to": data_dict["_id"],
                        "arrows": "to",
                        "hidden": True,
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                    }
                    edges.append(head_to_news_edge)
            if tail_added:
                if (tail_id, data_dict["_id"]) not in [
                    (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
                ]:
                    edge_id = next(edge_id_generator)
                    tail_to_news_edge = {
                        "id": edge_id,
                        "label": "MENCIONADO_EN",
                        "from": tail_id,
                        "to": data_dict["_id"],
                        "arrows": "to",
                        "hidden": True,
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                    }
                    edges.append(tail_to_news_edge)

    return {"nodes": nodes, "edges": edges}


def generate_kg_llm(news_data_llm) -> Dict[str, List]:
    nodes = []
    edges = []

    news_media = set([urlparse(news_dict["url"]).netloc for news_dict in news_data_llm])
    news_ids = set([news_dict["_id"] for news_dict in news_data_llm])
    media_ids = {media: i for i, media in enumerate(list(news_media))}
    for media_name in list(news_media):
        media_node = {
            "id": media_ids[media_name],
            "size": 60,
            "label": media_name,
            "title": media_name,
            "mass": 10,
            "group": "MEDIA",
            "shape": "image",
            "image": "static/newspaper-regular.svg",
            "font": {
                "color": "white",
                "size": 48,
                "bold": {"color": "white", "size": 30, "face": "arial", "mod": "bold"},
            },
        }
        nodes.append(media_node)

    node_id_generator = count(max(news_ids) + 1)
    edge_id_generator = count(1)
    for data_dict in news_data_llm:
        news_node = {
            "id": data_dict["_id"],
            "size": 45,
            "title": data_dict["url"],
            "label": f"noticia_{data_dict['_id']}",
            "mass": 7,
            "group": "NEWS",
            # 'color': colors_for_nodes['NEWS'],
            "shape": "image",
            "image": "static/envelope-open-text-solid.svg",
            "font": {"color": "white", "size": 26},
        }
        nodes.append(news_node)
        edge_id = next(edge_id_generator)
        news_to_media_edge = {
            "id": edge_id,
            "label": "PUBLICADO_POR",
            "length": 275,
            "from": data_dict["_id"],
            "to": media_ids[urlparse(data_dict["url"]).netloc],
            "arrows": "to",
            "font": {"color": "#D3D3D3", "size": 14, "strokeWidth": 0},
            "color": {"color": "#9ecae1"},
            "width": 1.5,
        }
        edges.append(news_to_media_edge)
        for triple in data_dict["triplets"]:
            if (
                "head" not in triple
                or "tail" not in triple
                or "type_tail" not in triple
                or "type_head" not in triple
            ):
                continue
            head_added = False
            tail_added = False
            if not triple["head"] in [node["label"] for node in nodes]:
                head_id = next(node_id_generator)
                head_node = {
                    "id": head_id,
                    "label": triple["head"],
                    "size": 35,
                    "title": triple["type_head"],
                    "group": "ENTITIES",
                    "shape": "image",
                    "image": node_type_to_icon.get(
                        triple["type_head"], "static/dot-svgrepo-com.svg"
                    ),  # "static/circle-user-solid.svg",
                    "mass": 4,
                    "font": {"color": "white", "size": 32},
                }
                nodes.append(head_node)
                head_added = True
            if not triple["tail"] in [node["label"] for node in nodes]:
                tail_id = next(node_id_generator)
                tail_node = {
                    "id": tail_id,
                    "label": triple["tail"],
                    "size": 35,
                    "title": triple["type_tail"],
                    "group": "ENTITIES",
                    "shape": "image",
                    "image": node_type_to_icon.get(
                        triple["type_tail"], "static/dot-svgrepo-com.svg"
                    ),  # "static/circle-user-solid.svg",
                    "mass": 4,
                    "font": {"color": "white", "size": 32},
                }
                nodes.append(tail_node)
                tail_added = True
            # if head_added or tail_added:  # remover esta condición
            if (head_id, tail_id) not in [
                (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
            ]:
                edge_id = next(
                    edge_id_generator
                )  # Filtrar edge para evitar edges duplicados
                head_to_tail_edge = {
                    "id": edge_id,
                    "label": triple["relation"],
                    "from": head_id,
                    "to": tail_id,
                    "arrows": "to",
                    "length": 350,
                    "font": {"color": "#D3D3D3", "size": 22, "strokeWidth": 0},
                    "smooth": {"enabled": True, "type": "continuous"},
                    "width": 2.0,
                }
                edges.append(head_to_tail_edge)
            if head_added:
                if (head_id, data_dict["_id"]) not in [
                    (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
                ]:
                    edge_id = next(edge_id_generator)
                    head_to_news_edge = {
                        "id": edge_id,
                        "label": "MENCIONADO_EN",
                        "length": 375,
                        "from": head_id,
                        "to": data_dict["_id"],
                        "arrows": "to",
                        "hidden": True,
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                        "smooth": {"enabled": True, "type": "continuous"},
                    }
                    edges.append(head_to_news_edge)
            if tail_added:
                if (tail_id, data_dict["_id"]) not in [
                    (edge_dict["from"], edge_dict["to"]) for edge_dict in edges
                ]:
                    edge_id = next(edge_id_generator)
                    tail_to_news_edge = {
                        "id": edge_id,
                        "label": "MENCIONADO_EN",
                        "length": 375,
                        "from": tail_id,
                        "to": data_dict["_id"],
                        "arrows": "to",
                        "hidden": True,
                        "font": {"color": "#D3D3D3", "size": 10, "strokeWidth": 0},
                        "smooth": {"enabled": True, "type": "continuous"},
                    }
                    edges.append(tail_to_news_edge)

    return {"nodes": nodes, "edges": edges}
