#!/usr/bin/env python3

# Import general libraries
import logging, os, sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp import web

# Import local libraries
from migrations.migrate import MigrationsManager

#############################################################################################################################
####################################################### ENV VARIABLES #######################################################
#############################################################################################################################

# API configuration
API_CONFIG = os.getenv("API_CONFIG")
URL_PREFIX = str(os.getenv("API_PREFIX"))

# DB configuration
DB_CONNECTION_STRING = str(os.getenv("API_DB_CONNECTION_STRING"))
DB_MIN_POOL_SIZE = int(os.getenv("API_DB_MIN_POOL_SIZE"))
DB_MAX_POOL_SIZE = int(os.getenv("API_DB_MAX_POOL_SIZE"))
DB_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("API_DB_SERVER_SELECTION_TIMEOUT_MS"))
DB_MAX_IDLE_TIME_MS = int(os.getenv("API_DB_MAX_IDLE_TIME_MS"))

###############################################################################################################################
######################################################### API MANAGER #########################################################
###############################################################################################################################

class APIManager():
    """
        API Manager for managing the API server
    """

    # Initialize API
    async def initialize_api(self):

        # Create the migrate object and execute migrations if necessary
        migrations = MigrationsManager(DB_CONNECTION_STRING)
        
        # Try to migrate DB
        if await migrations.migrate():
            log.info("## DB migration successfull ##")
        else:
            log.error("!! DB migration failed !!")
            sys.exit(1)

        log.info("## Initializing API server ##")

        self.subapp = web.Application()

        log.info("## Configuring Motor driver for MongoDB... ##")
        self.subapp['db_client'] = await self.setup_db()

        log.info("## Adding routes to application object... ##")
        self.subapp.router.add_routes(self.routes)

        # Add sub-app to set the IP/recognition-api request
        self.app = web.Application()
        self.app.add_subapp(URL_PREFIX, self.subapp)

        log.info("## API initialization complete ##")

    # Setup DB connection
    async def setup_db(self):
        # Configure the Motor driver for MongoDB
        client = AsyncIOMotorClient(host = DB_CONNECTION_STRING,
                                    minPoolSize=DB_MIN_POOL_SIZE,
                                    maxPoolSize=DB_MAX_POOL_SIZE,
                                    serverSelectionTimeoutMS=DB_SERVER_SELECTION_TIMEOUT_MS,
                                    maxIdleTimeMS=DB_MAX_IDLE_TIME_MS,
                                    appname="Rainsim-API",
                                    retryWrites=True,
                                    retryReads=True)
        return client

    # Run API
    def run_api(self, host, port, loop):
        log.info("## Server starting on address: http://{}:{} ##".format(host, port))
        web.run_app(self.app, host=host, port=port, loop=loop)


    ##############################################################################################################################
    ######################################################### API ROUTES #########################################################
    ##############################################################################################################################

    # Configure API routes
    routes = web.RouteTableDef()

    # API healthcheck
    @routes.get('/healthz-api')
    async def api_health_check(request):
        log.info("## API health-check running ##\n")
        return web.Response(text="## API health-check successfull ##\n")

    # DB healthcheck
    @routes.get('/healthz-db')
    async def db_health_check(request):
        log.info("## DB health-check running ##")

        try:
            # Get DB client
            db = request.app['db_client']
        except Exception as e:
            log.error("!! DB health-check failed with error: {}".format(e))
            return web.Response(text="!! DB health-check failed !!\n")
        else:
            try:
                # Check if DB is alive
                info = await db.server_info()
            except Exception as e:
                log.error("!! DB health-check failed with error: {}".format(e))
                return web.Response(text="!! DB health-check failed !!\n")
            else:
                # If DB is alive return success
                log.info("## DB health-check successfull ##\n")
                log.info("## DB info: {} ##\n".format(info))
            finally:
                return web.Response(text="## DB health-check successfull ##\n")
            




##############################################################################################################################
############################################################ MAIN ############################################################
##############################################################################################################################
if __name__ == '__main__':

    # Set up operation mode for server
    if API_CONFIG == "dev":
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        
        # Set DB connection parameters
        DB_MIN_POOL_SIZE = 1
        DB_MAX_POOL_SIZE = 1
        DB_SERVER_SELECTION_TIMEOUT_MS = 5000
        DB_MAX_IDLE_TIME_MS = 5000
        
        # Set logging and print configuration
        log = logging.getLogger()
        log.info("## Starting API server in development mode ##")
        log.info("## URL_PREFIX: {} ##".format(URL_PREFIX))
        log.info("## DB_CONNECTION_STRING: {} ##".format(DB_CONNECTION_STRING))
        log.info("## DB_MIN_POOL_SIZE: {} ##".format(DB_MIN_POOL_SIZE))
        log.info("## DB_MAX_POOL_SIZE: {} ##".format(DB_MAX_POOL_SIZE))
        log.info("## DB_SERVER_SELECTION_TIMEOUT_MS: {} ##".format(DB_SERVER_SELECTION_TIMEOUT_MS))
        log.info("## DB_MAX_IDLE_TIME_MS: {} ##".format(DB_MAX_IDLE_TIME_MS))

    elif API_CONFIG == "prod":
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Starting API server in production mode")
        log.info("URL_PREFIX: {}".format(URL_PREFIX))
        log.info("DB_CONNECTION_STRING: {}".format(DB_CONNECTION_STRING))
        log.info("DB_MIN_POOL_SIZE: {}".format(DB_MIN_POOL_SIZE))
        log.info("DB_MAX_POOL_SIZE: {}".format(DB_MAX_POOL_SIZE))
        log.info("DB_SERVER_SELECTION_TIMEOUT_MS: {}".format(DB_SERVER_SELECTION_TIMEOUT_MS))
        log.info("DB_MAX_IDLE_TIME_MS: {}".format(DB_MAX_IDLE_TIME_MS))

    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable API_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(API_CONFIG))
        sys.exit(1)

    # Get asyncio loop
    loop = asyncio.get_event_loop()

    # Create API_Manager object and initialize it
    manager = APIManager()
    loop.run_until_complete(manager.initialize_api())

    # Start the server
    manager.run_api(host='0.0.0.0', port=5000, loop=loop)
    











