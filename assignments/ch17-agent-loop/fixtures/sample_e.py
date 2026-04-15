import logging
import time

logger = logging.getLogger(__name__)

def retry(fn, max_attempts: int = 3, delay: float = 1.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
    raise RuntimeError("All attempts failed")
