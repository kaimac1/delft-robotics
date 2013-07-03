import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
import time
from host import lab
from lib.state import *
from lib.cricket import *
from numpy.matlib import *

def main():

	CAMERA = False

	#List of hostnames of robots used
	lab.robots = ["alpha1"]
	lab.init("sched-random")

	#Use crickets in chirp mode
	cricketList = cricketScan()
	crickets = buildDictionary(cricketList, 'id')
	for x in crickets:
		crickets[x].setMode(MODE_CHIRP)

	#Use camera
	if CAMERA:
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

	#State-space model
	dt = 0.1
	m = EKFModel(4)
	def const_velocity(x,u):
		return array(x[0] + x[2]*dt + 0.5*dt*dt*u[0],
					 x[1] + x[3]*dt + 0.5*dt*dt*u[1],
					 x[2] + u[0]*dt,
					 x[3] + u[1]*dt).T
	m.f = const_velocity
	m.Q = eye(2)*5
	m.R = eye(10)*0.02

	#Cricket locations and measurement equation
	node_xy = ((-13, 104), (-13, 312), (-13, 519), (79, 634), (236, 634), (331, 516), (331, 310), (242, -13), (81, -13))
	node_height = 153
	def h(x, i):
		return sqrt((x[0] - node_xy[i][0])^2 + (x[1] - node_xy[i][1])^2 + node_height^2)

	#Wait for valid camera readings
	cx = 0; cy = 0
	if CAMERA:
		while cx == 0:
			[cx, cy, cb, valid] = camera.getxy()
	m.x = array([cx, cy, 0, 0]).T
	lab.robot["alpha1"].set("goFlag", 1)

	plot = lab.Plot()
	plot.axes((-1000,1000),(-1000,1000))

	cx_old = 0
	cy_old = 0

	while True:

		time_start = time.clock()

		#Get camera reading and plot if valid
		if CAMERA:
			[cx,cy,cb,valid] = camera.getxy()
			if valid:
			 	plot.line(cx_old, cy_old, cx, cy, "blue")
		 		[cx_old, cy_old] = [cx, cy]

		#Get control input from gamepad & send to robot
		axes = gamepad.axes()
		(v, r) = lab.axes2vr(axes)
		lab.robot["alpha1"].robot.DriveVR(v, r)




		#Get estimated state & plot
		[mx_old, my_old] = [m.x[0], m.x[1]]
		plot.line(mx_old, my_old, m.x[0], m.x[1], "red")


		if msvcrt.kbhit(): key = msvcrt.getch() 
		else: key = "" 
		if key == "q": break

		#Update plot
		#pyplot.draw()

		loop_time = time.clock() - time_start
		print loop_time, loop_time < dt
		if loop_time < dt: time.sleep(dt-loop_time)



	lab.robot["alpha1"].robot.Stop()

	lab.deinit()



main()