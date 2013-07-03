import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Pyro4
from numpy.matlib import *
import time

r = Pyro4.Proxy("PYRONAME:alpha1.robot")
r.robot.Init()

ot = time.clock()

while r.get("goFlag") != 1:
	pass
	
while r.get("goFlag") == 1:
	#Get time delta
	dt = time.clock() - ot
	ot = time.clock()

	#Receive control inputs
	v = r.get("v")
	w = r.get("w")
	if v == None: v = 0
	if w == None: w = 0

print "gone"

r.robot.Stop()
