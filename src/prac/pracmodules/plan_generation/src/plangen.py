# 
#
# (C) 2011-2015 by Daniel Nyga (nyga@cs.uni-bremen.de)
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
from collections import namedtuple

from dnutils import logs, first, out
from scipy.stats import stats

from pracmln.mln.util import colorize

from prac.core.base import PRACModule
from prac.core.errors import ActionKnowledgeError
from prac.core.inference import PRACInferenceStep, AlternativeNode
from prac.pracutils.utils import prac_heading


logger = logs.getlogger('/prac/module/plan_generation', logs.DEBUG)


def normalized(dist):
    '''Returns a modification of ``seq`` in which all elements sum to 1, but keep their proportions.'''
    d_ = dist
    if isinstance(dist, list):
        dist = {i: p for i, p in enumerate(dist)}
    Z = sum(dist.values())
    if not Z:
        raise ValueError('Not a proper distribution: %s' % d_)
    if isinstance(d_, dict):
        return {e: dist[e]/Z for e in dist}
    else:
        return [dist[e]/Z for e in range(len(d_))]


def pdfres(dist):
    '''Computes the residual probability density function for a given discrete distribution.

    The residual probability p_r of an element with probabilty p is proportional to (1-p)

    Accepts ``dist`` to be either a ``list`` holding the probability values or ``dict`` assigning elements
    probabilities.'''
    if len(dist) < 2:
        raise ValueError('Must have at least two possible values to form a proper distribution. Got %s' % dist)
    d_ = dist
    if isinstance(dist, list):
        dist = {i: p for i, p in enumerate(dist)}
    dist = normalized({e: 1-p for e, p in dist.items()})
    if isinstance(d_, dict):
        return {e: dist[e] for e in dist.keys()}
    else:
        return [dist[e] for e in range(len(d_))]


class PlanGenerator(PRACModule):
    '''
    PRACModule used to generate a parameterized plan from information inferred
    by previous modules.
    '''

    def __call__(self, node, **params):
        return self.makeplan(node)

    def makeplan(self, node, **params):
        # ======================================================================
        # Initialization
        # ======================================================================
        # dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
        # infstep.indbs = [db.copy() for db in dbs]
        # infstep.outdbs = [db.copy() for db in dbs]
        
        logger.debug('Running {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Generating CRAM Plan(s)'))

        if not hasattr(self.prac.actioncores[node.frame.actioncore], 'plan'):
            raise ActionKnowledgeError('I don\'t know how to %s' % node.frame)
        ac = self.prac.actioncores[node.frame.actioncore]
        # fill dictionary with all inferred roles...
        acdict = dict([(k, v.type) for k, v in node.frame.actionroles.items()])

        # ..and their properties
        acdict.update(dict([('{}_props'.format(k), ' '.join(['({} {})'.format(pkey, pval) for pkey, pval in v.props.tojson().items()])) for k, v in node.frame.actionroles.items()]))

        # update dictionary with missing roles and roles properties
        for role in ac.roles:
            if acdict.get(role) is None:
                acdict[role] = 'Unknown'
                acdict['{}_props'.format(role)] = ''

        node.plan = ac.parameterize_plan(**acdict)

        if self.prac.verbose:
            print()
            print(prac_heading('PLAN GENERATION RESULTS'))
            print(colorize('actioncore:', (None, 'white', True), True), colorize(ac.name, (None, 'cyan', True), True))
            print(colorize('assignments:', (None, 'white', True), True))
            for x in acdict:
                print('\t{}: {}'.format(colorize(x, (None, 'white', True), True), colorize(acdict[x], (None, 'cyan', True), True)))
        return node


class PlanEval:

    def __init__(self, steps, unknown, missing, known):
        self.steps = steps
        self.unknown = unknown
        self.missing = missing
        self.known = known
        self.likelihood = None

    def __str__(self):
        return 'steps: %s, unknown: %s, missing: %s, known: %s, likelihood: %s' % (self.steps, self.unknown, self.missing, self.known, self.likelihood)


