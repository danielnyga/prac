'''
Created on Aug 24, 2012

@author: nyga
'''
import json
import urllib.error
import urllib.parse
import urllib.request
from subprocess import Popen, PIPE


class Voice(object):
    '''
    Implements an interface to the Google Speech Recognition API.
    Provides methods for recording speech from a microphone
    and sending it to the Google API.
    '''
    
    def __init__(self, name):
        self.arecord = None
        self.url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
#        self.url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=de-DE"
        self.header = {'Content-Type' : 'audio/x-flac; rate=16000'}
        self.wavFile = None
        self.wavName = None
        self.name = name
    
    def startRecording(self, duration=None):
        '''
        Initializes a recording process. Reqiures the 'arecord' programm installed.
        If the duration parameter is set, this method will block until the given 
        time of recording is up.
        '''
        self.wavName = '/tmp/wavFile_{}.wav'.format(self.name)
        self.wavFile = open(self.wavName, 'w+')
        cmdLine = ['/usr/bin/arecord']
        cmdLine.extend(['-f', 'S16_LE'])
        cmdLine.extend(['-t', 'wav'])
        cmdLine.extend(['-c', '1'])
        cmdLine.extend(['-r', '16000'])
        if duration != None:
            cmdLine.extend(['-d', str(duration)])
        self.arecord = Popen(cmdLine, stdout=self.wavFile, stderr=PIPE)
        if duration:
            self.arecord.wait()
        
    def stopRecording(self):
        '''
        Stops recording.
        '''
        if self.arecord != None:
            self.arecord.terminate()
            self.arecord = None
        if self.wavFile != None:
            self.wavFile.close()
            self.wavFile = None
    
    def analyze(self):
        '''
        Converts the recorded file to the .flac format
        and sends it to Google. Result is a JSON string
        with the hypotheses of written text.
        '''
        if self.wavName is None:
            return ""
        flacName = 'flacFile.flac'
        cmdLine = ['/usr/bin/ffmpeg']
        cmdLine.extend(['-i', self.wavName])
        cmdLine.extend(['-y'])
        cmdLine.extend([flacName])
        ffmpeg = Popen(cmdLine, stderr=PIPE)
        ffmpeg.wait()
        flacData = open(flacName, 'r').read()
        header = {'Content-Type' : 'audio/x-flac; rate=16000'}
        req = urllib.request.Request(self.url, flacData, header)
        answer = urllib.request.urlopen(req)
        self.wavName = None
        jsonResult = json.loads(answer.read())
        sentence = jsonResult.get('hypothesis', None)
        if sentence == '':
            sentence = None
        return sentence