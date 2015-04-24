## Setting up local environment

1. Install [Node.js](https://nodejs.org/download/)
2. Install [MongoDB](https://www.mongodb.org/downloads). Try and put **`/{path of mongodb installation}/bin`** into your PATH of environment variables, so it becomes easy to run mongo db from the command line.
3. Install [Git](http://git-scm.com/downloads).
4. Pull code to your local system: `git clone https://github.com/maaz93/iot-devs.git`
5. `cd iot-devs`
6. `npm install`
7. Create a folder for MongoDB. Say `{folder structure}/iot-devs/db/data`. Open cmd and run `mongod --dbpath={folder structure}/iot-devs/db/data`. If you get any 'not recognised' error, then you havn't added mongod in environment variables list. Then run `/{path of mongodb installation}/bin/mongod --dbpath={folder structure}/iot-devs/db/data`. Minimize the cmd. **DO NOT CLOSE THE CMD** as the mongo server will be running here.
8. `node /db/db.js` - This will create a default DB for you to use.
9. `node server.js` - This will create the REST API. Test using [localhost:8080/listAll](localhost:8080/listAll). It will list the full DB in the browser.

## Rest API documentation

##### URLs for testing: [OpenShift](http://iot-sniper6.rhcloud.com/),[localhost](localhost:8080/)

1. **`GET` `/listAll`**  
  * Request Parameters: None
  * Response: Details of all the students

2. **`GET` `/list/{id}`**  
  * Request Parameters: {id} is the Shimmer ID
  * Response: Details of the student with Shimmer ID as {id}

3. **`GET` `/sensor/{id}/{sensorName}`**  
  * Request Parameters: {id } is Shimmer ID, {sensorName} is the name of the sensor you need
  * Response: Timestamp and {sensorName} data of student
  * Sample Request: `/sensor/A643/gsr`
  * Sample Response: `{"timeStamp":[1,2,3,1,2,3],"gsr":[23,24,5,23,24,5]}`
  * Note: To access low range accelorometer use `/sensor/A643/accelerometer.lowRange`, i.e the dot notation to go inside objects.

4. **`POST` `/student/{id}`**  
  * Request Parameters: {id} is the Shimmer ID, body **should** contain a **`data`** paramater as described below 
  * Response: JSON Object telling success or failure
  * Sample Request: `/student/A643`
  * Sample Body:
  ```javascript
{"data":{"timeStamp":[1,2,3],"accelerometer":{"lowRange":{"x":[3,2,4],"y":[7,4,3],"z":[1,5,3]},"highRange":{"x":[4,2,4],"y":[8,7,6],"z":[3,5,1]}},"gsr":[23,24,5],"temperature":[32,5,2],"pressure":[4,24,54],"gyroscope":{"x":[3,2,4],"y":[7,4,3],"z":[1,5,3]},"magnetometer":{"x":[3,2,4],"y":[7,4,3],"z":[1,5,3]},"adc13":[324,32,2]}}
  ```
  * **VERY IMPORTANT NOTE: The data HAS to be in the same format as the sample body. Key names CANNOT differ even by a letter** 