class PlanOptimizer(PlanGenerator):

    def __call__(self, node, **params):
        self.worldmodel = params.get('worldmodel')
        self.do_select = params.get('do_select', True)
        return [self.makeplan(n) for n in self.leaves(first(self.optimize(node)))]

    def leaves(self, node):
        if not node.children:
            yield node
        else:
            for child in node.children:
                for leaf in self.leaves(child):
                    yield leaf

    def optimize(self, node):
        if not node.children:
            if self.worldmodel is not None:
                known = set([obj.type for _, obj in node.frame.actionrole_objects.items() if self.worldmodel.contains(obj.type)])
                unknown = set([obj.type for _, obj in node.frame.actionrole_objects.items() if self.worldmodel.contains(obj.type) is None and obj.type is not None])
                missing = set([obj.type for _, obj in node.frame.actionrole_objects.items() if self.worldmodel.contains(obj.type) is False and obj.type is not None])
            else:
                unknown, missing = set(), set()
                known = set([obj.type for _, obj in node.frame.actionrole_objects.items()])
            # out(unknown)
            # out(node.frame.actionrole_objects)
            unknown = set([c for c in unknown if 'abstraction.n.06' not in self.prac.wordnet.hypernyms_names(c) and '.v.' not in c])
            node.eval = PlanEval(1, unknown, missing, known)
            return [node]
        if isinstance(node, AlternativeNode):
            evals = []
            for i, plan in enumerate(node.alternatives):
                plansteps = [s for step in plan for s in self.optimize(step)]
                # out([n.eval.unknown for n in plansteps])
                e = PlanEval(sum([n.eval.steps for n in plansteps]),
                             set([u for n in plansteps for u in n.eval.unknown]),
                             set([m for n in plansteps for m in n.eval.missing]),
                             set([m for n in plansteps for m in n.eval.known]))
                evals.append(e)
            dist = []
            for e in evals if self.worldmodel is not None else []:
                allobjects = e.missing.union(e.known).union(e.unknown)
                logger.debug('known:', [first(self.worldmodel.getsimilars(o, node.pracinfer.similarity)) for o in e.known],
                             'unknown:', [first(self.worldmodel.getsimilars(o, node.pracinfer.similarity)) for o in e.unknown],
                             'missing:', [first(self.worldmodel.getsimilars(o, node.pracinfer.similarity)) for o in e.missing])
                similars = [first(self.worldmodel.getsimilars(o, node.pracinfer.similarity), lambda o2: node.pracinfer.prac.wordnet.wup_similarity(o, o2.type), 0) for o in e.known.union(e.unknown)]
                logger.debug(similars)
                enum = [sum(similars)] + [first(self.worldmodel.getsimilars(o, node.pracinfer.similarity), lambda o2: node.pracinfer.prac.wordnet.wup_similarity(o, o2.type), 0) for o in e.missing]
                if any([s == 0 for s in enum]):
                    enum = 0
                else:
                    enum = stats.hmean(enum)
                denom = len(allobjects)
                dist.append(enum / denom)
            if not sum(dist):
                raise ActionKnowledgeError('I did not find a plan that is executable in the given environment.')
            dist = normalized(dist)
            node.evals = evals
            logger.info('duistribution over availble plans:', dist)
            for e, l in zip(node.evals, dist):
                e.likelihood = l
            return [node] if not self.do_select else node.alternatives[max(range(len(dist)), key=lambda i: dist[i])]
        else:
            newchildren = []
            for child in node.children:
                children = self.optimize(child)
                newchildren.extend(children)
            node.children = newchildren
            node.eval = PlanEval(sum([n.eval.steps for n in node.children if not isinstance(n, AlternativeNode)]),
                                 set([u for n in node.children if not isinstance(n, AlternativeNode) for u in n.eval.unknown]),
                                 set([m for n in node.children if not isinstance(n, AlternativeNode) for m in n.eval.missing]),
                                 set([m for n in node.children if not isinstance(n, AlternativeNode) for m in n.eval.known]))
        return [node]
