import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Pyro4
from numpy.matlib import *
from lib.cricket import *
import time

r = Pyro4.Proxy("PYRONAME:alpha1.robot")
r.robot.Init()

r.set("dist", ("",-1))

cricketList = cricketScan()
crickets = buildDictionary(cricketList, 'id')
crickets["left1"].setMode(MODE_CHIRP)

while r.get("goFlag") != 1:
	pass
	
while r.get("goFlag") == 1:
	crickets["left1"].chirp()
	time.sleep(0.1)
	# if r.get("chirp") == True:
	# 	r.set("chirp", False)
	# 	time.sleep(0.12)
	# 	ts = time.clock()
	# 	dist = crickets["left1"].listen()
	# 	print time.clock() - ts
	# 	r.set("dist", dist)

print "gone"

r.robot.Stop()
