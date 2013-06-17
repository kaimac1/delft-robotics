import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
from host import lab
from lib.cricket import *
import time
import csv

def main():

	#Use camera
	#camera = lab.Camera()
	#camera.connect()

	cricketList = cricketScan()
	crickets = buildDictionary(cricketList, 'id')

	crickets["beac_7"].setMode(MODE_LISTEN)
	crickets["beac_2"].setMode(MODE_CHIRP)

	data = []
	
	for i in range(25):
		crickets["beac_2"].chirp()
		time.sleep(0.08)
		x = crickets["beac_7"].listen()[1]
		data.append(x)
		print x

	with open("c:/kyle/main/cricket-test/cricket.csv", "wb") as f:
		writer = csv.writer(f)
		writer.writerow(data)


#	print "go"

#	while True:
#		time.sleep(0.05)


main()