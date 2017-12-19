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

from dnutils import logs
from pracmln.mln.util import colorize

from prac.core.base import PRACModule
from prac.core.errors import ActionKnowledgeError
from prac.core.inference import PRACInferenceStep
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)


class PlanGenerator(PRACModule):
    '''
    PRACModule used to generate a parameterized plan from information inferred
    by previous modules.
    '''

    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================
        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
        infstep.indbs = [db.copy() for db in dbs]
        infstep.outdbs = [db.copy() for db in dbs]
        
        logger.debug('Running {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Generating CRAM Plan(s)'))

        if not hasattr(self.prac.actioncores[node.frame.actioncore], 'plan'):
            raise ActionKnowledgeError('I don\'t know how to %s' % node.frame.sentence)
            yield
        ac = self.prac.actioncores[node.frame.actioncore]
        # fill dictionary with all inferred roles...
        acdict = dict([(k, v.type) for k, v in list(node.frame.actionroles.items())])

        # ..and their properties
        acdict.update(dict([('{}_props'.format(k), ' '.join(['({} {})'.format(pkey, pval) for pkey, pval in list(v.props.tojson().items())])) for k, v in list(node.frame.actionroles.items())]))

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
