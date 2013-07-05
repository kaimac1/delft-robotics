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
		zn = self.h(self.x)
		H = self.csdJacobian(self.h, self.x)

		#Compute new Kalman gain & update state estimate
		PHT = self.P*(H.T)
		S = H*PHT + self.R[measNum, measNum]
		K = PHT / S
		innov = (K*(z-zn)).T
		self.x = self.x + array(innov)[0]
		self.P = (eye(self.P.shape[0]) - K*H) * self.P

	#Get Jacobian via complex step differentiation
	def csdJacobian(self, f, x):
		n = x.shape[0]
		s = f(x).shape
		if len(s) == 0:
			m = 1
		else:
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

# #State-space model
# dt = 0.1
# m = EKFModel(4)
# def const_velocity(x,u):
# 	return array([x[0] + x[2]*dt + 0.5*dt*dt*u[0],
# 				 x[1] + x[3]*dt + 0.5*dt*dt*u[1],
# 				 x[2] + u[0]*dt,
# 				 x[3] + u[1]*dt]).T
# m.f = const_velocity
# m.Q = eye(2)*5
# m.R = eye(10)*0.02
# m.x = array([0,0,0,0]).T

# #Cricket locations and measurement equation
# node_xy = ((-13, 104), (-13, 312), (-13, 519), (79, 634), (236, 634), (331, 516), (331, 310), (242, -13), (81, -13))
# node_height = 153
# def sq(x, i):
# 	return sqrt((x[0] - node_xy[i][0])**2 + (x[1] - node_xy[i][1])**2 + node_height**2)

# while True:
# 	m.predict([0,0])
# 	def hn(x):
# 		return sq(x, 5)
# 	m.h = hn
# 	m.updateSerial(5,5)
# 	print m.x

# dt = 0.1
# def constant_velocity(x, u):
# 	return array([x[0] + u[0]*dt/2*(cos(x[2]+u[1]*dt) + cos(x[2])),
# 			  	  x[1] + u[0]*dt/2*(sin(x[2]+u[1]*dt) + sin(x[2])),
# 			  	  x[2] + u[1]*dt]).T

# m = EKFModel(3)
# m.dt = 0.1
# m.f = constant_velocity
# m.h = m.sens
# m.Q = eye(2)*4
# m.x = array([0,0,0]).T
# m.u = array([0,0])
# N = int(6.28/m.dt)
# data = zeros([3, N])

# for k in range(N):
# 	t = k*m.dt
# 	data[:, k] = mat(m.x).T
# 	m.predict([1,2.405*sin(t)])

# print m.x
# m.updateSerial(0, 0)
# print m.x
# m.predict([1,1])

# pyplot.plot(data[0,:].T, data[1,:].T, 'r')
# pyplot.show()



