from numpy.matlib import *
from time import time
#from matplotlib import pyplot 

#Nonlinear discrete-time system with non-additive noise on the inputs:
#	x(k+1) = f(x(k), u(k) + q(k))
#	y(k)   = h(x(k)) + r(k)
class EKFModel():
	#System function f(x,u), measurement function h(x), state and input

	def __init__(self, dim = 3):
		#Process, measurement and state covariance
		self.Q = 1
		self.R = self.P = eye(dim)
		self.f = self.unicycle
		self.h = self.sens
		self.u = array([0,0])
		self.x = array([0,0,0]).T
		self.dt = 1

	#EKF predict from new control input
	def predict(self, unew):
		self.u = array(unew)
		#New state estimate
		self.x = self.f(self.x, self.u)

		#Compute the Jacobians df/dx|x,u and df/du|x,u
		J = self.csdJacobian(lambda x: self.f(x,self.u), self.x)
		L = self.csdJacobian(lambda u: self.f(self.x,u), self.u)

		#Update state covariance
		self.P = J*self.P*J.T + L*self.Q*L.T		

	#EKF update from complete set of new measurements
	def update(self, unew):
		pass

	#EKF serial update from single new measurement
	def updateSerial(self, z, measNum):
		#New measurement & Jacobian
		zn = h(self.x)
		H = self.csdJacobian(h, self.x)

		#Compute new Kalman gain & update state estimate
		PHT = self.P*(H.T)
		S = H*PHT + self.R[measNum, measNum]
		K = PHT / S
		self.x = self.x + (K*(z - zn)).T
		self.P = (eye(self.P.shape[0]) - K*H) * self.P

	#Get Jacobian via complex step differentiation
	def csdJacobian(self, f, x):
		n = x.shape[0]
		m = f(x).shape[0]
		J = zeros([m, n])
		h = n*spacing(1)

		for k in range(n):
			x1 = x + 0j
			x1[k] = x1[k] + h*1j
			J[:,k] = mat(f(x1).imag/h).T
		return J

	def get(self, attr):
		try:
			return getattr(self, attr)
		except:
			return None

	def set(self, attr, value):
		setattr(self, attr, value)

	#Unicycle model (discretised via Tustin's method)
	def unicycle(self, x, u):
		return array([x[0] + u[0]*self.dt/2*(cos(x[2]+u[1]*self.dt) + cos(x[2])),
				  	  x[1] + u[0]*self.dt/2*(sin(x[2]+u[1]*self.dt) + sin(x[2])),
				  	  x[2] + u[1]*self.dt]).T

	def sens(self, x):
		return array([x[0]])

dt = 0.1

def constant_velocity(x, u):
	return array([x[0] + u[0]*dt/2*(cos(x[2]+u[1]*dt) + cos(x[2])),
			  	  x[1] - u[0]*dt/2*(sin(x[2]+u[1]*dt) + sin(x[2])),
			  	  x[2] + u[1]*dt]).T

# m = EKFModel(3)
# m.dt = 0.1
# m.f = constant_velocity
# m.h = m.sens
# m.Q = eye(2)*4
# print m.Q
# m.x = array([0,0,0]).T
# m.u = array([0,0])
# N = int(6.28/m.dt)
# data = zeros([3, N])

# for k in range(N):
# 	t = k*m.dt
# 	data[:, k] = mat(m.x).T
# 	m.predict([1,2.405*sin(t)])

# pyplot.plot(data[0,:].T, data[1,:].T, 'r')
# pyplot.show()

# print m.P
# m.updateSerial(0, 0)
# print m.x
# print m.P

