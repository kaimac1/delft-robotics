import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Pyro4
from numpy.matlib import *
import time

r = Pyro4.Proxy("PYRONAME:alpha1.robot")
model = Pyro4.Proxy("PYRONAME:alpha1.model")

r.robot.Init()
r.set("x", array([0,0,0]).T)
v = w = 0

ot = time.clock()

while r.get("goFlag") != 1:
	updateX = r.get("updateX")
	if updateX != None:
		print "updating x to", updateX
		model.set("x", updateX)
		r.set("updateX", None)

while r.get("goFlag") == 1:
	#Get time delta
	dt = time.clock() - ot
	ot = time.clock()
	#print "dt = ", dt

	#Receive control inputs
	v = r.get("v")
	w = r.get("w")
	if v == None: v = 0
	if w == None: w = 0

	#Model prediction
	model.set("dt", dt)
	model.predict([v, w])

	#Send back state estimate
	r.set("x", model.get("x"))

print "gone"

r.robot.Stop()
