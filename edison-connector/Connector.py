#!/usr/bin/python

import sys, struct, serial, json, requests, time



SENSOR_ACCEL 					= 0x80
SENSOR_DACCEL 					= 0x10
SENSOR_GYRO						= 0x40
SENSOR_MAG					 	= 0x20
SENSOR_GSR 						= 0x04
SENSOR_INT_ADC_A13			 	= 0x01
SENSOR_PRESSURE					= 0X04
SENSOR_TEMPERATURE				= 0X02

fout=open("sensor.txt","w")

def wait_for_ack():
	ddata = ""
	ack = struct.pack('B', 0xff)
	while ddata != ack:
		ddata = ser.read(1)
	return

def calculate_gsr(gsr,resistor):
	if resistor == 0 :
		p1 = 0.0363
		p2 = -24.8617
	elif resistor == 1 :
		p1 = 0.0051
		p2 = -3.8357
	elif resistor == 2 :
		p1 = 0.0015
		p2 = -1.0067
	else :
		p1 = 0.00044513
		p2 = -0.3193
	conductance = p1 * gsr + p2
	return 1000000/conductance

def bmp180_calc_compensated_vals(UT, UP):
	X1 = (UT - AC6) * AC5 / 32768
	X2 = MC * 2048 / (X1 + MD)
	B5 = X1 + X2
	T = (B5 + 8) / 16

	B6 = B5 - 4000
	X1 = (B2 * (B6 * B6 / 4096)) / 2048
	X2 = AC2 * B6 / 2048
	X3 = X1 + X2
	B3 = (((AC1 * 4 + X3) *(1<< OSS) + 2)) / 4
	X1 = AC3 * B6 / 8192
	X2 = (B1 * (B6 * B6 / 4096)) / 65536
	X3 = ((X1 + X2) + 2) / 4
	B4 = AC4 * (X3 + 32768) / 32768
	B7 = (UP - B3) * (50000 >> OSS)
	if B7 < 0x80000000: 
		p = (B7 * 2) / B4
	else:
		p = (B7 / B4) * 2
	X1 = (int((p / 256.0) * (p / 256.0)) * 3038) / 65536
	X2 = (-7357 * p) / 65536
	p += (X1 + X2 + 3791) / 16
	return (T, p)


if len(sys.argv) < 3:
	print "no device specified"
	print "You need to specify the serial port of the device you wish to connect to"
	print "Also the Shimmer ID"
	print "example:"
	print "Connector.py Com12 A641"
	print "or"
	print "Connector.py /dev/rfcomm0 A641"
else:
	ser = serial.Serial(sys.argv[1], 115200)
	ser.flushInput()


# read the calibration coefficients
	ser.write(struct.pack('B', 0x59))
	wait_for_ack()

	ddata = ""
	calibcoeffsresponse = struct.pack('B', 0x58)
	while ddata != calibcoeffsresponse:
		ddata = ser.read(1)

	ddata = ""
	numbytes = 0
	framesize = 22
	while numbytes < framesize:
		ddata += ser.read(framesize)
		numbytes = len(ddata)
	data = ddata[0:framesize]

	(AC1, AC2, AC3, AC4, AC5, AC6, B1, B2, MB, MC, MD) = struct.unpack('>hhhHHHhhhhh', data);

# set OSS value (0-3)
	OSS = 0
	ser.write(struct.pack('BB', 0x52, OSS))
	wait_for_ack()
# send the set sensors command
	ser.write(struct.pack('BBBB', 0x08, SENSOR_ACCEL | SENSOR_GYRO | SENSOR_MAG | SENSOR_GSR, SENSOR_DACCEL | SENSOR_INT_ADC_A13, SENSOR_PRESSURE | SENSOR_TEMPERATURE))  #Low Noise Accelerometer, Gyroscope, Magnetometer, GSR, Wide Range Accelerometer, A13
	wait_for_ack()
# send the set sampling rate command
	#ser.write(struct.pack('BBB', 0x05, 0x80, 0x02)) #50Hz (640 (0x280)). Has to be done like this for alignment reasons
	#wait_for_ack()
