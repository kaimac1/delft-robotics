import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import msvcrt
from host import lab
from lib.cricket import *

#Use camera
camera = lab.Camera()
camera.connect()

while True:
	pass

