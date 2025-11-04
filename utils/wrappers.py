import time

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
