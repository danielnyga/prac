# PRAC -- SEMCORE CORPUS CONVERSION
#
# (C) 2011-2014 by Daniel Nyga (nyga@cs.uni-bremen.de)
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys, bs4

from dnutils import logs

from prac import java
from pracmodules import StanfordParser

sys.modules['BeautifulSoup'] = bs4
import lxml.html.soupparser as p
import os
from nltk.corpus import wordnet

logger = logs.getlogger(__name__)

java.classpath.append(os.path.join('3rdparty', 'stanford-parser-2015-12-09', 'stanford-parser.jar'))
grammarPath = os.path.join('3rdparty', 'stanford-parser-2015-12-09', 'grammar', 'englishPCFG.ser.gz')

def readSemcor3File(filename):
    '''
    Reads an XML semcore3.0 file and returns a corresponding MLN database.
    '''
    if not java.isJvmRunning():
            java.startJvm()
    tree = p.parse(filename)
    parser = StanfordParser(grammarPath)
    for e in tree.iter():
        if e.tag == 's':
            s, atoms = reconstruct(e)
            print('//', s)
            for a in atoms:
                print(a)
            deps = parser.get_dependencies(s)
            depstr = list(map(str, deps))
            # do some sanity check
            
            for d in depstr:
                print(d) 
            print('---')

def reconstruct(s_element):
    sentence = []
    wf_count = 1
    gnd_atoms = []
    for e in s_element.iter():
        if e.text is not None:
            sentence.append(e.text)
        if e.tag == 'wf':
            wf_count += 1
            word_const = '{}-{:f}'.format(e.text, wf_count)
            if e.get('pos', None) is not None:
                gnd_atoms.append('has_pos({},{})'.format(word_const, e.get('pos')))
            if e.get('lemma', None) is not None:
                lem = e.get('lemma')
                lexsn = e.get('lexsn')
                synset = None
                for l in wordnet.lemmas(lem):
                    if l.key == '{}%%{}'.format(lem, lexsn):
                        synset = l.synset
                if synset is not None:
                    sid = 's-{}'.format(word_const)
                    gnd_atoms.append('has_sense({},{})'.format(word_const, sid))
                    gnd_atoms.append('is_a({},{})'.format(sid, synset.name))
    sentence = ' '.join(sentence).strip()
    return sentence, gnd_atoms
    
if __name__ == '__main__':
    path = os.path.join('/', 'home', 'nyga', 'work', 'nl_corpora', 'semcor3.0', 'brown1', 'tagfiles')
    readSemcor3File(os.path.join(path, 'br-a01'))
