# MongoDB Demo

## 1. Replica Set

- Install the [Docker Engine](https://docs.docker.com/engine/install/ubuntu/).
- Add the following lines to your `/etc/hosts` (only for MacOS and Linux OS).

```bash
127.0.0.1 mongo1
127.0.0.1 mongo2
127.0.0.1 mongo3
```

- Run the following command to start the MongoDB replica set.

```bash
docker-compose up -d
```

to stop then run

```bash
docker-compose down
```

- Connection URI: `mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set&readPreference=primary&ssl=false`
- Run `db.runCommand("ismaster").primary` to get the current primary node.

## 2. Schema with MongoDB

Define schema.

```json
db.createCollection("students", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         title: "Student Object Validation",
         required: [ "address", "major", "name", "year" ],
         properties: {
            name: {
               bsonType: "string",
               description: "'name' must be a string and is required"
            },
            year: {
               bsonType: "int",
               minimum: 2017,
               maximum: 3017,
               description: "'year' must be an integer in [ 2017, 3017 ] and is required"
            },
            gpa: {
               bsonType: [ "double" ],
               description: "'gpa' must be a double if the field exists"
            }
         }
      }
   }
} )
```

Invalid record.

```json
db.students.insertOne( {
   name: "Alice",
   year: 2019,
   major: "History",
   gpa: 3,
   address: {
      city: "NYC",
      street: "33rd Street"
   }
} )
```

Valid record.

```json
db.students.insertOne( {
   name: "Alice",
   year: 2019,
   major: "History",
   gpa: 3.5,
   address: {
      city: "NYC",
      street: "33rd Street"
   }
} )
```
