# PROBABILISTIC ROBOT ACTION CORES - INFERENCE
#
# (C) 2012 by Daniel Nyga (nyga@cs.tum.edu)
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

from collections import defaultdict

from dnutils import logs
from graphviz.dot import Digraph

from prac.db.ies.models import Object, Frame, Word
from prac.pracutils import StopWatch
from prac.pracutils.pracgraphviz import render_gv
from prac.pracutils.utils import splitd
from pracmln import Database


logger = logs.getlogger(__name__, level=logs.INFO)


class PRACInferenceStep(object):
    '''
    Wrapper class encapsulating a single inference step in the PRAC
    pipeline. It consists of n input databases and m output databases.
    '''
    def __init__(self, node, module):
        '''
        Initializes the inference step.
        
        :param pracinfer:   reference to the PRACInference object.
        :param module:      reference to the PRACModule performing this
                            inference step.
        :param indbs:   list of databases taken as inputs.
        '''
#         self.indbs = [db.copy() for db in node.outdbs]
        self.indbs = []
        self.module = module
        self.node = node
        self.node.infchain.append(self)
        self.outdbs = []
        self.watch = StopWatch()



class PRACInferenceNode(object):
    '''
    Abstract node in the inference tree spanned by the PRAC
    reasoning pipeline.
    '''
    def __init__(self, pracinfer, parent, pred, indbs, prevmod=None):
        self.pracinfer = pracinfer
        self.parent = parent
        self.infchain = []
        self.previous_module = None
        if parent:
            parent.children.append(self)
        self.previous_module = prevmod
        self.pred = pred
        self.children = []
        self.indbs = indbs
    
    def idx(self):
        '''
        The index of the inference node 
        '''
        preds = 0
        pred = self.pred
        while pred is not None: 
            preds += 1
            pred = pred.pred
        return preds
    
    
    def iterpreds(self):
        '''
        Iterates over all predecessors of this node backwards.
        '''
        pred = self.pred
        while pred is not None:
            yield pred
            pred = pred.pred
    
    
    def rdfs(self, goaltest, all=False):
        '''
        Performs a 'reverse' depth-first search starting from this node.
        
        :param goaltest:    callable specifying the goal test
        :param all:         whether or not all solutions are being returned 
        '''
        q = list(reversed(list(self.parentspath()))) + [self] 
        parents = list(q)
        processed = set()
        while q:
            n = q.pop()
            if n in processed: continue
            processed.add(n)
            if goaltest(n) and n not in parents:
                yield n
                if not all: return
            q.extend(reversed(list(n.iterpreds())))
            if n not in parents:
                q.extend(list(n.children))
    
    
    def parentspath(self):
        parent = self.parent
        while parent is not None:
            yield parent 
            parent = parent.parent
        
    
    def nlinstr(self):
        if isinstance(self, NLInstruction): return self
        for par in self.parentspath():
            if isinstance(par, NLInstruction):
                return par
    
    
    @property
    def outdbs(self):
        if not self.infchain: 
            return self.indbs
        return self.infchain[-1].outdbs
    
    
    def copy(self, pred=None):
        return PRACInferenceNode(pracinfer=self.pracinfer, parent=self.parent, pred=pred)
    
        
    @property
    def laststep(self):
        return self.infchain[-1]
        
    
    def next_module(self):
        '''
        Determines which module is to be executed next in the PRAC pipeline.
        :return:    the next module to be executed according to the search
                    algorithm as a string
        '''
        previous_module = self.previous_module
#         out(previous_module)
#         if isinstance(self, FrameNode):
#             out(self.frame)
        if previous_module is None:
            return 'nl_parsing'
        if previous_module == 'nl_parsing':
            return 'ac_recognition'
        elif previous_module == 'ac_recognition':
            return 'prop_extraction'
        elif previous_module == 'prop_extraction':
            return 'senses_and_roles'
        elif previous_module == 'senses_and_roles':
            return 'coref_resolution'
        elif previous_module == 'coref_resolution':
            if self.frame.missingroles():
                return 'role_look_up'
            elif hasattr(self.pracinfer.prac.actioncores[self.frame.actioncore], 'plan'): 
                return 'plan_generation'
            else:
                return 'achieved_by'
        elif previous_module == 'role_look_up':
            if hasattr(self.pracinfer.prac.actioncores[self.frame.actioncore], 'plan'):
                return 'plan_generation'
            else: return 'achieved_by'
        elif previous_module == 'achieved_by':
            return 'roles_transformation'
        elif previous_module == 'roles_transformation':
            if hasattr(self.pracinfer.prac.actioncores[self.frame.actioncore], 'plan'):
                return 'plan_generation'
            else:
                return 'achieved_by'
        elif previous_module == 'plan_generation':
            return None

        
class NLInstruction(PRACInferenceNode):
    '''Node in the PRAC inference tree that represents an unprocessed
    natural-language instruction.'''
    def __init__(self, pracinfer, instr, pred=None, prevmod=None):
        PRACInferenceNode.__init__(self, pracinfer=pracinfer, parent=None, pred=pred, indbs=None, prevmod=prevmod)
        self.instr = instr
    
    
    def __str__(self):
        return '"%s"' % self.instr
        

class FrameNode(PRACInferenceNode):
    '''Node representing a Frame.'''
    
    def __init__(self, pracinfer, frame, parent=None, pred=None, indbs=None, prevmod=None):
        PRACInferenceNode.__init__(self, pracinfer=pracinfer, parent=parent, pred=pred, indbs=indbs, prevmod=prevmod)
        self.frame = frame
        
    def __str__(self):
        return str(self.frame)


    def repstr(self):
        return self.frame.repstr()


