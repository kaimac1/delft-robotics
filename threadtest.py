import threading
import time

class Poll(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.i = 0

	def run(self):
		while True:
			print "hello " + str(self.i)
			self.i += 1
			time.sleep(1)


t = Poll()
t.start()

while True:
	print "i = " + str(t.i)
	time.sleep(0.1)

