from datetime import datetime, timedelta
from pytz import timezone

from extract.extract_news import get_news_from_table, n
from config.db import conn
from config.mongo import settings_for_mongo

import spacy
from pymongo import MongoClient

nlp = spacy.load("es_core_news_md")

mongo_client = MongoClient(
    settings_for_mongo.MONGO_URL
    # host=settings_for_mongo.MONGOHOST,
    # port=settings_for_mongo.MONGOPORT,
    # username=settings_for_mongo.MONGOUSER,
    # password=settings_for_mongo.MONGOPASSWORD,
)


def extract_entities_spacy(extracted_raw_news=None, nlp=None) -> list:
    news_with_entities = []
    for (
        news_id,
        news_date,
        media_name,
        news_url,
        news_text,
        keywords,
    ) in extracted_raw_news:
        doc = nlp(news_text)
        news_with_entities.append(
            {
                "id": news_id,
                "entities": [
                    {"entity": ent.text, "entity_label": ent.label_}
                    for ent in doc.ents
                    if ent.label_ != "MISC"
                ],
                "media": media_name,
                "date": news_date,
                "url": news_url,
                "body_text": news_text,
                "keywords": keywords,
            }
        )
    return news_with_entities


def extract_entities_llm(
    client=None,
    db_name: str = "news",
    collection_name: str = "news_entities",
    delta_days: int = 1,
) -> tuple:
    mongo_db = client[db_name]
    mongo_collection = mongo_db[collection_name]
    cl_tz = timezone("America/Santiago")
    today = datetime.today()
    today = today.replace(tzinfo=cl_tz)
    t_delta = timedelta(
        days=delta_days, hours=today.hour, minutes=today.minute, seconds=today.second
    )
    filter_datetime = today - t_delta
    news_objs = list(
        filter(
            lambda obj: datetime.strptime(obj["date"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=cl_tz
            )
            >= filter_datetime,
            (obj for obj in mongo_collection.find() if "date" in obj.keys()),
        )
    )
    news_objs_with_llm_entities = list(
        filter(lambda obj: len(obj["triplets"]), news_objs)
    )
    print(
        f"\t{len(news_objs_with_llm_entities)} News filtered in function extract_entities_llm"
    )
    news_ids_without_llm_entities = [
        obj["_id"]
        for obj in news_objs
        if obj["_id"] not in [n["_id"] for n in news_objs_with_llm_entities]
    ]

    return news_objs_with_llm_entities, news_ids_without_llm_entities


extracted_raw_news = get_news_from_table(
    connection=conn, table_name="news_chile", delta_days=2, n=n  # conn_postgresql
)

news_with_entities_spacy = extract_entities_spacy(
    extracted_raw_news=extracted_raw_news, nlp=nlp
)
news_with_entities_llm, news_ids_without_llm_entities = extract_entities_llm(
    client=mongo_client, delta_days=1
)

# print(f"Cantidad en llm entities: {len(news_with_entities_llm)}")
# print(f"Cantidad en spacy entities: {len(news_with_entities_spacy)}")

for news_dict in news_with_entities_llm:
    same_news = [
        news_data
        for news_data in news_with_entities_spacy
        if news_data["url"] == news_dict["url"]
    ][
        0
    ]  # news_data["url"]
    news_dict["body_text"] = same_news["body_text"]
    news_dict["media"] = same_news["media"]
    news_dict["id"] = news_dict["_id"]  # normalizar id de otra forma
    news_dict["date"] = datetime.strptime(news_dict["date"], "%Y-%m-%d %H:%M:%S")