class PRACInference(object):
    '''
    Represents an inference chain in PRAC
    '''
    def __init__(self, prac, instr):
        '''
        PRAC inference initialization.
        :param prac:     reference to the PRAC instance.
        :param instr:    (str/iterable) list of natural-language sentences subject to
                         inference.
        '''
        self._logger = logs.getlogger(self.__class__.__name__, level=logs.DEBUG)
        self.prac = prac
        prac.deinit_modules()
        self.watch = StopWatch()
        if type(instr) in {list, tuple}:
            instr_ = instr
        elif isinstance(instr, basestring):
            instr_ = [instr]
        self.fringe = []
        pred = None
        for i in instr_:
            self.fringe.append(NLInstruction(self, i, pred=pred))
            pred = self.fringe[-1]
        self.root = list(self.fringe)
        self.lastnode = None
    
    
    def run(self, stopat=None):
        if type(stopat) not in (tuple, list):
            stopat = [stopat]
        while self.fringe:
            modname = self.next_module()
            if modname in stopat: break
            self.runstep()
        return self

    
    def next_module(self):
        if not self.fringe:
            return None
        return self.fringe[0].next_module()
    
    
    def runstep(self):
        if not self.fringe: return
        node = self.fringe.pop(0)
        modname = node.next_module()
        if modname:
            self._logger.debug('running %s' % modname)
            module = self.prac.module(modname)
            nodes = list(module(node))
            node.previous_module = modname
            self.fringe.extend(nodes)
        self.lastnode = node
#         if type(node) == FrameNode:
#             out('indbs:', list(node.indbs))
#             out('outdbs:', list(node.outdbs))
        return node
        

    def steps(self):
        q = list(self.root)
        while q:
            n = q.pop(0)
            if isinstance(n, FrameNode) and not n.children:
                yield n
            q = n.children + q

    def write(self):
        q = list(self.root)
        while q:
            n = q.pop(0)
            print ' ' * len(list(n.parentspath())), n
            q = n.children + q



    def buildframes(self, db, sidx, sentence):
        for _, actioncore in db.actioncores():
            roles = defaultdict(list)
            for role, word in db.rolesw(actioncore):
                sense = db.sense(word)
                props = db.properties(word)
                obj = Object(self.prac, id_=word, type_=sense, props=props, syntax=self.buildword(db, word))
                roles[role].append(obj)
            frames = splitd(roles)    
            for frame in frames:
                yield Frame(self.prac, sidx, sentence, syntax=list(db.syntax()), words=self.buildwords(db), actioncore=actioncore, actionroles=frame)
    
    
    def buildword(self, db, word):
        tokens = word.split('-')
        w = '-'.join(tokens[:-1])
        idx = int(tokens[-1])
        pos = set(db.postag(word)).pop()
        sense = db.sense(word)
        nltkpos = db.prac.wordnet.nltkpos(pos)
        lemma = db.prac.wordnet.lemmatize(w, nltkpos) if nltkpos is not None else None
        return Word(self.prac, word, w, idx, sense, pos, lemma)
    
                
    def buildwords(self, db):
        for word in db.words():
            yield self.buildword(db, word)
            
        

    

    def finalgraph(self, filename=None):
        finaldb = Database(self.prac.mln)
        for step in self.inference_steps:
            for db in step.output_dbs:
                for atom, truth in db.evidence.iteritems():
                    if truth == 0: continue
                    _, predname, args = self.prac.mln.logic.parseLiteral(atom)
                    if predname in self.prac.roles.union(['has_sense', 'action_core', 'achieved_by']):
                        finaldb << atom
                    #         finaldb.write(sys.stdout, color=True)
        g = Digraph(format='svg', engine='dot')
        g.attr('node', shape='box', style='filled')
        for res in finaldb.query('action_core(?w, ?a) ^ has_sense(?w, ?s)'):
            actioncore = res['?a']
            sense = res['?s']
            predname = 'action_core'
            g.node(actioncore, fillcolor='#bee280')
            g.node(sense)
            g.edge(actioncore, sense, label='is_a')
            roles = self.prac.actioncores[actioncore].roles
            for role in roles:
                for res in db.query('{}(?w, {}) ^ has_sense(?w, ?s)'.format(role, actioncore)):
                    sense = res['?s']
                    g.node(sense)
                    g.edge(actioncore, sense, label=role)
        for res in finaldb.query('achieved_by(?a1, ?a2)'):
            a1 = res['?a1']
            a2 = res['?a2']
            g.node(a1, fillcolor='#bee280')
            g.node(a2, fillcolor='#bee280')
            g.edge(a1, a2, label='achieved_by')
            actioncore = a2
            roles = self.prac.actionroles[actioncore].roles
            for role in roles:
                for res in db.query('{}(?w, {}) ^ has_sense(?w, ?s)'.format(role, actioncore)):
                    sense = res['?s']
                    g.node(sense)
                    g.edge(actioncore, sense, label=role)
        return render_gv(g, filename)


    def is_task_missing_roles(self, db):
        # Assuming there is only one action core
        for q in db.query('action_core(?w,?ac)'):
            actioncore = q['?ac']

            roles_senses_dict = dict(db.roles(actioncore))

            inferred_roles_set = set(roles_senses_dict.keys())

            # Determine missing roles: All_Action_Roles\Inferred_Roles
            actioncore_roles_list = self.prac.actioncores[actioncore].required_roles

            if not actioncore_roles_list:
                actioncore_roles_list = self.prac.actioncores[actioncore].roles
                
            missing_role_set = set(actioncore_roles_list).difference(inferred_roles_set)

            if missing_role_set:
                return True
            return False
        return False
