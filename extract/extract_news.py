from datetime import datetime, timedelta
from pytz import timezone
import re

import newspaper
import psycopg
# from medias.medias_list import medias_dict

today = datetime.today()
tz = timezone('UTC')
today = today.replace(tzinfo=tz)
time_delta = timedelta(days=2, hours=today.hour, minutes=today.minute)
n = 100

# conn_postgresql = psycopg.connect(
#     host="localhost",
#     dbname="news_kg_v1",
#     user="postgres",
#     password="0rioN-689"
# )


def news_extractor_per_media(country: str, medias:dict, today:datetime, t_delta:timedelta, conn):
    # query
    cursor = conn.cursor()
    cursor.execute(f'''SELECT url FROM {"news_" + country}''')
    saved_articles_urls = set([article[0] for article in cursor.fetchall()])
    # scrapings
    medias_urls = medias[country]
    for media in medias_urls:
        try:
            media_news = newspaper.build(media, memoize_articles=False, number_threads=4)
        except Exception as e:
            print(f"Ha ocurrido un error con {str(media)}:\n{e}")
            continue
        for art in media_news.articles:
            try:
                art.download()
                art.parse()
                if art.is_valid_body() and not art.is_media_news() and art.meta_lang == 'es' and art.publish_date >= (today - t_delta) and art.url not in saved_articles_urls:
                    media_name = art.source_url.partition('//')[-1][:149] if art.source_url else None
                    date = art.publish_date.strftime('%Y-%m-%d %H:%M:%S') if art.publish_date else None
                    authors = ' '.join(art.authors)[:149] if art.authors else None
                    url = art.url if art.url else None
                    body_text = art.text
                    keywords = ", ".join(art.keywords) if art.keywords else None
                else:
                    continue
            except:
                continue
            else:
                cursor.execute(
                        f'''
                        INSERT INTO {"news_" + country} (media_name, url, date, author, body, keywords)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        ''',
                        (media_name, url, date, authors, body_text, keywords)
                        )
                # print(f'Artículo de {media_name} agregado, medio de {country_media}')
        conn.commit()
        
        
def news_extractor_per_media_concurrent(media:str, today:datetime, t_delta:timedelta, conn):
    # query
    saved_articles_urls = set([article[0] for article in conn.execute(f'''SELECT url FROM news_chile''').fetchall()])
    # scrapings
    try:
        media_news = newspaper.build(media, memoize_articles=False)
    except Exception as e1:
        print(f"Ha ocurrido un error con {str(media)}:\n\t{e1}")
    else:
        for art in media_news.articles:
            try:
                art.download()
                art.parse()
                if art.is_valid_body() and not art.is_media_news() and art.meta_lang == 'es' and art.publish_date >= (today - t_delta) and art.url not in saved_articles_urls:
                    media_name = art.source_url.partition('//')[-1][:149] if art.source_url else None
                    date = art.publish_date.strftime('%Y-%m-%d %H:%M:%S') if art.publish_date else None
                    authors = ' '.join(art.authors)[:149] if art.authors else None
                    url = art.url if art.url else None
                    body_text = art.text
                    keywords = ", ".join(art.keywords) if art.keywords else None
                else:
                    continue
            except Exception as e2:
                print(f'Ha ocurrido un error al descargar un artículo de {media}:\n\t{e2}')
                continue
            else:
                conn.execute(
                        f'''
                        INSERT INTO news_chile (media_name, url, date, author, body, keywords)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        ''',
                        (media_name, url, date, authors, body_text, keywords)
                    )
                # print(f'Artículo de {media_name} agregado, medio de {country_media}')
    conn.commit()
    print(f'Concluida extracción de noticias de {media}')
        
        
def get_news(connection, table_name:str='news_chile', n:int=10, delta_days=1, media_name:str=None):
    today = datetime.today()
    t_delta = timedelta(days=delta_days, hours=today.hour, minutes=today.minute, seconds=today.second)
    from_date = (today - t_delta).strftime('%Y-%m-%d')
    cursor_pgsql = connection.cursor()
    fetched_ids = set()
    fetched_ids.add(-1)
    if delta_days and not media_name:
        query = f'''
        SELECT id, date, media_name, url, body, keywords
        FROM {table_name}
        WHERE id NOT IN ({re.sub(pattern=r"[{}]", repl="", string=str(fetched_ids))})
        AND date::date >= '{from_date}
        LIMIT {str(n)}
        '''
    elif delta_days and media_name:
        query = f'''
        SELECT id, date, media_name, url, body, keywords
        FROM {table_name}
        WHERE id NOT IN ({re.sub(pattern=r"[{}]", repl="", string=str(fetched_ids))})
        AND media_name = '{media_name}'
        AND date::date >= '{from_date}
        LIMIT {str(n)}
        '''
    else:
        query = f'''
        SELECT id, date, media_name, url, body, keywords
        FROM {table_name}
        WHERE id NOT IN ({re.sub(pattern=r"[{}]", repl="", string=str(fetched_ids))})
        LIMIT {str(n)}
        '''
    try:
        cursor_pgsql.execute(query)
        for results in cursor_pgsql.fetchall(): 
            news_id, news_date, media_name, news_url, news_text, keywords = results
            yield (news_id, news_date, media_name, news_url, news_text, keywords)
            # print(f'Recuperada noticia de fecha {str(news_date)}')
            fetched_ids.add(news_id)
    except Exception as e:
        print(f'An error has ocurred: {e}')
        cursor_pgsql.execute('ROLLBACK;')
        cursor_pgsql.close()
        
        
def get_media_in_db(conn:psycopg.Connection, year=None, month=None, day=None) -> list:
    query = f'''
        SELECT DISTINCT media_name FROM news_chile
    '''.strip()
    unique_media_list = conn.execute(query=query).fetchall()
    return [media_name[0] for media_name in unique_media_list]


# def get_media_in_db(conn:psycopg.Connection, year=None, month=None, day=None) -> list:
#     query = f'''
#         SELECT DISTINCT media_name FROM news_chile
#         WHERE EXTRACT(YEAR FROM date) >= {year}
#         AND EXTRACT(MONTH FROM date) >= {month}
#         AND EXTRACT(DAY FROM date) >= {day}
#     '''.strip()
#     unique_media_list = conn.execute(query=query).fetchall()
#     return unique_media_list