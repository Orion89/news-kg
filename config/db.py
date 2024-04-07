import psycopg
from config.settings import settings

# private_url = os.getenv('DATABASE_PRIVATE_URL')
# database_url =  os.getenv('DATABASE_URL')
# pgpassword = os.getenv('PGPASSWORD')
# pgport = os.getenv('PGPORT')

conn = psycopg.connect(conninfo=settings.POSTGRES_URL)
