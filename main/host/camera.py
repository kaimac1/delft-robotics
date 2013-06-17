import socket
from struct import *

class Camera():
	def __init__(self):
		self.bufsize = 32

	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind(("127.0.0.1", 1968))
		print "Waiting for connection to AGVsock...",
		self.s.listen(1)
		self.conn, self.addr = self.s.accept()
		print "connected."

		packet = pack("!HH", 2, 6)
		self.conn.send(packet)
		packet = pack("!Hl", 1, 2)
		self.conn.send(packet)

	def poll(self):
		data = self.conn.recv(self.bufsize)
		if len(data) == 10:
			packet_id, packet_size, car_id, state = unpack("!HHLH", data)
			print "rx packet:", car_id, state

	def disconnect(self):
		self.s.close()