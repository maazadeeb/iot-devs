Repository for an IoT based project that aims at monitoring autistic students in real-time.

## Setup local environment

1. Install [Node.js](https://nodejs.org/download/)
2. Install [MongoDB](https://www.mongodb.org/downloads). Try and put **`/{path of mongodb installation}/bin`** into your PATH of environment variables, so it becomes easy to run mongo db from the command line.
3. Install [Git](http://git-scm.com/downloads).
4. Pull code to your local system: `git clone https://github.com/maaz93/iot-devs.git`
5. `cd iot-devs`
6. `npm install`
7. Create a folder for MongoDB. Say `{folder structure}/iot-devs/db/data`. Open cmd and run `mongod --dbpath={folder structure}/iot-devs/db/data`. If you get any 'not recognised' error, then you havn't added mongod in environment variables list. Then run `/{path of mongodb installation}/bin/mongod --dbpath={folder structure}/iot-devs/db/data`. Minimize the cmd, **DO NOT CLOSE THE CMD**.
8. `node /db/db.js` - This will create a default DB for you to use.
9. `node server.js` - This will create the REST API. Test using [localhost:8080/listAll](localhost:8080/listAll). It will list the full DB in the browser.

## Rest API documentation

TODO.
