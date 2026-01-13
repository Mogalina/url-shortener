import time
import logging
from datetime import datetime
from app.db.cassandra import session
from app.db.redis import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("service.cleanup")

CHECK_INTERVAL_SECONDS = 3600

def cleanup_expired_urls():
    logger.info("Starting cleanup job...")
    
    try:
        rows = session.execute(
            """
            SELECT short_code 
            FROM urls 
            WHERE expires_at < %s ALLOW FILTERING
            """,
            (datetime.now(),)
        )
        
        count = 0
        for row in rows:
            code = row.short_code
            
            session.execute(
                """
                DELETE FROM urls 
                WHERE short_code = %s
                """,
                (code,)
            )
            
            redis.delete(f"short:{code}")
            count += 1
            
        if count > 0:
            logger.info(f"Cleanup complete. Removed {count} expired URLs.")
        else:
            logger.info("Cleanup complete. No expired URLs found.")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    logger.info("Cleanup service initialized")
    while True:
        cleanup_expired_urls()
        time.sleep(CHECK_INTERVAL_SECONDS)
