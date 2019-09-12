#This code has for objective to simulate 4 beam interference with different polarizations and directions and to calculate the resulting potential.
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate

class Ewave():
    #general wave considered as a collection of plane waves
    def __init__(self, Epwaves):
        self.Epwaves = Epwaves
        self._same_freq()

    def __radd__(self, values):
        copy1 = self.Epwaves.copy()
        copy2 = values.Epwaves.copy()
        return Ewave(copy1+copy2)

    def _same_freq(self):
        #Checks if all frequencies of the plane waves are the same. It modifies the value of self.same_freq. (Avoids having to recalculate every time)
        #1st case: all epwaves have the same period => then ignore time dependence in intensity since abs(e^(iwt)) = 1
        #Make sure it's called after each change to the self.Epwaves!
        w1 = self.Epwaves[0].pulsation
        res = True
        for plane_wave in self.Epwaves:
            res *= (plane_wave.pulsation == w1)
        self.same_freq = res
        if self.same_freq:
            self.w = w1


    def value(self, t, x, y, z, time = True):
        sum = 0
        
        for E in self.Epwaves:
            if self.same_freq:
                sum += E.rvalue(x, y, z)
            else:
                sum += E.value(t, x, y, z)
        sum = np.exp(1j*(self.w*t))*sum if self.same_freq and time else sum #multiplies by phase term after sum if time = true and waves have the same frequency
        return sum
    
    def intensity(self, t, x, y, z):
        #calculates the intensity of the packet of plane waves (square of field value)
        return np.abs(self.value(t, x, y, z))**2

    def tavg_intensity(self, x, y, z):
        if self.same_freq:
            #if all waves have the same angular frequency:
            res = np.linalg.norm(self.value(0, x, y, z, time=False), axis=0) #provide a dummy time if time is set to false.
            if isinstance(x, np.ndarray):
                return res.reshape(x.shape)
            return res
        else:
            return "Not Implemented"
    



        


    

class Epwave():
    #plane wave class
    def __init__(self, amplitude, polarization, w, kvector, phase):
        self.amplitude = amplitude
        self.polarization = polarization
        self.pulsation = w
        self.kvector = kvector
        self.phase = phase
    def value(self, t, x,y,z):
        #provides the value of the field at position x, y, z
        r = np.array(x, y, z)
        return self.polarization*self.amplitude*np.exp(1j*(self.pulsation*t-np.dot(self.kvector, r)+self.phase))
    def rvalue(self, x, y, z):
        #provides the value of the position part of the field at x, y, z. Time dependency is ignored. Useful when summing plane waves with same periodicity.
        r = []
        if isinstance(z, int) and isinstance(x, np.ndarray):
            r = np.vstack([ x.reshape(-1), y.reshape(-1), np.zeros(x.shape).reshape(-1)])
            #print(r)
        else:
            r = np.vstack((x,y,z))  
        kprod = np.dot(self.kvector, r)  
        e = np.exp(1j*self.phase-1j*kprod)*self.amplitude
        res = np.array(list(map(lambda x: self.polarization*x, e))).T
        #print(res)
        return res
        

    def intensity(self, t, x, y, z):
        return np.abs(self.value(t, x, y, z))**2
    def tavg_intensity(self, x, y, z):
        one_over_period = self.pulsation/(2*np.pi)
        I = lambda t: self.intensity(t, x, y, z)
        return one_over_period*integrate.quad(I, 0, 1/one_over_period)
    def __add__(self, value):
        return Ewave([self, value])
    def __radd__(self, values : Ewave):
        copy = values.Epwaves.copy()
        copy.append(self)
        return Ewave(copy)

##test of class with four waves:
#we set lambda = 1 = c thus lambda = 1, kmag = 2*pi, w = 1/(2*pi)
#k vectors:
kmag = 2*np.pi
k1 = kmag*np.array([1,0,0])
k2 = kmag*np.array([0,1,0])
k3 = kmag*np.array([-1,0,0])
k4 = kmag*np.array([0,-1,0])
#amplitudes:
e1, e2, e3, e4 = 0.6,1,0.55,1
#phases:
ph = [0, 90, 0, -75]
ph1, ph2, ph3, ph4 = list(map(lambda x: x*np.pi/180, ph))
#polarization:
p1,p2,p3,p4 = np.array([0,0,1]),np.array([0,0,1]), np.array([0,0,1]), np.array([0,0,1])
#angular freq:
w = 1/(2*np.pi)

#initialization of Ep waves:

E1 = Epwave(e1, p1, w, k1, ph1)
E2 = Epwave(e2, p2, w, k2, ph2)
E3 = Epwave(e3, p3, w, k3, ph3)
E4 = Epwave(e4, p4, w, k4, ph4)

Sum = E1+E2+E3+E4

X = np.arange(3, step=0.01)
Y = np.arange(3,  step=0.01)
xx, yy = np.meshgrid(X, Y)
zz = np.zeros(xx.shape)
Z = Sum.tavg_intensity(xx, yy, 0)
print(f"value = {Z}")
h = plt.contourf(xx, yy, Z)
plt.show()
print(Sum.value(1,1,1,1))
print(Sum.tavg_intensity(1,1,1))