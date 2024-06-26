from datetime import datetime
from datetime import timedelta
from pytz import timezone

from extract.extract_news import get_news, tz, today, time_delta, n
from config.db import conn
import spacy

nlp = spacy.load('es_core_news_md')


def extract_entities_spacy(extracted_raw_news=None, nlp=None) -> list:
    news_with_entities = []
    for (news_id, news_date, media_name, news_url, news_text, keywords) in extracted_raw_news:
        doc = nlp(news_text)
        news_with_entities.append(
            {
                'id': news_id,
                'entities': [{'entity': ent.text, 'entity_label': ent.label_} for ent in doc.ents if ent.label_ != 'MISC'],
                'media': media_name,
                'date': news_date,
                'url': news_url,
                'body_text': news_text,
                'keywords': keywords
            }
        )
    return news_with_entities


extracted_raw_news = get_news(
    connection=conn, # conn_postgresql
    table_name='news_chile',
    year=today.year,
    month=today.month,
    day=(today - time_delta).day,
    n=n
)

news_with_entities = extract_entities_spacy(extracted_raw_news=extracted_raw_news, nlp=nlp)