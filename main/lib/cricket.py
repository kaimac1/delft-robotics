import serial
import time
import re

MODE_LISTEN = 2
MODE_CHIRP = 3

#Scans for serial ports, returns array of port numbers
#The numbers are 1 less than the normal COM numbers (COM1 = 0)
def portScan():

	ports = []
	print("Discovering serial ports:"),

	for i in range(256):
		try:
			s = serial.Serial(i)
			print s.portstr,
			ports.append(i)
			s.close() 
		except serial.SerialException:
 			pass
 	print
	return ports

#Checks whether port is actually a cricket module, returns beacon ID if it is
def cricketIdentify(port):

	spaceid = ""
	s = serial.Serial(port, 115200)
	
	#Put cricket into manual (chirp) mode to stop it sending any data
	#then try and get the beacon ID
	s.write("P MD 3\r")
	time.sleep(0.05)
	s.write("G SP\r")
	time.sleep(0.05)

	response = s.read(s.inWaiting())
	if "SP" in response: spaceid = response.split("\r\n")[1][3:]
	s.close()
	return spaceid


#Detects all connected crickets, returns list of initialised Cricket objects
def cricketScan():

	cricketList = []
	ports = portScan()

	print("Identifying crickets:")
	for port in ports:
		sid = cricketIdentify(port)
		if sid != "": 
			#We have a cricket
			print "COM" + str(port+1) + " = " + sid
			c = Cricket(id=sid, port=port)
			cricketList.append(c)

	return cricketList

#Builds a dictionary given a list of objects and an object variable
#Rather generic, but in this case we use it to address crickets by their beacon IDs
def buildDictionary(objectList, var):

	dict = {}
	
	for object in objectList:
		dict[getattr(object, var)] = object

	return dict

	

#Main cricket class
class Cricket:
	def __init__(self, id, port):
		#Open serial port
		self.id = id
		self.port = port
		self.s = serial.Serial(self.port, 115200)

	#Set mode between beacon (1), listener (2) or chirp (3)
	def setMode(self, mode):
		if mode not in [1,2,3]: raise Exception("Invalid cricket mode")
		self.s.write("P MD " + str(mode) + "\r")
		time.sleep(0.05)

	#Send out a chirp
	def chirp(self):
		self.s.write("P CH\r")
		#time.sleep(0.12)

	#Return the measured distance & ID as a tuple if the cricket has been listening
	def listen(self):
		rx = ""
		#Get the latest returned string
		while self.s.inWaiting():
			rx = self.s.readline()

		#Extract the distance from the returned string. Return -1 if no distance reported
		dist = re.search("DB=(.+?),", rx)
		if dist:
			id = re.search("SP=(.+?),", rx).group(1)
			return (id, dist.group(1))
		else:
			return ("", -1)

	def __del__(self):
		#Close port
		self.s.close()