import logging
from cassandra.cluster import Cluster
from app.core.config import settings

logger = logging.getLogger("cassandra")

cluster = Cluster([settings.CASSANDRA_HOSTS])
session = cluster.connect()

logger.info("Connected to Cassandra cluster")

session.execute(f"""
CREATE KEYSPACE IF NOT EXISTS {settings.KEYSPACE}
WITH replication = {{ 
    'class': 'SimpleStrategy', 
    'replication_factor': 3 
}};
""")

session.set_keyspace(settings.KEYSPACE)

session.execute("""
CREATE TABLE IF NOT EXISTS urls (
    short_code TEXT PRIMARY KEY,
    long_url TEXT,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
)
""")

logger.info("Cassandra schema ensured")
