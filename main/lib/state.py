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


class ParticleFilter():
	def __init__(self, N, x0_sample, f, w_sample):
		self.x = []
		self.w = []
		self.N = N
		self.f = f
		self.w_sample = w_sample
		#Create initial distribution of particles
		for i in range(self.N):
			self.x.append(x0_sample())
			self.w.append(1.0/N)

	def predict_update(self, y, p_y_given_x):
		for i in range(self.N):
			self.x[i] = self.f(self.x[i], self.w_sample())
			self.w[i] *= p_y_given_x(y, self.x[i])

		w_sum = sum(self.w)
		for i in range(self.N):
			self.w[i] = self.w[i] / w_sum
		print y, p_y_given_x(y, self.x[i])

		#estimate state
		self.xest = 0
		for i in range(self.N):
			self.xest += self.w[i]*self.x[i]

		#N_eff = 1.0/w_sum
		#resample
		xnew = []
		try:
			idx = random.choice(range(self.N), self.N, replace=True, p=self.w)
		except:
			print self.w
		for i in idx:
			xnew.append(self.x[i])
		self.x = xnew
		for i in range(self.N):
			self.w[i] = 1.0/self.N

		return self.xest



def normpdf(x, mu, sigma):
	u = float((x-mu) / abs(sigma))
	y = exp(-u*u/2) / (sqrt(2*pi) * abs(sigma))
	return y