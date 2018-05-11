# 
#
# (C) 2011-2016 by Daniel Nyga (nyga@cs.uni-bremen.de)
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# 'Software'), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
from pprint import pprint

from pracmln.mln.util import avg
from scipy.stats import stats

from dnutils import edict, trace, out
from prac.db.ies import constants
from dnutils import edict


def tojson(obj):
    '''Recursively generate a JSON representation of the object ``obj``.'''
    if hasattr(obj, 'tojson'): 
        return obj.tojson()
    if type(obj) in (list, tuple):
        return [tojson(e) for e in obj]
    elif isinstance(obj, dict):
        return {str(k): tojson(v) for k, v in obj.iteritems()}
    return obj


def toplan(obj, lang='json'):
    '''Recursively generate a JSON or Lisp plan representation'''
    if hasattr(obj, 'toplan'):
        return obj.toplan(lang)
    if type(obj) in (list, tuple):
        return [toplan(e) for e in obj]
    elif isinstance(obj, dict):
        return {str(k): toplan(v) for k, v in obj.iteritems()}
    return obj


class Frame(object):
    '''
    Represents a (partially) instantiated action core that is stored in the MongoDB. 
    '''
    def __init__(self, prac, sidx, sentence, words, syntax, actioncore, actionroles, mandatory=True):
        self.sidx = sidx
        self.sentence = sentence
        self.actionroles = actionroles
        self.actioncore = actioncore
        self.syntax = syntax
        self.words = words
        self.prac = prac
        self.mandatory = mandatory

    def __str__(self):
        return '%s [%s]' % (self.actioncore, ', '.join(['%s: %s' % (k, v) for k, v in self.actionroles.items()]))

    def repstr(self):
        return '{} [{}]'.format(self.actioncore, ', '.join(['{}: {}'.format(k, v.repstr()) for k, v in self.actionroles.items() if k != 'action_verb' ]))

    def sim(self, f):
        '''
        Determines the frame similarity of this frame and another frame f.
        The frame similarity is calculated by taking the harmonic mean of the actionroles between the given frames.
        This value can be interpreted as the semantic similarity between the frames.
          
        :param f:     The frame this frame shall be compared to.
        :return:      The frame similarity of this frame and ``f``.
        '''
        # if 'action_verb' in self.actionroles and 'action_verb' in f.actionroles:
        #     verbsim = self.prac.wordnet.similarity(str(self.actionroles['action_verb'].type),
        #                                     str(f.actionroles['action_verb'].type), simtype='wup')
        # else:
        #     return 0
        #------------------------------------------------------------------------------ 
        # This is a sanity check to revoke false inferred 
        # frames during the information extraction process.
        # if verbsim  < 0.85: return 0
        #------------------------------------------------------------------------------ 
        sims = []
        for rolename, rolevalue in self.actionroles.items():
            if rolename in f.actionroles:
                if rolename == 'action_verb':
                    continue
                # sims.append(self.prac.wordnet.similarity(f.actionroles[rolename].type, rolevalue.type, simtype='wup'))
                sims.append(self.prac.wordnet.wup_similarity(f.actionroles[rolename].type, rolevalue.type))
            else:
                return 0
                #------------------------------------------------------------------------------ 
                #Sometimes Stanford Parser parses some objects as adjectives
                #due to the fact that nouns and adjectives cannot be compared
                #we define the the similarity between the instruction and the frame as zero
                #------------------------------------------------------------------------------ 
                # if sims[-1] == 0:
                #     return 0
        return 0 if not sims else avg(*sims)

    def specifity(self):
        '''
        '''
        return 1.0 - float(len(self.missingroles()))/len(self.prac.actioncores[self.actioncore].roles)

    def word(self, wid):
        for w in self.words:
            if w.wid == wid: return w
            
    def object(self, oid):
        for r, o in self.actionroles.iteritems():
            if o.id == oid: return o
        
    def copy(self):
        return Frame.fromjson(self.prac, self.tojson())
    
    def tojson(self):
        return tojson({constants.JSON_FRAME_SENTENCE: self.sentence,
                constants.JSON_FRAME_ACTIONCORE: self.actioncore,
                constants.JSON_FRAME_SYNTAX: self.syntax,
                constants.JSON_FRAME_WORDS: [w.tojson() for w in self.words],
                constants.JSON_FRAME_ACTIONCORE_ROLES: self.actionroles,
                constants.JSON_FRAME_MANDATORY: self.mandatory})

    def toplan(self, lang='json'):
        return {constants.JSON_FRAME_ACTIONCORE: self.actioncore,
                constants.JSON_FRAME_ACTIONCORE_ROLES: toplan(self.actionroles, lang=lang)}

    @staticmethod
    def fromjson(prac, data):
        return Frame(prac, 
                     sidx=data.get(constants.JSON_FRAME_SENTENCE_IDX),
                     sentence=data.get(constants.JSON_FRAME_SENTENCE),
                     syntax=data.get(constants.JSON_FRAME_SYNTAX),
                     words=data.get(constants.JSON_FRAME_WORDS),
                     actioncore=data.get(constants.JSON_FRAME_ACTIONCORE),
                     actionroles={r: Object.fromjson(prac, o) for r, o in data.get(constants.JSON_FRAME_ACTIONCORE_ROLES, {}).iteritems()},
                     mandatory=data.get(constants.JSON_FRAME_MANDATORY, True))
        
    def missingroles(self):
        return [r for r in self.prac.actioncores[self.actioncore].roles if r not in self.actionroles]

    def objects(self):
        return list(self.actionroles.values())

    def itersyntax(self):
        for predname, tuples in self.syntax:
            for w1, w2 in tuples:
                yield '%s(%s,%s)' % (predname, w1, w2) 

    def todb(self):
        for a in self.itersyntax(): yield a
        if 'action_verb' in self.actionroles:
            yield 'action_core(%s,%s)' % (self.actionroles['action_verb'].id, self.actioncore)
        else:
            yield 'action_core(ac-skolem,%s)' % self.actioncore
        for role, obj in self.actionroles.iteritems():
            yield '%s(%s,%s)' %(role, obj.id, self.actioncore)
            yield 'has_sense(%s,%s)' % (obj.id, obj.type)
            yield 'is_a(%s,%s)' % (obj.type, obj.type)
            yield 'has_pos(%s,%s)' % (obj.id, obj.syntax.pos)

    def __eq__(self, other):
        if other is None: return False
        if self.actioncore != other.actioncore: return False
        for role, obj in self.actionroles.items():
            if other.actionroles.get(role) != obj: return False
        for role, obj in other.actionroles.items():
            if self.actionroles.get(role) != obj: return False
        return True
    
    def __ne__(self, other):
        return not self == other
                

