import math
import time

from pracmln.mln.util import colorize


nounTags = ['NN', 'NNS', 'NNP', 'CD']
verbTags = ['VB', 'VBG', 'VBZ', 'VBD', 'VBN', 'VBP', 'MD']
adjTags = ['JJ', 'JJR', 'JJS']
posMap = {}
for n in nounTags:
    posMap[n] = 'n'
for v in verbTags:
    posMap[v] = 'v'
for a in adjTags:
    posMap[a] = 'a'

class StopWatch(object):
    
    def __init__(self):
        self.start = 0
        self.tags = []
        
    def tag(self, label, verbose=True):
        if verbose:
            print(label + '...')
        now = time.time()
        self.start = now
        if len(self.tags) > 0:
            self.tags[-1][0] = now - self.tags[-1][0]
        self.tags.append([now, label])
    
    def finish(self):
        now = time.time()
        if len(self.tags) > 0:
            self.tags[-1][0] = now - self.tags[-1][0]
    
    def reset(self):
        self.tags = []
        self.start = time.time()
        
    def printSteps(self):
        for t in self.tags:
            print('{}{}{} took {:f} sec.'.format(bash.BOLD, t[1], bash.END, t[0]))

def powerset(seq):
    '''
    Returns all the subsets of this set.
    '''
    if len(seq) <= 1:
        yield seq
        yield [] 
    else: 
        for item in powerset(seq[1:]):
            yield [seq[0]]+item 
            yield item

def unifyDicts(d1, d2):
    '''
    Adds all key-value pairs from d2 to d1.
    '''
    for key in d2:
        d1[key] = d2[key]

def dict_get(d, entry):
    e = d.get(entry, None)
    if e is None:
        e = {}
        d[entry] = e
    return e

def list_get(d, entry):
    e = d.get(entry, None)
    if e is None:
        e = []
        d[entry] = e
    return e

def difference_update(l1, l2):
    '''
    Removes all elements in l1 from l2.
    '''
    for e in l2:
        l1.remove(e)
        
        
def printListAndTick(l, t):
    if type(t) is str:
        t = l.index(t)
    for idx, item in enumerate(l):
        print('    [{}] {}'.format('X' if t==idx else ' ', colorize(item, (None, {True: 'yellow', False: 'white'}[t==idx], True), True)))
        
class bash:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    
def red(s):
    return bash.RED + s + bash.END

def bold(s):
    return bash.BOLD + s + bash.END

def green(s):
    return bash.OKGREEN + s + bash.END

def orange(s):
    return bash.ORANGE + s + bash.END


def logx(x):
    if x < 1E-30:
        return -200
    else:
        return math.log(x)
        
def combinations(domains):
    return _combinations(domains, [])

def _combinations(domains, comb):
    if len(domains) == 0:
        yield comb
        return
    for v in domains[0]:
        for ret in _combinations(domains[1:], comb + [v]):
            yield ret
