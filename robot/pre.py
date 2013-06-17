import Pyro4
import socket
import shlex
import subprocess

class RemoteClass:
	def __init__(self):
		self.host = socket.gethostname().lower()
		self.processcmd = "python remote.py"
		self.processargs = shlex.split(self.processcmd)
		self.pid = 0
		#self.start()

	def start(self):
		print(self.host + " remote started")
		self.pid = subprocess.Popen(self.processargs)

	def stop(self):
		print(self.host + " remote stopped")
		self.pid.terminate()

def main():
	pre = RemoteClass()

	#Start the Pyro server
	while True:
		try:
			Pyro4.Daemon.serveSimple ({pre:"alpha1.pre"}, host=pre.host, ns=True)
		except Pyro4.errors.NamingError:
			pc("Cannot locate the nameserver, retrying...", 0xC)

main()