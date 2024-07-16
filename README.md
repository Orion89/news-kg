# Knowledge Graph a partir de noticias

Un visualizador simple de un *knowledge graph* construido a partir de noticias en español de Chile. El proyecto está alojado en *Railway*: https://news-kg-production.up.railway.app/

[Desentraña la red de noticias](https://news-kg-production.up.railway.app/)

## *scraping* de noticias

El listado de medios (sitios web de noticias) han sido obtenidos de [Prensa Escrita](https://www.prensaescrita.com/#google_vignette).

La extracción de noticias (artículos) se realiza de forma concurrente haciendo uso de la biblioteca [newspaper4k](https://pypi.org/project/newspaper4k/), habiendose hecho pruebas con [Newspaper3k](https://github.com/codelucas/newspaper).

Se extraen y visualizan *key words* de cada noticia haciendo uso de [pytextrank](https://pypi.org/project/pytextrank/), con el objetivo de distinguir los principales temas de cada artículo.

## Extracción de entidades y relaciones

Las entidades y relaciones entre estas últimas son extraídas con Spacy y por medio de consulta a un LLM *open-source*, [Mixtral 8x22B](https://mistral.ai/technology/#models).

De la cantidad todal de noticias extraídas cada cierta frecuencia, solo se procesan 100 con el LLM debido a los costos generados, almacenando las entidades extraídas, y otros datos al respecto, en una base MongoDB.

Tanto el *scraping* de noticias como la extracción de entidades y relaciones entre estas últimas se encuentra implenentado en el siguiente repositorio: [news-extractor](https://github.com/Orion89/news-extractor/tree/mistral-extractor).

## Front-End

La *app* ha sido desarrollada con **Plotly Dash**, haciendo especial uso de [dashvis](https://pypi.org/project/dashvis/) para la visualización de la red. ***Dashvis***, tal como se indica en su [repositorio](), es una implementación completa para Plotly Dash del objeto `Network` de [vis.js](https://visjs.github.io/vis-network/docs/network/).

Otras bibliotecas usadas en el *front*:

* [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

**WORK IN PROGRESS**