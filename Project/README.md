# Rain-simulator

Rain simulator developed by UNI LJ Faculty of electrical engineering and Faculty of civil and geodetic engineering.

## Project structure

The folder structure of this project is the following:

- **databse** 
    - ***docker-compose.yaml*** - *Docker compose file for testing runs of the DB*
    - ***stack-db.yml*** - *Docker swarm compose file for production runs of the DB*
    - ***init-mongo.js*** - *Initialization script for the DB schema and DB user access*
    - ***db-data*** - *COntainer volume that saves the current DB state and can be accessed externaly*

- **old**
    - Contains various files from the previous implementation of the software, here for reference to allow a simpler transition

- **rpi**
    - ***docker compose.yaml*** - *Docker compose file for testing runs of the software that will be ran on the RPI*
    - ***stack-rpi.yml*** - *Docker swarm compose file for the production runs of the software that will be ran on the RPI*
    - ***nginx*** - *Folder with the reverse proxy Nginx configuration for the web frontend on the RPI*
    - ***api*** - *Folder with the python API code for controling the simulator*

- **startStopProdScripts** (Should be run in the following order for the successful deployment)
    - ***startSWARM.sh*** - *Script that creates the overlay API-DB network and starts the Docker swarm on the current system* (To add more nodes check the output of this script and deploy RPI/DB stacks on sepparate nodes)
    - ***startDB.sh*** - *Script that deploys the DB stack to the swarm node*
    - ***startRPI.sh*** - *Script that deploys the RPI software stack to the swarm node*
    - ***stopRPI.sh*** - *Script that stops the RPI software stack on the swarm node*
    - ***stopDB.sh*** - *Script that stops the DB stack on the swarm node*
    - ***stopSWARM.sh*** - *Script that removes the overlay API-DB network and stops the Docker swarm on the current system* (To stop the other nodes check the script for the exit out of the swarm mode on a system)

- **startStopTestScripts** (Should be run in the following order for the successfull)
    - ***startDB.sh*** - *Script that runs the docker compose DB instance localy*
    - ***startRPI.sh*** - *Script that runs the docker compose RPI software instance localy*
    - ***stopDB.sh*** - *Script that stops the docker compose DB instance localy*
    - ***stopRPI.sh*** - Script that stops the docker compose RPI software instance localy*

- **testing**
    - Contains the example python scripts used for testing, after the code matures the scripts will be integrated properly into the API sub-classes

- ***.env***
    - Example environment configuration file for the testing/production runs of the application