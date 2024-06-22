# Knowledge Graph a partir de noticias

Un visualizador simple de un *knowledge graph* construido a partir de noticias en español de Chile. El proyecto está alojado en *Railway*: https://news-kg-production.up.railway.app/

[Desentraña la red de noticias](https://news-kg-production.up.railway.app/)

## *scraping* de noticias

El listado de medios (sitios web de noticias) han sido obtenidos de [Prensa Escrita](https://www.prensaescrita.com/#google_vignette).

La extracción de noticias (artículos) se realiza de forma concurrente haciendo uso de la biblioteca [newspaper4k](https://pypi.org/project/newspaper4k/), habiendose hecho pruebas con [Newspaper3k](https://github.com/codelucas/newspaper).

## Extracción de entidades y relaciones

Las entidades y relaciones entre estas últimas son extraídas con Spacy y por medio de consulta a un LLM *open-source*, [Mixtral 8x22B](https://mistral.ai/technology/#models).

De la cantidad todal de noticias extraídas cada cierta frecuencia, solo se procesan 100 con el LLM debido a los costos generados, almacenando las entidades extraídas, y otros datos al respecto, en una base MongoDB.

## Front-End

La *app* ha sido desarrollada con **Plotly Dash**, haciendo especial uso de [dashvis](https://pypi.org/project/dashvis/) para la visualización de la red.

**WORK IN PROGRESS**