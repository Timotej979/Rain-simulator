// Usage: mongo init-mongo.js

// Get the database name
db.getSiblingDB('admin').auth(
    process.env.MONGO_INITDB_ROOT_USERNAME,
    process.env.MONGO_INITDB_ROOT_PASSWORD
);

// Create the user on the database
db.createUser({
    user: process.env.DB_USER,
    pwd: process.env.DB_PASS,
    'roles': [{
        'role': 'dbOwner',
        'db': process.env.DB_NAME
    }],
});

// Get the database and create the collections
db = new Mongo().getDB(process.env.DB_NAME);

print('Database created');

////////////////////////////////
////////// ROOT TABLE //////////
////////////////////////////////

// Create the collection of experiments
db.createCollection('experiments', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['name', 'description', 'date'],
            properties: {
                name: {
                    bsonType: 'string',
                    description: 'must be a string and is required',
                },
                description: {
                    bsonType: 'string',
                    description: 'must be a string and is required',
                },
                date: {
                    bsonType: 'date',
                    description: 'must be a date and is required',
                },

                cameraReference: {
                    bsonType: 'array',
                    description: 'must be a array of keys',
                },

                // TODO: Add the other sensor references if needed

            },
        },
    },
});

print('Experiments collection created');

///////////////////////////////////////
////////// SENSOR TIMESERIES //////////
///////////////////////////////////////

// Camera
db.createCollection('camera', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['timestamp', 'value'],
            properties: {
                timestamp: {
                    bsonType: 'date',
                    description: 'must be a date and is required',
                },
                value: {
                    bsonType: 'array',
                    description: 'must be a array and is required',
                },
            },
        },
    },
});

print('Camera collection created');

