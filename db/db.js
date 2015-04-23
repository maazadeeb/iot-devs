/*  ================================================================  */
/*  Helper js to set up local DB                       				  */
/*  ================================================================  */

var mongojs = require('mongojs');

var mongo_url = '127.0.0.1:27017/iot';

if (process.env.OPENSHIFT_MONGODB_DB_URL) {
	mongo_url = process.env.OPENSHIFT_MONGODB_DB_URL + "iot";
}
var data = [{"shimmerId":"A643","shimmerMAC":"00:06:66:63:A6:43","studentData":{"id":"S001","name":"Alice","address":"R T Nagar","parentName":"Bob","parentNumber":"+919543344562","parentEmail":"bob@example.com"},"timeStamp":[],"accelerometer":{"lowRange":{"x":[],"y":[],"z":[]},"highRange":{"x":[],"y":[],"z":[]}},"gsr":[],"temperature":[],"pressure":[],"gyroscope":[],"magnetometer":[],"adc13":[]},{"shimmerId":"A75F","shimmerMAC":"3C:77:E6:EB:A0:BF","studentData":{"id":"S002","name":"Carl","address":"Jalahalli","parentName":"Dave","parentNumber":"+919548144562","parentEmail":"dave@example.com"},"timeStamp":[],"accelerometer":{"lowRange":{"x":[],"y":[],"z":[]},"highRange":{"x":[],"y":[],"z":[]}},"gsr":[],"temperature":[],"pressure":[],"gyroscope":[],"magnetometer":[],"adc13":[]},{"shimmerId":"A641","shimmerMAC":"00:06:66:63:A6:41","studentData":{"id":"S003","name":"Eve","address":"CBI","parentName":"Fowler","parentNumber":"+918318144562","parentEmail":"fowler@example.com"},"timeStamp":[],"accelerometer":{"lowRange":{"x":[],"y":[],"z":[]},"highRange":{"x":[],"y":[],"z":[]}},"gsr":[],"temperature":[],"pressure":[],"gyroscope":[],"magnetometer":[],"adc13":[]}];

var db = mongojs(mongo_url, ['students']);
// var bulk = db.students.initializeOrderedBulkOp();

db.students.drop( function (err, docs) {
	db.students.insert(data, function (err, docs) {
		if(err) {
			console.log("Error in inserting DB: " + err);
			process.exit(1);
		}
		else {
			console.log("DB created successfully");
			db.close();
		}
	});
});  