# send start streaming command
	ser.write(struct.pack('B', 0x07))
	wait_for_ack()

	# read incoming data
	ddata = ""
	numbytes = 0
	framesize = 36 # 1B Packet Type + 2B Timestamp + 3x2B Low Noise Accelerometer + 3x2bB Gyroscope + 3x2B Magnetometer + 2B GSR + 3x2B Wide Range Accelerometer + 2B A13 + 3B Pressure + 2B Temperature
	jsondata = {}
	jdata = {"timeStamp":[],"accelerometer":{"lowRange":{"x":[],"y":[],"z":[]},"highRange":{"x":[],"y":[],"z":[]}},"gsr":[],"temperature":[],"pressure":[],"gyroscope":{"x":[],"y":[],"z":[]},"magnetometer":{"x":[],"y":[],"z":[]},"adc13":[]}
	#jdata['shimmerId'] = ['A643']
	#jdata['shimmerMAC'] = ['00:06:66:63:A6:41']
	print "Packet Type,Timestamp,Analog AccelX,Analog AccelY,Analog AccelZ,GyroX,GyroY,GyroZ,MagX,MagY,Magz,Active Resistor,GSR,Digital AccelX,Digital AccelY,Digital AccelZ,ADC13,Pressure,Temperature"
	start_time = time.time()
	try:

		  
		while (time.time() - start_time <= 60):
			#count += 1
			if(time.time() - start_time <= 10.0) :
				while numbytes < framesize:
					ddata += ser.read(framesize)
					numbytes = len(ddata)
				
				data = ddata[0:framesize]
				ddata = ddata[framesize:]
				numbytes = len(ddata)

				(packettype,) = struct.unpack('B', data[0:1])
				(timestamp, analogaccelx, analogaccely, analogaccelz, adc13, gsr) = struct.unpack('HHHHHH', data[1:13])
				(digiaccelx, digiaccely, digiaccelz) = struct.unpack('hhh',data[19:25])
				(gyrox, gyroy, gyroz) = struct.unpack('>hhh',data[13:19])
				(magx, magz, magy) = struct.unpack('>hhh',data[25:31])
				#(adc13) = struct.unpack('H',data[29:31])

				(UT,) = struct.unpack('>H', data[31:33])
				(msb, lsb, xlsb) =struct.unpack('BBB', data[33:framesize])
				UP = ((msb<<16) + (lsb<<8) + xlsb)>>(8-OSS)
				(temperature, pressure) = bmp180_calc_compensated_vals(UT, UP)

				#gsr = struct.unpack('H',data[34:framesize]) # Workaround

				#(gyrox, gyroy, gyroz, magx, magy, magz) = struct.unpack('>hhhhhh', data[9:21])
				#(gsr, digiaccelx, digiaccely, digiaccelz, adc13) = struct.unpack('HHHHH', data[21:31])
				
				#(UT,) = struct.unpack('>H', data[31:33])
				#(msb, lsb, xlsb) =struct.unpack('BBB', data[33:framesize])
				#UP = ((msb<<16) + (lsb<<8) + xlsb)>>(8-OSS)
				#(T, p) = bmp180_calc_compensated_vals(UT, UP)

				#(pressure, temperature) = struct.unpack('HH', data[31:framesize])
				resistor = (gsr & 0xC000) >> 14
				gsr &= 0x3FFF
				gsr_cal=calculate_gsr(gsr,resistor)

				#jdata['sensordata']['timeStamp'].append(timestamp)
				
				#jdata['sensordata']['accelerometer']['lowRange']['x'].append(analogaccelx)
				#jdata['sensordata']['accelerometer']['lowRange']['y'].append(analogaccely)
				#jdata['sensordata']['accelerometer']['lowRange']['z'].append(analogaccelz)

				#jdata['sensordata']['accelerometer']['highRange']['x'].append(digiaccelx)
				#jdata['sensordata']['accelerometer']['highRange']['y'].append(digiaccely)
				#jdata['sensordata']['accelerometer']['highRange']['z'].append(digiaccelz)

				#jdata['sensordata']['gsr'].append(gsr)
				#jdata['sensordata']['temperature'].append(temperature/10.0)
				#jdata['sensordata']['pressure'].append(pressure)
				#jdata['sensordata']['adc13'].append(adc13)


				jdata['timeStamp'].append(time.time())
				
				jdata['accelerometer']['lowRange']['x'].append(analogaccelx)
				jdata['accelerometer']['lowRange']['y'].append(analogaccely)
				jdata['accelerometer']['lowRange']['z'].append(analogaccelz)

				jdata['accelerometer']['highRange']['x'].append(digiaccelx)
				jdata['accelerometer']['highRange']['y'].append(digiaccely)
				jdata['accelerometer']['highRange']['z'].append(digiaccelz)

				jdata['gsr'].append(gsr_cal)
				jdata['temperature'].append(temperature/10.0)
				jdata['pressure'].append(pressure)
				jdata['adc13'].append(adc13)

				jdata['magnetometer']['x'].append(magx)
				#jdata['magnetometer'].append(magx)
				jdata['magnetometer']['y'].append(magy)
				jdata['magnetometer']['z'].append(magz)

				#jdata['gyroscope'].append(gyrox)
				jdata['gyroscope']['x'].append(gyrox)
				jdata['gyroscope']['y'].append(gyroy)
				jdata['gyroscope']['z'].append(gyroz)

				jsondata = json.dumps(jdata)
				postData = {}
				postData["data"] = jsondata
				#print jdata


				#print "0x%02x, %5d\t%4d, %4d, %4d, \t%4d, %4d, %4d\t%4d, %4d, %4d, \t%4d, %4d, \t%4d, %4d, %4d\t%4d\t %4d, %4d" % (packettype, timestamp, analogaccelx, analogaccely, analogaccelz, gyrox, gyroy, gyroz, magx, magy, magz, resistor, gsr, digiaccelx, digiaccely, digiaccelz, adc13, pressure, temperature)
				fout.write("0x%02x, %0.3f\t%4d, %4d, %4d, \t%4d, %4d, %4d\t%4d, %4d, %4d, \t%4d, %4d, \t%4d, %4d, %4d\t%4d\t %4d,%4d, \t%4d,%0.1f\n" % (packettype, time.time(), analogaccelx, analogaccely, analogaccelz, gyrox, gyroy, gyroz, magx, magy, magz, resistor, gsr, digiaccelx, digiaccely, digiaccelz, adc13, UP,pressure, UT,temperature/10.0))
				#print jsondata
			else :
				#ser.write(struct.pack('B', 0x20))
				#wait_for_ack()
				#ser.close()
				
				#fout.close()
				print "All done"
				r = requests.post('http://localhost:8080/student/'+sys.argv[2], data = postData)
				start_time += 10
				print "else"
				jdata = {"timeStamp":[],"accelerometer":{"lowRange":{"x":[],"y":[],"z":[]},"highRange":{"x":[],"y":[],"z":[]}},"gsr":[],"temperature":[],"pressure":[],"gyroscope":{"x":[],"y":[],"z":[]},"magnetometer":{"x":[],"y":[],"z":[]},"adc13":[]}
				jsondata = {}
	except KeyboardInterrupt:
		print "except"
		pass