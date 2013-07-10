import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
import time
from host import lab
from lib.state import *
from lib.cricket import *
from numpy.matlib import *
import random
import csv

def main():

	#List of hostnames of robots used
	lab.robots = ["alpha1"]
	lab.init("cricket")

	#Use crickets in chirp mode
	cricketList = cricketScan()
	crickets = buildDictionary(cricketList, 'id')
	for x in crickets:
		crickets[x].setMode(MODE_LISTEN)

	#Use gamepad
	gamepad = lab.Joystick()

	dt = 0.2

	lab.robot["alpha1"].set("goFlag", 1)

	while True:

		time_start = time.clock()

		#Get control input from gamepad & send to robot
		axes = gamepad.axes()
		(v, r) = lab.axes2vr(axes)
		lab.robot["alpha1"].robot.DriveVR(v, r)
		
		
		#node = random.randrange(1,11)
		node = 4
		node_name = "beac_" + str(node)

		#Get measurement
		(nn, dist) = crickets[node_name].listen()
		for c in crickets:
			crickets[c].s.flush()
		print nn, node, dist
		dist = int(dist)*10

		if msvcrt.kbhit(): key = msvcrt.getch() 
		else: key = "" 
		if key == "q": break

		loop_time = time.clock() - time_start
		#print loop_time, loop_time < dt, t
		if loop_time < dt: time.sleep(dt-loop_time)



	lab.robot["alpha1"].robot.Stop()

	lab.deinit()

main()