# PROBABILISTIC ROBOT ACTION CORES 
#
# (C) 2012-2015 by Daniel Nyga (nyga@cs.tum.edu)
# (C) 2015 by Sebastian Koralewski (seba@informatik.uni-bremen.de)
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
import os

from dnutils import logs, out, first, ifnone

import prac
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import FrameNode, AlternativeNode
from prac.db.ies.models import constants, Howto
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)


class ComplexAchievedBy(PRACModule):
    '''
    PRACModule used to perform action core refinement with a mongo database
    lookup.
    '''

    def closest_howtos(self, frame, similarity=None):
        '''
        Determines the howto which describes how to perform the complex task.
        
        :param db: A PRAC database which represents the complex instruction.
        :return: A list of databases which each represents a step how to perform the complex instruction.
        '''
        similarity = ifnone(similarity, .9)
        actioncore = frame.actioncore
        howtodb = self.prac.mongodb.prac.howtos 
        # ==================================================================
        # Mongo Lookup
        # ==================================================================
        logger.debug('querying the PRAC database for "%s" howtos...' % actioncore)
        query = {constants.JSON_HOWTO_ACTIONCORE: str(actioncore)}
        docs = howtodb.find(query)
        howtos = [(h, frame.sim(h)) for h in [Howto.fromjson(self.prac, d) for d in docs]]
        howtos = [h for h in howtos if h[1] >= similarity]
        howtos.sort(key=lambda h: h[0].specifity(), reverse=1)
        howtos.sort(key=lambda h: h[1], reverse=1)
        if self.prac.verbose > 1:
            print 'found %d matching howtos (threshold %s):' % (len(howtos), similarity)
            for howto in howtos:
                print howto[1], ':', howto[0]
        if howtos:
            maxscore = max([score for howto, score in howtos])
            alternatives = [(h, s) for h, s in howtos if s == maxscore]
            return alternatives

    def __call__(self, node, worldmodel=None, **params):
        # ======================================================================
        # Initialization
        # ======================================================================
        logger.debug('inference on {}'.format(self.name))
        if self.prac.verbose > 0:
            print prac_heading('Processing complex Action Core refinement')
        frame = node.frame
        pngs = {}
        howtos = self.closest_howtos(node.frame, node.pracinfer.similarity)
        if not howtos:
            return
        alternatives = []
        for howto, score in howtos:
            subst = {}
            for role, obj in frame.actionroles.iteritems():
                obj_ = howto.actionroles.get(role)
                if obj_ is not None and obj_.type != obj.type: subst[obj_.type] = obj
            substitutions = 0
            for step in howto.steps:
                for role, obj in step.actionroles.iteritems():
                    if obj.type in subst:
                        step.actionroles[role] = subst[obj.type]
                        substitutions += 1
            if not substitutions and score < 1.0:
                if self.prac.verbose > 1:
                    logger.debug('discarding howto {}, since no adaptation is possible'.format(howto))
                continue
            pred = None
            steps = []
            for step in howto.steps:
                newnode = FrameNode(node.pracinfer,
                                    step,
                                    node,
                                    pred,
                                    indbs=[PRACDatabase(self.prac, evidence={a: 1 for a in step.todb()})])
                newnode.previous_module = 'coref_resolution'
                pred = step
                steps.append(newnode)
            alternatives.append(steps)
        if len(alternatives) > 1:
            alternative = AlternativeNode(node.pracinfer, node.frame, parent=node, alternatives=alternatives, indbs=node.indbs)
            for plan in alternatives:
                for step in plan:
                    step.parent.children = [alternative]
                    step.parent = alternative
                    step.previous_module = 'coref_resolution'
            yield alternative
        elif len(alternatives) == 1:
            for c in first(alternatives):
                yield c
        return
