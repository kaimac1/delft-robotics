import Pyro4
import time

r = Pyro4.Proxy("PYRONAME:alpha1.robot")

r.Init()

while r.get("goFlag") == 0:
	pass

print "go"

while r.get("goFlag") == 1:
	pass

#r.DriveStraight(VELOCITY_FAST)
#time.sleep(1)
#r.TurnInPlace(VELOCITY_FAST, 'cw')
#time.sleep(0.5)

#r.LED(1)
#time.sleep(0.1)
#r.LED(0)



r.Stop()
