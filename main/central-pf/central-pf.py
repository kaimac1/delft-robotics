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

	CAMERA = False

	# #List of hostnames of robots used
	# lab.robots = ["alpha1"]
	# lab.init("sched-trace")

	# #Use crickets in chirp mode
	# cricketList = cricketScan()
	# crickets = buildDictionary(cricketList, 'id')
	# for x in crickets:
	# 	crickets[x].setMode(MODE_LISTEN)

	# #Use camera
	# if CAMERA:
	# 	camera = lab.Camera()
	# 	camera.connect()

	# #Use gamepad
	# gamepad = lab.Joystick()

	#State-space model
	dt = 0.1
	m = EKFModel(4)
	def const_velocity(x,u):
		 return array([x[0] + x[2]*dt + 0.5*dt*dt*u[0],
		 			 x[1] + x[3]*dt + 0.5*dt*dt*u[1],
		 			 x[2] + u[0]*dt,
		 			 x[3] + u[1]*dt]).T
	m.f = const_velocity
	m.Q = eye(2)*1000
	m.R = eye(10)*20
	m.P = eye(4)*100


	#SS model for simulation
	ms = EKFModel(3)
	ms.dt = dt

	#Cricket locations and measurement equation
	#node_xy = ((-1810, -2080), (-1810, 0), (-1810, 2070), (-890, 3220), (680, 3220), (1630, 2040), (1630, -200), (1630, -2090), (740, -3250), (-870, -3250))
	node_xy = ((0, 1.5), (0.8, 1.5), (1.5, 0.5), (1.5, -0.5), (0.8, -1.5), (0, -1.5), (-0.8, -1.5), (-1.5, -0.5), (-1.5, 0.5), (-0.8, 1.5))

	node_height = 1230
	def h(x, i):
		return sqrt((x[0] - node_xy[i][0])**2 + (x[1] - node_xy[i][1])**2)

	q0 = 0.2
	x0 = lambda: array([random.gauss(0, q0), random.gauss(0, q0), 0, 0])
	q = 5
	r = 0.05
	process_noise = lambda: array([random.gauss(0, q), random.gauss(0, q)])
	sensor_likelihood = lambda y,x,i: normpdf(sqrt((x[0]-node_xy[i][0])**2 + (x[1]-node_xy[i][1])**2) - y, 0, r)

	pf = ParticleFilter(500, x0, const_velocity, process_noise)
	#print pf.x
	p_yx = lambda y,x: sensor_likelihood(y,x,0)
	#xe = pf.predict_update(2770, p_yx)
	#print xe
	#print pf.w
	#print pf.x

	#exit()




	#Wait for valid camera readings
	cx = 0; cy = 0
	if CAMERA:
		while cx == 0:
			[cx, cy, cb, valid] = camera.getxy()
	m.x = array([cx, cy, 0, 0]).T
	#lab.robot["alpha1"].set("goFlag", 1)

	plot = lab.Plot()
	plot.axes((-3,3),(-3,3))

	cx_old = 0
	cy_old = 0
	x = [0,0,0,0]

	data = []
	k = 0

	while True:

		k += 1
		t = k*dt

		time_start = time.clock()
		[mx_old, my_old] = [x[0], x[1]]

		data.append([mx_old, my_old, cx_old, cy_old])

		#Get control input from gamepad & send to robot
		#axes = gamepad.axes()
		#(v, r) = lab.axes2vr(axes)
		#lab.robot["alpha1"].robot.DriveVR(v, r)
		v = 1
		w = -2.405*sin(t)
		(vl, vr) = lab.vw2lr(v,w)
		#lab.robot["alpha1"].robot.DriveLR(vl, vr)
		ms.predict([v,w])

		#Schedule
		# mintrace = 1e6
		# for j in range(1,11):
		# 	def hj(x):
		# 		return h(x, j-1)
		# 	hx = hj(m.x)
		# 	if hx > 30:
		# 		#R = m.R[j-1,j-1] + hx
		# 		H = m.csdJacobian(hj, m.x)
		# 		PHT = m.P*(H.T)
		# 		S = H*PHT + m.R[j-1,j-1]
		# 		K = PHT / S
		# 		Pj = (eye(4) - K*H)*m.P
		# 		if trace(Pj) < mintrace:
		# 			mintrace = trace(Pj)
		# 			node = j

		node = random.randrange(1,11)
		node_name = "beac_" + str(node)

		#Get measurement
		#(nn, dist) = crickets[node_name].listen()
		dist = (h(ms.x, node-1) + random.gauss(0, 0.05))
		#for c in crickets:
		#	crickets[c].s.flush()
		print node, dist

		def hn(x):
			return h(x, node-1)
		m.h = hn

		#m.predict([0,0])
		#if dist > -1: m.updateSerial(dist, node-1)
		p_yx = lambda y,x: sensor_likelihood(y,x,node-1)
		x = pf.predict_update(dist, p_yx)

		#Get camera reading and plot if valid
		if not CAMERA:
			#[cx,cy,cb,valid] = camera.getxy()
			[cx,cy,valid] = [ms.x[0], ms.x[1], True]
			if valid:
				#cy += 100
				#cx -= 100
			 	plot.line(cx_old, cy_old, cx, cy, "blue")
		 		[cx_old, cy_old] = [cx, cy]		


		#Get estimated state & plot
		#for i in range(pf.N):
		plot.point(x[0], x[1], "red")
		#	plot.point(pf.x[i][0], pf.x[i][1], "red")
		plot.line(mx_old, my_old, x[0], x[1], "red")


		if msvcrt.kbhit(): key = msvcrt.getch() 
		else: key = "" 
		if key == "q": break

		loop_time = time.clock() - time_start
		print loop_time, loop_time < dt, t
		#if loop_time < dt: time.sleep(dt-loop_time)



	#lab.robot["alpha1"].robot.Stop()

	#lab.deinit()

	writer = csv.writer(open("C:/data.csv", 'w'))
	for row in data:
		writer.writerow(row)
	#writer.close()


main()