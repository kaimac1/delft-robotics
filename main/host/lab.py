#lab.py
#Kyle McInnes
#25 March 2013

#Functions used to connect to and control robots from within an experiment file

import Pyro4
import shutil
import os
import socket
import time
from struct import *
import pygame
from math import *
import threading

robot = {}
remote = {}
pre = {}
Pyro4.config.HMAC_KEY = "dcsc"

#Uploads latest code to robots and starts it running
def init(experiment):
	global remote
	path = os.path.dirname(os.path.abspath(__file__))

	#Connect to pre-remote and stop remote
	for hostname in robots:
		pre[hostname] = Pyro4.Proxy("PYRONAME:"+hostname+".pre")
		try:
			pre[hostname].stop()
		except:
			pass

	#Upload the latest code
	print "Uploading code for " + experiment + " to:",
	for hostname in robots:
		print hostname,
		try:
			shutil.rmtree("\\\\"+hostname+"\\py\\src")
		except:
			pass
		os.makedirs("\\\\"+hostname+"\\py\\src\\main")
		shutil.copy(path+"\\__init__.py", "\\\\"+hostname+"\\py\\src\\__init__.py")
		shutil.copy(path+"\\..\\"+experiment+"\\"+hostname+".py", "\\\\"+hostname+"\\py\\src\\main\\main.py")
		shutil.copytree(path+"\\..\\lib", "\\\\"+hostname+"\\py\\src\\lib")

	print

	#Then restart the remote, connect to it and start the main robot code running
	for hostname in robots:
		pre[hostname].start()
	time.sleep(2)

	for hostname in robots:
		remote[hostname] = Pyro4.Proxy("PYRONAME:"+hostname+".remote")
		robot[hostname] = Pyro4.Proxy("PYRONAME:"+hostname+".robot")
		remote[hostname].start()

def deinit():
	global remote

	for hostname in robots:
		remote[hostname].stop()

class CameraPoll(threading.Thread):
	def __init__(self, connection):
		self.conn = connection
		self.bufsize = 128
		self.new = False
		threading.Thread.__init__(self)

	def run(self):
		while True:
			data = self.conn.recv(self.bufsize)
			if len(data) == 10:
				packet_id, packet_size, car_id, state = unpack("!HHLH", data)
				print "rx packet:", car_id, state
				robot[robots[0]].robot.LED(state)

				time.sleep(0.1)
				#packet = pack("!HHLH", 1, 6, car_id, state)
				packet = pack("!HHLH", 1, 10, 3, state)
				self.conn.send(packet)
				#packet = pack("!LH", car_id, state)
				#self.conn.send(packet)
			if len(data) > 10:
				try:
					self.packet_id, self.packet_size, self.frame, self.numcars, self.car_id, self.x, self.y, self.hdg = unpack("!HHlHLfff", data)
					self.new = True
					#print self.x, self.y, self.hdg
				except:
					self.new = False
			time.sleep(0.05)

#Camera class
class Camera():
	def __init__(self):
		pass

	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind(("127.0.0.1", 1968))
		print "Waiting for connection to AGVsock...",
		self.s.listen(1)
		self.conn, self.addr = self.s.accept()
		print "connected."

		packet = pack("!HH", 2, 6)
		self.conn.send(packet)
		packet = pack("!Hl", 1, 3)
		self.conn.send(packet)

		self.pollthread = CameraPoll(self.conn)
		self.pollthread.start()

	def getxy(self):
		if (self.pollthread.new):
			return [self.pollthread.x, self.pollthread.y, self.pollthread.hdg]
		else:
			return [0, 0, 0]


	def disconnect(self):
		self.s.close()

#Gamepad/Joystick class
class Joystick():
	def __init__(self):
		pygame.init()
		pygame.joystick.init()
		#Just use the first joystick
		self.stick = pygame.joystick.Joystick(0)
		self.stick.init()
		self.numAxes = self.stick.get_numaxes()

	def axes(self):
		events = pygame.event.get()
		axisValues = []
		for i in range(self.numAxes):
			axisValues.append(self.stick.get_axis(i))
		return axisValues

#Convert gamepad axes to velocity & radius
def axes2vr(axes):

	x = axes[0]
	y = -axes[1]

	vel = sqrt(x*x + y*y)
	if y < 0: vel *= -1
	if abs(vel) > 1: vel /= abs(vel)
	vel *= 500

	angle = atan2(-x,y)
	if abs(angle) < 0.1:
		radius = 32768
	else:
		radius = cmp(angle, 0) - angle*(2/pi)
		radius *= 500

		if radius < 0:
			radius -= 1
		else:
			radius += 1

	return (vel, radius)

#Convert gamepad axes to forward velocity & angular velocity
def axes2vw(axes):

	x = -axes[0]
	y = -axes[1]

	vt = y * 500 *0.5
	omega = x * 1.9 * 0.5

	if abs(vt) < 0.01: vt = 0
	if abs(omega) < 0.01: omega = 0

	return (vt, omega)

#Convert forward & angular velocity to left & right wheel velocities
def vw2lr(vt, omega):

	vl = int(vt - 129*omega)
	vr = int(vt + 129*omega)

	return (vl, vr)