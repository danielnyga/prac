import urllib2
from HTMLParser import HTMLParser

import pygame


# create a subclass and override the handler methods
class DownloadLinkExtractor(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.start = False
    
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if  tag == 'a':
            if attrs.get('href', None).endswith('.mp3'):
                self.downloadlink = attrs.get('href', None)
            
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        pass

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    
    voices = ['nitech_us_slt_arctic_hts',
              'nitech_us_rms_arctic_hts']
    
    url = 'http://www.text2speech.org'
    text = 'What should I use for flipping the pancake?'
    voice = voices[1]
    
    params = "speech=" + text + "&voice=" + voice + "&volume_scale=1&make_audio=Convert Text To Speech"
    header = {"Content-type": "application/x-www-form-urlencoded",
              "Content-length": len(params),
              "Connection": "close"}
    
    req = urllib2.Request(url, params, header)
    answer = urllib2.urlopen(req).read()
    
    parser = DownloadLinkExtractor()
    parser.feed(answer)
    mp3file = urllib2.urlopen(url + '/' + parser.downloadlink)
    sout = open('/tmp/sayit.mp3', 'w+')
    sout.write(mp3file.read())
    sout.close()
    pygame.mixer.music.load("/tmp/sayit.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): 
        pygame.time.Clock().tick(10)    
    

