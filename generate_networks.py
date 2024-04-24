def generate_kg_spacy(news_list:list=None, entity_types:list=None, colors:list=None, color_converter=None) -> tuple:
    from itertools import count
    all_entities = []
    for entity_list in [ent for ent in [l['entities'] for l in news_list]]:
        for ent in entity_list:
            all_entities.append(ent['entity'])
    all_entities = set(all_entities)
    news_ids = [n['id'] for n in news_list]
    max_news_id = max(news_ids)
    entity_ids = {ent: i for i, ent in enumerate(all_entities, max_news_id + 1)}
    max_entities_id = max(entity_ids.values())
    media_names = set([n['media'] for n in news_list])
    media_ids = {media: i for i, media in enumerate(media_names, max_entities_id + 1)}
    
    colors_for_nodes = {
        ent_label: color_converter(c) for ent_label, c in zip(entity_types, colors)
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
            'font': {
                'color': 'white',
                'size': 17
            }
        }
        nodes.append(media_dict)
    gen_id = count(1)
    for news_dict in news_list:
        entity_news_dict = {
            'id': news_dict['id'],
            'title': news_dict['url'],
            'label': f"{news_dict['body_text'][:26]}...",
            'group': 'NEWS',
            'color': colors_for_nodes['NEWS'],
            'shape': 'dot',
            'font': {
                'color': 'white',
                'size': 17
            }
        }
        nodes.append(entity_news_dict)
        edge_id = next(gen_id)
        if (news_dict['id'], media_ids[news_dict['media']]) not in set([(edge_dict['from'], edge_dict['to']) for edge_dict in edges]):
            edges.append(
                {
                    'id': edge_id,
                    'label': 'PUBLICADO_POR',
                    'from': news_dict['id'],
                    'to': media_ids[news_dict['media']],
                    'arrows': 'to',
                    'font': {
                        'color': '#D3D3D3',
                        'size': 10,
                        'strokeWidth': 0
                    }
                }
            )
        for ent in news_dict['entities']:
            if not ent['entity'] in [node['label'] for node in nodes]:
                entity_ent_dict = {
                    'id': entity_ids[ent['entity']],
                    'label': ent['entity'],
                    'group': 'ENTITY',
                    'title': ent['entity_label'],
                    'color': colors_for_nodes[ent['entity_label']],
                    'shape': 'dot',
                    'font': {
                        'color': 'white',
                        'size': 17
                    }
                }
                nodes.append(entity_ent_dict)
            edge_id = next(gen_id)
            if (entity_ids[ent['entity']], news_dict['id']) not in set([(edge_dict['from'], edge_dict['to']) for edge_dict in edges]):
                edges.append(
                    {
                        'id': next(gen_id),
                        'label': 'MENCIONADO_EN',
                        'from': entity_ids[ent['entity']],
                        'to': news_dict['id'],
                        'arrows': 'to',
                        'font': {
                        'color': '#D3D3D3',
                        'size': 10,
                        'strokeWidth': 0
                    }
                    }
            )
    
    data = {
            'nodes': nodes,
            'edges': edges
    }
    
    return data, list(media_names)


def generate_kg_llm(news_entities_llm=None, news_entities_spacy=None, news_ids_without_llm_entities:list=None):
    pass