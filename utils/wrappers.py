import time, logging

class RegistryWrapper:
    web_sites = []

    @classmethod
    def take_sites(cls):
        return cls.web_sites

    def __call__(self, web_site):
        self.web_sites.append(web_site())
        return web_site

def async_timer(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            print(time.time() - start)
    return wrapper

class Logger:

    def __init__(self, sync):
        self.sync = sync

    def __call__(self, func):
        logging.basicConfig(level=logging.INFO, filename="log_file.log", filemode="w",
                            format="%(asctime)s %(levelname)s %(message)s")

        async def async_log(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error(f"{func.__name__} {e}")

        def sync_log(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"{func.__name__} {e}")

        return sync_log if self.sync else async_log