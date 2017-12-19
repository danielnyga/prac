# PROBABILISTIC ROBOT ACTION CORES 
#
# (C) 2012 by Daniel Nyga (nyga@cs.tum.edu)
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
import os

import yaml
from dnutils import logs
from pracmln.mln.base import parse_mln
from pracmln.mln.errors import NoConstraintsError
from pracmln.mln.util import colorize
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png

import prac
from prac.core import locations as pracloc
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import PRACInferenceStep
from prac.db.ies.models import Object
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)
rolesTransformationModulePath = os.path.join(prac.locations.pracmodules, 'roles_transformation')
planListFilePath = os.path.join(rolesTransformationModulePath, 'plan_list.yaml')


class RolesTransformation(PRACModule):
    '''
    PRACModule used refine action roles after a preceding action core
    refinement.
    '''

    def initialize(self):
        self.isLastActionCoreAPlan = False


    def getPlanList(self):
        planListFile = open(planListFilePath, 'r')
        yamlData = yaml.load(planListFile)

        return yamlData['planList']


#     @PRACPIPE
    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================

        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print prac_heading('Update roles based on Action Core Refinement')

        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
#         planlist = self.getPlanList()
#         out(node.parent.frame, '->', node.frame)
        pngs = {}
        for i, db_ in enumerate(dbs):
#             db = db_.copy()
#             db = PRACDatabase(self.prac)
            # ==================================================================
            # Preprocessing
            # ==================================================================
            actioncore = node.frame.actioncore
            logger.debug('Action core: {}'.format(actioncore))
            if params.get('project', None) is None:
                logger.debug('Loading Project: {}.pracmln'.format(colorize(actioncore, (None, 'cyan', True), True)))
                projectpath = os.path.join(pracloc.pracmodules, self.name, '{}Transformation.pracmln'.format(actioncore))
                project = MLNProject.open(projectpath)
            else:
                logger.debug(colorize('Loading Project from params', (None, 'cyan', True), True))
                projectpath = os.path.join(params.get('projectpath', None) or os.path.join(pracloc.pracmodules, self.name), params.get('project').name)
                project = params.get('project')
    
            mlntext = project.mlns.get(project.queryconf['mln'], None)
            mln = parse_mln(mlntext, searchpaths=[self.module_path],
                            projectpath=projectpath,
                            logic=project.queryconf.get('logic', 'FirstOrderLogic'),
                            grammar=project.queryconf.get('grammar', 'PRACGrammar'))
            result_db = None
                
            for pdb in node.parent.outdbs:
                db = pdb.copy()
                db = db.union(db_)
                objs = {o.id for o in node.parent.frame.actionroles.values()}
                for w in set(db.domains['word']):
                    if w not in objs:
                        db.rmval('word', w)
                infstep.indbs.append(db)
                ac = node.parent.frame.actioncore
                db << 'achieved_by(%s, %s)' % (ac, actioncore)
                for role, object_ in node.parent.frame.actionroles.iteritems():
                    db << '%s(%s, %s)' % (role, object_.id, ac)
            try:
                # ==========================================================
                # Inference
                # ==========================================================
                infer = self.mlnquery(config=project.queryconf, db=db,
                                      verbose=self.prac.verbose > 2,
                                      mln=mln)
                result_db = infer.resultdb
    
                if self.prac.verbose == 2:
                    print
                    print prac_heading('INFERENCE RESULTS')
                    print
                    infer.write()
            except NoConstraintsError:
                logger.error('no constraints in role transformation: %s -> %s' % (node.parent.frame, node.frame))
                result_db = db
            
            # ==============================================================
            # Postprocessing
            # ==============================================================
            r_db = PRACDatabase(self.prac)
            roles = self.prac.actioncores[actioncore].roles
            for atom, truth in sorted(result_db.evidence.iteritems()):
                if any(r in atom for r in roles):
                    _, predname, args = self.prac.mln.logic.parse_literal(atom)
                    word, ac = args
                    if ac == actioncore:
                        r_db << (atom, truth)
                        if truth:
                            sense = pdb.sense(word)
                            props = pdb.properties(word)
                            obj = Object(self.prac, id_=word, type_=sense, props=props, syntax=node.pracinfer.buildword(pdb, word))
                            node.frame.actionroles[predname] = obj
#             out('->', node.frame)
            unified_db = db.union(r_db, mln=self.prac.mln)
            r_db_ = PRACDatabase(self.prac)
    
            # It will be assumed that there is only one true action_
            # c1ore predicate per database
#             for actionverb, actioncore in unified_db.actioncores(): break
    
            for atom, truth in sorted(unified_db.evidence.iteritems()):
                if 'action_core' in atom: continue
                r_db_ << (atom, truth)
            infstep.outdbs.append(r_db_)
    
            pngs['RolesTransformation - ' + str(i)] = get_cond_prob_png(project.queryconf.get('queries', ''), dbs,
                                                                        filename=self.name)
            infstep.png = pngs
            infstep.applied_settings = project.queryconf.config
        return [node]
