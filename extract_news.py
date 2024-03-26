from datetime import datetime
from datetime import timedelta
from pytz import timezone
import re

import newspaper
import psycopg
# from medias.medias_list import medias_dict

today = datetime.today()
tz = timezone('UTC')
today = today.replace(tzinfo=tz)
time_delta = timedelta(days=1, hours=today.hour, minutes=today.minute)

conn_postgresql = psycopg.connect(
    host="localhost",
    dbname="news_kg_v1",
    user="postgres",
    password="0rioN-689"
)


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
        
        
def get_news(connection, table_name:str='news_chile', n:int=10, year:int=None, day:int=None, month:int=None):
    cursor_pgsql = connection.cursor()
    fetched_ids = set()
    fetched_ids.add(-1)
    if year and month:
        query = f'''
        SELECT id, date, media_name, url, body, keywords
        FROM {table_name}
        WHERE id NOT IN ({re.sub(pattern=r"[{}]", repl="", string=str(fetched_ids))})
        AND EXTRACT(YEAR FROM date) >= {year}
        AND EXTRACT(MONTH FROM date) >= {month}
        AND EXTRACT(DAY FROM date) >= {day}
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
            fetched_ids.add(news_id)
    except Exception as e:
        print(f'An error has ocurred: {e}')
        cursor_pgsql.execute('ROLLBACK;')
        cursor_pgsql.close()