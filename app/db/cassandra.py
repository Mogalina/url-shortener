import logging
from cassandra.cluster import Cluster
from app.core.config import settings

logger = logging.getLogger("cassandra")

hosts = [h.strip() for h in settings.CASSANDRA_HOSTS.split(",")]

cluster = Cluster(hosts, compression=True)
session = cluster.connect()

logger.info(f"Connected to Cassandra cluster at {hosts}")

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

session.execute("""
CREATE INDEX IF NOT EXISTS idx_expires_at ON urls (expires_at);
""")

logger.info("Cassandra schema ensured")
