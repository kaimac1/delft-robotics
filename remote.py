#remote.py
#Kyle McInnes
#25 March 2013

#This implements a simple Pyro server which runs on the robots.
#It exposes the following commands to the host PC:
#	start(), stop()
#		These start and stop the main code, located at py/src/main/main.py
#	battery()
#		Returns the battery level in percent

import Pyro4
import socket
import shlex
import subprocess
import win32com.client
import pythoncom
from ctypes import windll

from 

#Windows stuff for a colour terminal
STD_OUTPUT_HANDLE = -11
stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

#Windows stuff for the battery level
wmi = win32com.client.GetObject('winmgmts:')
batt = wmi.InstancesOf('win32_battery')



class RemoteClass:
	def __init__(self):
		self.host = socket.gethostname().lower()
		self.processcmd = "python src/main/main.py"
		self.processargs = shlex.split(self.processcmd)
		self.pid = 0

	def start(self):
		print(self.host + " started")
		self.pid = subprocess.Popen(self.processargs)

	def stop(self):
		print(self.host + " stopped")
		self.pid.terminate()

	def battery(self):
		pythoncom.CoInitialize()
		return batt[0].EstimatedChargeRemaining

#Colour print
def pc(text, colour):
	windll.kernel32.SetConsoleTextAttribute(stdout_handle, colour)
	print text
	windll.kernel32.SetConsoleTextAttribute(stdout_handle, 0x7)


def main():
	remote = RemoteClass()
	pc("Hostname: " + remote.host, 0xE)
	
	#Start the Pyro server
	while True:
		try:
			Pyro4.Daemon.serveSimple ({remote:"alpha1.remote"}, host=remote.host, ns=True)
		except Pyro4.errors.NamingError:
			pc("Cannot locate the nameserver, retrying...", 0xC)

		

main()