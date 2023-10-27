import logging, os, sys

import asyncio
import aiohttp_sqlalchemy as ahsa

from aiohttp import web


###############################################################
# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("API_URL_PREFIX")
DB_URI = str(os.getenv("API_DB_CONNECTION_STRING"))






###############################################################
## API Class
class API_Manager():
    """
        API Manager for managing the API server
    """

    # Configure routes table and all available methods
    routes = web.RouteTableDef()

    # Healthcheck
    @routes.get('/healthz')
    async def health_check(request):
        log.info("Api test running\n")
        return web.Response(text="## API test successfull ##\n")



if __name__ == '__main__':

    # Set up operation mode for server
    if APP_CONFIG == "dev":
        # Development build
        logging.basicConfig(level=logging.DEBUG)

    elif APP_CONFIG == "prod":
        # Production build
        logging.basicConfig(level=logging.INFO)
        

    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable APP_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(APP_CONFIG))
        sys.exit(1)









