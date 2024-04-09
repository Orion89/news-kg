import psycopg
from config.settings import settings

# private_url = os.getenv('DATABASE_PRIVATE_URL')
# database_url =  os.getenv('DATABASE_URL')
# pgpassword = os.getenv('PGPASSWORD')
# pgport = os.getenv('PGPORT')

if os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'dev':
    conn = psycopg.connect(
        host=os.getenv('DEV_DBHOST'),
        dbname=os.getenv('DEV_DBNAME'),
        user=os.getenv('DEV_DBUSER'),
        password=os.getenv('DEV_DBPASSWORD')
    )
elif os.getenv('RAILWAY_ENVIRONMENT_NAME') == 'production':
    from config.settings import settings
    conn = psycopg.connect(conninfo=settings.POSTGRES_URL)
