import logging, os, sys

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from aiohttp import web


#############################################################################################################################
####################################################### ENV VARIABLES #######################################################
#############################################################################################################################

API_CONFIG = os.getenv("API_CONFIG")
URL_PREFIX = str(os.getenv("API_PREFIX"))
DB_CONNECTION_STRING = str(os.getenv("API_DB_CONNECTION_STRING"))

###############################################################################################################################
######################################################### API MANAGER #########################################################
###############################################################################################################################

class API_Manager():
    """
        API Manager for managing the API server
    """

    # Initialize API
    async def initialize_api(self):
        log.info("Initializing API server")

        self.subapp = web.Application()

        log.info("Configuring Motor driver for MongoDB...")
        self.subapp['db_client'] = await self.setup_db()

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add sub-app to set the IP/recognition-api request
        self.app = web.Application()
        self.app.add_subapp(URL_PREFIX, self.subapp)

        log.info("API initialization complete")

    # Setup DB connection
    async def setup_db(self):
        # Example connection string: mongodb://localhost:27017/database_name
        client = AsyncIOMotorClient(DB_CONNECTION_STRING)
        return client

    # Run API
    def run_api(self, host, port, loop):
        log.info("Server starting on address: http://{}:{}".format(host, port))
        web.run_app(self.app, host=host, port=port, loop=loop)


    ##############################################################################################################################
    ######################################################### API ROUTES #########################################################
    ##############################################################################################################################

    # Configure API routes
    routes = web.RouteTableDef()

    # API healthcheck
    @routes.get('/healthz-api')
    async def api_health_check(request):
        log.info("API health-check running\n")
        return web.Response(text="## API health-check successfull ##\n")

    # DB healthcheck
    @routes.get('/healthz-db')
    async def db_health_check(request):
        log.info("DB health-check running")

        try:
            db = request.app['db_client']

            # Check if DB is alive
            info = await db.server_info()

        return web.Response(text="## DB health-check successfull ##\n")




##############################################################################################################################
############################################################ MAIN ############################################################
##############################################################################################################################
if __name__ == '__main__':

    # Set up operation mode for server
    if API_CONFIG == "dev":
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        # Limit DB connection pooling if necessary
        log = logging.getLogger()
        log.info("Starting API server in development mode")
        log.info("URL_PREFIX: {}".format(URL_PREFIX))
        log.info("DB_CONNECTION_STRING: {}".format(DB_CONNECTION_STRING))

    elif API_CONFIG == "prod":
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Starting API server in production mode")
        log.info("URL_PREFIX: {}".format(URL_PREFIX))
        log.info("DB_CONNECTION_STRING: {}".format(DB_CONNECTION_STRING))


    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable API_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(API_CONFIG))
        sys.exit(1)

    # Get asyncio loop
    loop = asyncio.get_event_loop()

    # Create API_Manager object and initialize it
    manager = API_Manager()
    loop.run_until_complete(manager.initialize_api())

    # Start the server
    manager.run_api(host='0.0.0.0', port=5000, loop=loop)
    











