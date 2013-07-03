import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from lib import pyrobot
from lib import cricket

#Initialise cricket and iRobot objects
cricketList = cricket.cricketScan()
crickets = cricket.buildDictionary(cricketList, 'id')
r = pyrobot.Roomba()

print "running"

r.sci.Wake()
r.Control()

#r.DriveStraight(pyrobot.VELOCITY_FAST)
#time.sleep(1)
#r.TurnInPlace(pyrobot.VELOCITY_FAST, 'cw')
#time.sleep(0.5)

r.LED(1)
time.sleep(0.1)
r.LED(0)



r.Stop()
