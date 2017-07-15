import logging
from functools import wraps


logger = logging.getLogger('miner_center')
def exception_handle(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def try_except(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(e)
                raise
        return try_except(*args, **kwargs)
    return wrapper

