import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
import time
from host import lab
from lib.cricket import *
from numpy.matlib import *

def main():

	#List of hostnames of robots used
	lab.robots = ["alpha1"]
	lab.init("test-setup")

	#Use crickets in chirp mode
	cricketList = cricketScan()
	crickets = buildDictionary(cricketList, 'id')
	for x in crickets:
		crickets[x].setMode(MODE_CHIRP)

	#Use camera
	camera = lab.Camera()
	camera.connect()

	#Use gamepad
	gamepad = lab.Joystick()

	

	#crickets["beac_8"].setMode(MODE_LISTEN)
	#crickets["beac_2"].setMode(MODE_CHIRP)
	#crickets["beac_2"].chirp()
	#time.sleep(0.1)
	#print crickets["beac_8"].listen()
	#print "break"
	#crickets["beac_2"].chirp()
	#time.sleep(0.1)
	#print crickets["beac_8"].listen()

	#Wait for valid camera readings
	cx = 0
	while cx == 0:
		[cx, cy, cb, valid] = camera.getxy()
	lab.robot["alpha1"].set("updateX", array([cx, cy, cb]).T)
	lab.robot["alpha1"].set("goFlag", 1)

	print "go"

	plot = lab.Plot()
	plot.axes((-1000,1000),(-1000,1000))


	cx_old = 0
	cy_old = 0
	x = array([0,0,0]).T

	#time_start = time.clock()

	while True:

		time_start = time.clock()

		#Get camera reading
		[cx,cy,cb,valid] = camera.getxy()

		#Plot it if valid
		if valid:
		 	#pyplot.plot([cx_old, cx], [cy_old, cy], 'bx-')
		 	plot.line(cx_old, cy_old, cx, cy, "blue")
		 	[cx_old, cy_old] = [cx, cy]

		 #Get control input from gamepad, convert to velocity & send to robot
		axes = gamepad.axes()
		(vt, w) = lab.axes2vw(axes)
		(vl, vr) = lab.vw2lr(vt, w)
		lab.robot["alpha1"].set("v", vt)
		lab.robot["alpha1"].set("w", w)
		lab.robot["alpha1"].robot.DriveLR(vl, vr)

		#Get estimated state from robot & plot
		[mx_old, my_old] = [x[0], x[1]]
		x = lab.robot["alpha1"].get("x")
		#pyplot.plot([mx_old, x[0]], [my_old, x[1]], 'rx-')
		plot.line(mx_old, my_old, x[0], x[1], "red")


		if msvcrt.kbhit(): key = msvcrt.getch() 
		else: key = "" 
		if key == "q": break

		#Update plot
		#pyplot.draw()

		time_pad = time.clock() - time_start
		print time_pad


	lab.robot["alpha1"].robot.Stop()

	lab.deinit()



main()