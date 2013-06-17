import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
import time
from host import lab
from lib.cricket import *
from matplotlib import pyplot
from numpy.matlib import *

def main():
	#List of hostnames of robots used
	lab.robots = ["alpha1"]
	lab.init("test-setup")

	#Use camera
	camera = lab.Camera()
	camera.connect()

	gamepad = lab.Joystick()

	#cricketList = cricketScan()
	#crickets = buildDictionary(cricketList, 'id')

	#crickets["beac_8"].setMode(MODE_LISTEN)
	#crickets["beac_2"].setMode(MODE_CHIRP)
	#crickets["beac_2"].chirp()
	#time.sleep(0.1)
	#print crickets["beac_8"].listen()
	#print "break"
	#crickets["beac_2"].chirp()
	#time.sleep(0.1)
	#print crickets["beac_8"].listen()

	#Wait for sane camera readings
	cx = 0
	while cx == 0:
		[cx, cy, cb] = camera.getxy()
	lab.robot["alpha1"].set("updateX", array([cx, cy, cb]).T)

	lab.robot["alpha1"].set("goFlag", 1)

	print "go"

	pyplot.ion()
	pyplot.axis([-1000,1000,-1000,1000])

	cx_old = 0
	cy_old = 0
	x = array([0,0,0]).T
	while True:
		[cx,cy,cb] = camera.getxy()
		if (cx != 0) and (cy != 0):
			pyplot.plot([cx_old, cx], [cy_old, cy], 'bx-')
			[cx_old, cy_old] = [cx, cy]

		pyplot.draw() # update the plot


		axes = gamepad.axes()
		(vt, w) = lab.axes2vw(axes)
		(vl, vr) = lab.vw2lr(vt, w)

		lab.robot["alpha1"].set("v", vt)
		lab.robot["alpha1"].set("w", w)
		
		lab.robot["alpha1"].robot.DriveLR(vl, vr)

		[mx_old, my_old] = [x[0], x[1]]
		x = lab.robot["alpha1"].get("x")
		pyplot.plot([mx_old, x[0]], [my_old, x[1]], 'rx-')

		if msvcrt.kbhit(): key = msvcrt.getch() 
		else: key = "" 

		if 		key == "q": break
		elif 	key == "w": lab.robot["alpha1"].robot.DriveVR(500, 500)
		elif	key == "s": lab.robot["alpha1"].robot.DriveStraight(-500)
		elif	key == "e": lab.robot["alpha1"].robot.Stop()

		#time.sleep(0.05)

	lab.robot["alpha1"].robot.Stop()

	lab.deinit()



main()