class Howto(Frame):
    '''
    Wrapper class representing a howto in PRAC.
    '''
    def __init__(self, prac, instr, steps, import_date=None):
        Frame.__init__(self, prac, sidx=instr.sidx, sentence=instr.sentence, syntax=instr.syntax,
                       words=instr.words, actioncore=instr.actioncore, actionroles=instr.actionroles)
        self.steps = steps
        if import_date is None:
            self.import_date = datetime.datetime.now()
        else:
            self.import_date = import_date

    def tojson(self):
        return tojson(edict({constants.JSON_HOWTO_IMPORT_DATE: self.import_date}) +\
               edict(Frame.tojson(self)) + edict({constants.JSON_HOWTO_STEPS: tojson(self.steps)}))

    @staticmethod
    def fromjson(prac, data):
        return Howto(prac,
                     instr=Frame.fromjson(prac, data), 
                     steps=[Frame.fromjson(prac, s) for s in data.get(constants.JSON_HOWTO_STEPS)],
                     import_date=data.get(constants.JSON_HOWTO_IMPORT_DATE))

    def toplan(self, lang='json'):
        return [toplan(step, lang=lang) for step in self.steps]

    def shortstr(self):
        s = 'Howto: %s\nSteps:\n' % Frame.__str__(self)
        s += '\n'.join([('  - %s' % f) for f in self.steps])
        return s

    def specifity(self):
        '''
        Computes how 'specific' this howto is.
        
        Specifity is defined in terms of the number of roles being assigned 
        in the steps relatively to the total number of roles. A howto with
        all roles assigned in all steps will thus have a specifity of 1,
        whereas one with all roles unknown has specifity of 0.
        '''
        specs = [s.specifity() for s in self.steps]
        specs.append(Frame.specifity(self))
        if any([s == 0 for s in specs]):
            return 0
        return stats.hmean(specs)

    def object_types(self):
        return set([c for s in self.steps for r, c in s.actionroles.items()])


class PropertyStore(object):
    '''Store for property values of objects'''
    
    def __init__(self, prac):
        self.prac = prac
        propmod = prac.module('prop_extraction')
        self.__props = [p.name for p in propmod.mln.predicates]
        for pred in self.__props:
            setattr(self, pred, None)

    def tojson(self):
        return {k: tojson(getattr(self, k)) for k in self.__props if getattr(self, k) is not None}

    def toplan(self, lang='json'):
        return {p: getattr(self, p) for p in self.__props if getattr(self, p) is not None}

    def items(self):
        for k, v in {p: getattr(self, p) for p in self.__props if getattr(self, p) is not None}.items():
            yield k, v

    @staticmethod
    def fromjson(prac, data):
        s = PropertyStore(prac)
        for k, v in data.items(): setattr(s, k, v)
        return s
    
    def __eq__(self, other):
        return self.tojson() == other.tojson()

    def __ne__(self, other):
        return not self == other
    
        
