from dnutils import logs

from .recognize import Voice
from .microphone import MicLevelController
from threading import Timer

logger = logs.getlogger(__name__ + 'REC', logs.DEBUG)

class VoiceRecorder():
    
    def __init__(self):
        self.voices = []
        self.voip = 0
        self.counter = 0
        self.recording = False

    def startListenerThread(self):
        
        newVoice = Voice(str(self.counter))
        if len(self.voices) < 2:
            self.voices.append(newVoice)
        else:
            if self.recording:
                Timer(0.6, self.startListenerThread).start()
                return
            self.voices[self.voip].stopRecording()
            self.voices[self.voip] = newVoice
            self.voip = (self.voip + 1) % 2
        newVoice.startRecording()
        self.counter += 1
        if self.counter < 20:
            Timer(0.6, self.startListenerThread).start()
        else:
            for v in self.voices:
                v.stopRecording()
        
    def start(self):
        logger.debug('Start recording...')
        self.startListenerThread()
        
    def record(self):
        self.recording = True

    def stop(self):
        self.recording = False
        self.counter = 0
        logger.debug('Stop recording.')
        print('"{}"'.format(self.voices[self.voip].analyze()))
        

if __name__ == '__main__':

    v = VoiceRecorder()
    mic = MicLevelController(sensitivity=1200, startCallback=v.record, endCallback=v.stop)
    mic.listen()
    v.start()
