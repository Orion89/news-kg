height_ = "100%"
width_ = "100%"

nodes_ = {
    "shape": "box",
    "margin": 10,
    "size": 25,
    "borderWidth": 2,
    "borderWidthSelected": 2,
    "font": {
        "multi": "markdown",
        "align": "center",
    },
    "labelHighlightBold": True,
    "widthConstraint": {
        "minimum": 30,
        "maximum": 100,
    },
}

edges_ = {
    "color": {
        "inherit": "both",
    },
    "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
    "chosen": False,
    "arrowStrikethrough": False,
    "smooth": {"type": "dynamic", "roundness": 0.5, "avoidOverlap": 0.5},
}

physics_ = {
    "enabled": True,
    "barnesHut": {
        "gravitationalConstant": -5_000,
        "centralGravity": 0,
        "springLength": 350,
        "springConstant": 0.009,
        "damping": 0.025,
        "avoidOverlap": 0.1,
    },
    "stabilization": {"iterations": 250},
}

manipulation_ = {
    "enabled": False,
    "initiallyActive": False,
    #     'addNode': """function(nodeData,callback) {
    #       nodeData.label = 'hello world';
    #       callback(nodeData);
    # }""",
    "addEdge": False,
    "addNode": False,
    "editNode": None,
    "editEdge": False,
    "deleteNode": False,
    "deleteEdge": False,
}

interaction_ = {
    "hover": True,
    "hoverConnectedEdges": True,
    # 'multiselect': True,
    # 'keyboard': {
    #     'enabled': True,
    #     'bindToWindow': False,
    #     'autoFocus': True,
    # },
    "selectable": True,
    "tooltipDelay": 200,
    # 'navigationButtons': True,
}

layout_ = {
    "improvedLayout": True,
}

configure_ = {
    "enabled": False,
    "showButton": False,
}
# '"Font Awesome 6 Free"'
groups_ = {
    "MEDIA": {
        "shape": "icon",
        "icon": {"face": '"FontAwesome"', "code": "\uf1ea", "size": 60},
    },
    "NEWS": {
        "shape": "icon",
        "icon": {"face": '"FontAwesome"', "code": "\uf15b", "size": 45},
    },
    "ENTITIES": {
        "shape": "icon",
        "icon": {"face": '"FontAwesome"', "code": "\uf2bd", "size": 35},
    },
}

default_options_ = dict(
    autoResize=True,
    # height=height_,
    # width=width_,
    locale="es",
    configure=configure_,
    # nodes=nodes_,
    # edges=edges_,
    layout=layout_,
    interaction=interaction_,
    # manipulation=manipulation_,
    # physics=physics_,
)
