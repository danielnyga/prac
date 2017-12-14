'''
Created on Aug 24, 2012

@author: nyga
'''

import alsaaudio, time, audioop
import thread

class MicLevelController(object):
    '''
    This class implements a wrapper for accessing
    some simple microphone functionality. It porvides
    callback services for 'noise' perceived by the mic
    exceeding and deceeding some noise level. 
    '''
    
    def __init__(self, startCallback=None, endCallback=None, waitTime=1, sensitivity=1000):
        self.waitTime = waitTime
        self.sensitivity = sensitivity
        self.startCallbacks = []
        self.endCallbacks = []
        if startCallback != None:
            self.startCallbacks.append(startCallback)
        if endCallback != None:
            self.endCallbacks.append(endCallback)

    def registerStartCallback(self, callback):
        '''
        Registers a new callback for a starting noise event.
        '''
        self.startCallbacks.append(callback)
        
    def registerEndCallback(self, callback):
        '''
        Registers a new callback for a stopping noise event.
        '''
        self.endCallbacks.append(callback)
        
    def listen(self):
        '''
        Starts a listener thread on the mic.
        '''
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)
        inp.setchannels(1)
        inp.setrate(8000)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        inp.setperiodsize(160)
        
        def listenerThread(device):
            lastSignalHeard = -1
            hearing = False
            while True:      # Read data from device
                l, data = device.read()
                if l: # Return the maximum of the absolute value of all samples in a fragment.
                    signal = audioop.max(data, 2)
                    currentTime = time.time()
                    if signal > self.sensitivity:
                        lastSignalHeard = currentTime
                        if hearing: continue
                        hearing = True
                        for fcn in self.startCallbacks: fcn()
                    elif signal < self.sensitivity and lastSignalHeard < currentTime - self.waitTime and hearing:
                        for fcn in self.endCallbacks: fcn()
                        hearing = False
                time.sleep(.001)
        thread.start_new_thread(listenerThread,(inp,))
            
if __name__ == '__main__':
    print 'Starting...'
    def start():
        print 'I hear something...',
        
    def end():
        print 'now it stopped.'
    
    l = MicLevelController(start, end, sensitivity=1200)
    l.listen()
    
    while True:
        pass
