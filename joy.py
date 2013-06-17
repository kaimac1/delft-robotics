import pygame
from math import *

pygame.init()
 
#Loop until the user clicks the close button.
done = False

# Initialize the joysticks
pygame.joystick.init()

# For each joystick:
joystick = pygame.joystick.Joystick(0)
joystick.init()
axes = joystick.get_numaxes()

def axes2vr(axes):

    x = axes[0]
    y = -axes[1]

    vel = sqrt(x*x + y*y)
    if y < 0: vel *= -1
    if abs(vel) > 1: vel /= vel
    vel *= 500

    angle = atan2(-x,y)
    if abs(angle) < 0.1:
        radius = 32768
    else:
        radius = cmp(angle, 0) - angle*(2/pi)
        radius *= 2000

        if radius < 0:
            radius -= 1
        else:
            radius += 1

    return (vel, radius)
    
# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    events = pygame.event.get() # User did something
        
    
    vals = []
    for i in range( axes ):
        vals.append(joystick.get_axis( i ))

    (v, r) = axes2vr(vals)

    print v, '\t', r

    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()

