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

from dnutils import logs, out

import prac
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import FrameNode
from prac.db.ies.models import constants, Howto
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)


class ComplexAchievedBy(PRACModule):
    '''
    PRACModule used to perform action core refinement with a mongo database
    lookup.
    '''
    def closest_howto(self, frame):
        '''
        Determines the howto which describes how to perform the complex task.
        
        :param db: A PRAC database which represents the complex instruction.
        :return: A list of databases which each represents a step how to perform the complex instruction.
        '''
        actioncore = frame.actioncore
        howtodb = self.prac.mongodb.prac.howtos 
        # ==================================================================
        # Mongo Lookup
        # ==================================================================
        logger.debug('querying the PRAC database for "%s" howtos...' % actioncore)
        query = {constants.JSON_HOWTO_ACTIONCORE: str(actioncore)}
        docs = howtodb.find(query)
        howtos = [(h, frame.sim(h)) for h in [Howto.fromjson(self.prac, d) for d in docs]]
        howtos = [h for h in howtos if h[1] >= 0.5]
        howtos.sort(key=lambda h: h[0].specifity(), reverse=1)
        howtos.sort(key=lambda h: h[1], reverse=1)
        if self.prac.verbose > 1:
            print('found %d matching howtos:' % len(howtos))
            for howto in howtos:
                print(howto[1], ':', howto[0])
        if howtos:
            howto = howtos[0][0]
            return howto
            
#     @PRACPIPE
    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================
        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Processing complex Action Core refinement'))
        frame = node.frame
        pngs = {}
        howto = self.closest_howto(node.frame)
        if howto is None: return 
        print(howto.shortstr())
        subst = {}
        for role, obj in list(frame.actionroles.items()):
            obj_ = howto.actionroles.get(role)
            if obj_ is not None and obj_.type != obj.type: subst[obj_.type] = obj
        for step in howto.steps:
            for role, obj in list(step.actionroles.items()):
                if obj.type in subst: 
                    step.actionroles[role] = subst[obj.type] 
        pred = None
        for step in howto.steps:
            newnode = FrameNode(node.pracinfer, 
                                step, 
                                node, 
                                pred, 
                                indbs=[PRACDatabase(self.prac, evidence={a: 1 for a in step.todb()})])
            newnode.previous_module = 'coref_resolution'
            pred = step
            yield newnode
        return
