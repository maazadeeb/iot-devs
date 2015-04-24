#!/bin/env node
 //  OpenShift sample Node application
var express = require('express');
var fs = require('fs');
var bodyParser = require('body-parser');
var mongojs = require('mongojs');

// var dbCon = require('./db-con/db.js');


/**
 *  Define the sample application.
 */
var SampleApp = function() {

    //  Scope.
    var self = this;

    // Static messages
    var successJSON = {
        "success": true
    };

    var failureJSON = {
        "success": false
    }

    /*  ================================================================  */
    /*  Helper functions.                                                 */
    /*  ================================================================  */

    /**
     *  Set up server IP address and port # using env variables/defaults.
     */
    self.setupVariables = function() {
        //  Set the environment variables we need.
        self.ipaddress = process.env.OPENSHIFT_NODEJS_IP;
        self.port = process.env.OPENSHIFT_NODEJS_PORT || 8080;

        if (typeof self.ipaddress === "undefined") {
            //  Log errors on OpenShift but continue w/ 127.0.0.1 - this
            //  allows us to run/test the app locally.
            console.warn('No OPENSHIFT_NODEJS_IP var, using 127.0.0.1');
            self.ipaddress = "127.0.0.1";
        };

        // default to a 'localhost' configuration:
        // self.connection_string = '127.0.0.1:27017/iot';
        // if OPENSHIFT env variables are present, use the available connection info:
        if (process.env.OPENSHIFT_MONGODB_DB_URL) {

            self.connection_string = process.env.OPENSHIFT_MONGODB_DB_URL + "iot";

        } else {
            console.warn('No OPENSHIFT_MONGODB_DB_URL var, using 127.0.0.1:27017');
            self.connection_string = '127.0.0.1:27017/iot';
        }
    };


    /**
     *  Populate the cache.
     */
    self.populateCache = function() {
        if (typeof self.zcache === "undefined") {
            self.zcache = {
                'index.html': ''
            };
        }

        //  Local cache for static content.
        self.zcache['index.html'] = fs.readFileSync('./index.html');
    };


    /**
     *  Retrieve entry (content) from cache.
     *  @param {string} key  Key identifying content to retrieve from cache.
     */
    self.cache_get = function(key) {
        return self.zcache[key];
    };


    /**
     *  terminator === the termination handler
     *  Terminate server on receipt of the specified signal.
     *  @param {string} sig  Signal to terminate on.
     */
    self.terminator = function(sig) {
        if (typeof sig === "string") {
            console.log('%s: Received %s - terminating sample app ...',
                Date(Date.now()), sig);
            self.db.close();
            process.exit(1);
        }
        console.log('%s: Node server stopped.', Date(Date.now()));
    };


    /**
     *  Setup termination handlers (for exit and a list of signals).
     */
    self.setupTerminationHandlers = function() {
        //  Process on exit and signals.
        process.on('exit', function() {
            self.terminator();
        });

        // Removed 'SIGPIPE' from the list - bugz 852598.
        ['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT',
            'SIGBUS', 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGTERM'
        ].forEach(function(element, index, array) {
            process.on(element, function() {
                self.terminator(element);
            });
        });
    };


    /*  ================================================================  */
    /*  App server functions (main app logic here).                       */
    /*  ================================================================  */

    /**
     *  Create the routing table entries + handlers for the application.
     */
    self.createRoutes = function() {
        self.getRoutes = {};
        self.postRoutes = {};

        // default page for landing. HAProxy error avoidance
        self.getRoutes['/'] = function(req, res) {
            res.setHeader('Content-Type', 'text/html');
            res.send(self.cache_get('index.html'));
        };

        // list all the students in the DB
        self.getRoutes['/listAll'] = function(req, res) {
            console.log("Inside listAll...");
            res.setHeader('Content-Type', 'application/json');
            self.db.students.find(function(err, docs) {
                if (err) {
                    res.json(failureJSON);
                } else {
                    res.json(docs);
                }
            });
        };

        // list out the particular Shimmer ID's details
        self.getRoutes['/list/:id'] = function(req, res) {
            console.log("Inside list %s...", req.params.id);
            var shimmerId = req.params.id;
            res.setHeader('Content-Type', 'application/json');
            self.db.students.findOne({
                    shimmerId: shimmerId
                },
                function(err, doc) {
                    if (err) {
                        res.json(failureJSON);
                    } else {
                        res.json(doc)
                    }
                });
        };

        // send out data for the graphs for Shimmer ID
        self.getRoutes['/sensor/:id/:name'] = function(req, res) {
            var shimmerId = req.params.id;
            var sensor = req.params.name;
            var filter = {};
            filter[sensor] = 1;
            filter["timeStamp"] = 1;
            filter["_id"] = 0;
            console.log("Inside sensor %s for %s", sensor, shimmerId);
            self.db.students.findOne({
                    shimmerId: shimmerId
                },
                filter,
                function(err, doc) {
                    if (err) {
                        res.json(failureJSON);
                    } else {
                        res.json(doc);
                    }
                });

        };

        // accept data to particular Shimmer ID
        // TODO: Bad way of pushing data. Make it more modular
        self.postRoutes['/student/:id'] = function(req, res) {
            console.log("Inside student...");
            res.setHeader('Content-Type', 'application/json');
            var shimmerId = req.params.id;
            var sensorData = JSON.parse(req.body.data);
            self.db.students.update({
                    shimmerId: shimmerId
                }, {
                    $push: {
                        timeStamp: {
                            $each: sensorData.timeStamp
                        },
                        'accelerometer.lowRange.x': {
                            $each: sensorData.accelerometer.lowRange.x
                        },
                        'accelerometer.lowRange.y': {
                            $each: sensorData.accelerometer.lowRange.y
                        },
                        'accelerometer.lowRange.z': {
                            $each: sensorData.accelerometer.lowRange.z
                        },
                        'accelerometer.highRange.x': {
                            $each: sensorData.accelerometer.highRange.x
                        },
                        'accelerometer.highRange.y': {
                            $each: sensorData.accelerometer.highRange.y
                        },
                        'accelerometer.highRange.z': {
                            $each: sensorData.accelerometer.highRange.z
                        },
                        gsr: {
                            $each: sensorData.gsr
                        },
                        temperature: {
                            $each: sensorData.temperature
                        },
                        pressure: {
                            $each: sensorData.pressure
                        },
                        gyroscope: {
                            $each: sensorData.gyroscope
                        },
                        magnetometer: {
                            $each: sensorData.magnetometer
                        },
                        adc13: {
                            $each: sensorData.adc13
                        }
                    }
                },
                function() {
                    res.json(successJSON);
                }
            );
        };
    };


    /**
     *  Initialize the server (express) and create the routes and register
     *  the handlers.
     */
    self.initializeServer = function() {
        self.createRoutes();
        self.app = express();
        self.app.use(bodyParser.urlencoded({
            extended: true
        }));
        self.app.use(bodyParser.json());
        self.app.use(bodyParser.raw());
        self.db = mongojs(self.connection_string, ['students']);

        //  Add handlers for the app (from the routes).
        for (var r in self.getRoutes) {
            self.app.get(r, self.getRoutes[r]);
        }

        // Add handlers for POST
        for (var r in self.postRoutes) {
            self.app.post(r, self.postRoutes[r]);
        }

        console.log("Server initialized...");
    };


    /**
     *  Initializes the sample application.
     */
    self.initialize = function() {
        self.setupVariables();
        self.populateCache();
        self.setupTerminationHandlers();

        // Create the express server and routes.
        self.initializeServer();
    };


    /**
     *  Start the server (starts up the sample application).
     */
    self.start = function() {
        //  Start the app on the specific interface (and port).
        self.app.listen(self.port, self.ipaddress, function() {
            console.log('%s: Node server started on %s:%d ...',
                Date(Date.now()), self.ipaddress, self.port);
            console.log('Mongo DB running on: %s', self.connection_string);
        });
    };

}; /*  Sample Application.  */



/**
 *  main():  Main code.
 */
var zapp = new SampleApp();
zapp.initialize();
zapp.start();

//module.exports = db;