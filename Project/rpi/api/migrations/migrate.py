#!/usr/bin/env python3

# Import general libraries
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


class MigrationsManager():
    """
        Migrations class for managing MongoDB migrations
    """

    # Initialize migrations
    def __init__(self, connection_string):
        logging.info("## Initializing migrations... ##")
        # Set parameters
        self.connection_string = connection_string
        self.minPoolSize = 1
        self.maxPoolSize = 1
        self.serverSelectionTimeoutMS = 3000
        self.maxIdleTimeMS = 3000

    # Connect to MongoDB
    async def connect(self):
        logging.info("## Connecting to MongoDB... ##")
        # Create the client
        self.client = AsyncIOMotorClient(host = self.connection_string,
                                    minPoolSize=self.minPoolSize,
                                    maxPoolSize=self.maxPoolSize,
                                    serverSelectionTimeoutMS=self.serverSelectionTimeoutMS,
                                    maxIdleTimeMS=self.maxIdleTimeMS)

    # Disconnect from MongoDB
    async def disconnect(self):
        logging.info("## Disconnecting from MongoDB... ##")
        # Close the client
        self.client.close()

    async def create_migrations_table(self):
        logging.info("## Creating Migrations table... ##")

    async def create_experiments_table(self):
        logging.info("## Creating Experiments table... ##")

    async def create_depth_camera_table(self):
        logging.info("## Creating Depth Camera table... ##")


    # Migrate DB schema
    async def migrate(self):
        logging.info("## Migrating DB schema... ##")

        try:
            # Connect to MongoDB
            await self.connect()
        except Exception as e:
            logging.error("!! Error connecting to MongoDB: {}".format(e))
            await self.disconnect()
            return False
        else:
        
            try:
                # Get the default db
                db = self.client.get_default_database()
            except Exception as e:
                logging.error("!! Error getting default database: {}".format(e))
                await self.disconnect()
                return False
            else:

                try:
                    # List collections
                    collections = await db.list_collection_names()
                    logging.info("Collections: {}".format(collections))
                except Exception as e:
                    logging.error("Error listing collections: {}".format(e))
                    await self.disconnect()
                    return False
            
        await self.disconnect()
        return True

    
    