class Object(object):
    '''
    Representation of a generic object that has an id and a type.
    '''
    def __init__(self, prac, id_, type_, props=None, syntax=None):
        self.type = type_
        self.id = id_
        if isinstance(props, PropertyStore):
            self.props = props
        else:
            self.props = PropertyStore(prac)
        if isinstance(props, dict):
            for k, v in props.iteritems(): setattr(self.props, k, v)
        self.syntax = syntax
        self.prac = prac

    def tojson(self):
        return tojson({constants.JSON_OBJECT_ID: self.id,
                constants.JSON_OBJECT_TYPE: self.type,
                constants.JSON_OBJECT_PROPERTIES: self.props,
                constants.JSON_OBJECT_SYNTAX: self.syntax})

    def toplan(self, lang='json'):
        return toplan(edict({constants.JSON_OBJECT_TYPE: self.type}) + edict(self.props.toplan(lang=lang)))

    def copy(self):
        return Object.fromjson(self.prac, self.toplan())

    @staticmethod
    def fromjson(prac, data):
        return Object(prac,
                      type_=data.get(constants.JSON_OBJECT_TYPE),
                      id_=data.get(constants.JSON_OBJECT_ID),
                      props=PropertyStore.fromjson(prac, data.get(constants.JSON_OBJECT_PROPERTIES, {})),
                      syntax=Word.fromjson(prac, data.get(constants.JSON_OBJECT_SYNTAX)))
    
    def __eq__(self, other):
        if other is None: return False
        if self.props != other.props: return False
        return self.type == other.type

    def __ne__(self, other):
        return not self == other    
    
    def __repr__(self):
        return '<Object id=%s type=%s at 0x%x>' % (self.id, self.type, hash(self))

    def repstr(self):
        return '{}'.format(self.type)

    def __str__(self):
        return repr(self)#'%s: %s' % (self.id, self.type)

    def matches(self, obj):
        if obj.type not in self.prac.wordnet.hypernyms_names(self.type):
            return False
        for prop, val in obj.props.items():
            if val is None or prop in ('in', 'on'):
                continue
            if getattr(self.props, prop) is None or val != getattr(self.props, prop):
                return False
        return True


class Word(object):
    '''
    This class represents a data structure of a word in a sentence.
    Sense objects are used to determine the meaning of a sentence.
    A sense object is always included in a frame, which contains a set of senses.
    WordNet is used to assign the senses.
    '''

    def __init__(self, prac, wid, word, widx, sense, pos, lemma, misc=None):
        self.wid = wid
        self.word = word
        self.widx = widx
        self.sense = sense
        self.pos = pos
        self.lemma = lemma
        self.misc = misc
        self.prac = prac

    def tojson(self):
        return tojson({constants.JSON_SENSE_WORD_ID: self.wid, 
                constants.JSON_SENSE_WORD: self.word,
                constants.JSON_SENSE_LEMMA: self.lemma,
                constants.JSON_SENSE_POS: self.pos,
                constants.JSON_SENSE_WORD_IDX: self.widx,
                constants.JSON_SENSE_SENSE: self.sense,
                constants.JSON_SENSE_MISC: self.misc})

    @staticmethod    
    def fromjson(prac, data):
        return Word(prac, 
                    data.get(constants.JSON_SENSE_WORD),
                    data.get(constants.JSON_SENSE_WORD),
                    data.get(constants.JSON_SENSE_WORD_IDX),
                    data.get(constants.JSON_SENSE_SENSE),
                    data.get(constants.JSON_SENSE_POS),
                    data.get(constants.JSON_SENSE_LEMMA))


class Worldmodel(object):

    def __init__(self, prac, cw=False):
        self.prac = prac
        self.cw = cw
        self.available = {}
        self.unavailable = set()

    def contains(self, concept):
        hypernyms = reduce(lambda a, b: a | b, [set(self.prac.wordnet.hypernyms_names(o.type)) for o in self.available.values()])
        if concept in hypernyms:
            return True
        if concept in self.unavailable or self.cw:
            return False

    def __contains__(self, o):
        return self.contains(o)

    def add(self, obj):
        self.available[obj.id] = obj
        if obj.type in self.unavailable:
            self.unavailable.remove(obj.type)

    def remove(self, objid, cw=True):
        obj = self.available.get(objid)
        if obj is None: return
        del self.available[objid]
        if cw and obj.type not in self:
            self.unavailable.add(obj.type)

    def getall(self, obj):
        if type(obj) is str:
            obj = Object(self.prac, self.newid(), type_=obj)
        objects = []
        for id_, o in self.available.items():
            if o.matches(obj):
                objects.append(o)
        return objects

    def removeall(self, concept, cw=True):
        for o in self.getall(concept):
            self.remove(o.id)
        if cw:
            self.unavailable.add(concept)

    def newid(self):
        i = 0
        while 'id-%s' % i in self.available:
            i += 1
        return 'id-%s' % i

    def __str__(self):
        return str({o.id: o.type for o in self.available.values()}) + '{%s}' % ','.join(['!%s' % c for c in self.unavailable])


if __name__ == '__main__':
    from prac.core.base import PRAC
    prac = PRAC()
    o1 = Object(prac, 'w1', 'coffee_cup.n.01', syntax=Word(prac, 'water-1', 'water', 1, 'water.n.06', 'NN', 'water'), props={'color': 'green.n.01'})
    print o1
    print repr(o1)
    pprint(o1.tojson())

    wm = Worldmodel(prac)
    wm.add(o1)
    # wm.remove(o1.id, True)
    print wm.contains('cup.n.01')

