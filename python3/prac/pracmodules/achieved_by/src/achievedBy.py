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

from dnutils import logs

from prac.core import locations as pracloc
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import PRACInferenceStep, FrameNode
from prac.db.ies.models import Frame
from prac.pracutils.utils import prac_heading
from pracmln.mln.base import parse_mln
from pracmln.mln.errors import NoConstraintsError
from pracmln.mln.util import colorize
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png


logger = logs.getlogger(__name__, logs.DEBUG)


class AchievedBy(PRACModule):
    '''
    PRACModule used to perform action core refinement. If there exist no
    robot-executable plan for a given action core, this module will find an
    action by which this action core can be achieved.
    '''

    def extendDBWithAchievedByEvidence(self, db, querymln, actioncore):
        '''
        TODO

        :param db:
        :param querymln:
        :return:
        '''
        # It will be assumed that there is only one true action_core
        # predicate per database
        acdomain = querymln.domains.get("actioncore")
        acdomain.extend(db.domains.get("actioncore"))
        acdomain = set(acdomain)
        db_ = PRACDatabase(self.prac)

        for ac1 in acdomain:
            for ac2 in acdomain:
                if ac1 == actioncore:
                    continue
                db_["achieved_by({},{})".format(ac1, ac2)] = 0

        for atom, truth in sorted(db.evidence.items()):
            db_ << (atom, truth)

        return db_


#     @PRACPIPE
    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================

        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Refining Actioncores'))
        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
#         if node.previous_module == 'achieved_by':
#             raise ActionKnowledgeError('I don\'t know how to %s' % node.frame.sentence)
        # ======================================================================
        # Preprocessing
        # ======================================================================
        for olddb in dbs:
            infstep.indbs.append(olddb.copy())
            #To handle multiple acs in one task, we have to check if the single 
            # dbs contain achieved_bys which representing already plans
            pngs = {}
            actioncore = node.frame.actioncore
            mod = self.prac.module('complex_achieved_by')
            newnodes = list(mod(node))
            n = None
            parentframes = [p.frame for p in node.parentspath() if isinstance(p, FrameNode)]
            if any(n.frame in parentframes for n in newnodes):
                logger.error('aborting reasoning because of infinite loop. (%s)' % node.frame)
                node.children = []
            else:
                for n in newnodes:
                    yield n
            if n is not None: return
            if n is None:
                # This list is used to avoid an infinite loop during the
                # achieved by inference.
                # To avoid this infinite loop, the list contains the pracmlns
                # which were inferenced during the process.
                # Every pracmln should be used only once during the process
                # because the evidence for the inference will always remain
                # the same.
                # So if the pracmln hadnt inferenced a plan in the first time,
                # it will never do it.
    
                # Need to remove possible achieved_by predicates from
                # previous achieved_by inferences
                db_ = PRACDatabase(self.prac)
                for atom, truth in sorted(olddb.evidence.items()):
                    if 'achieved_by' in atom: continue
                    db_ << (atom,truth)
                if params.get('project', None) is None:
                    logger.debug('Loading Project: {}.pracmln'.format(colorize(actioncore, (None, 'cyan', True), True)))
                    projectpath = os.path.join(pracloc.pracmodules, self.name, '{}.pracmln'.format(actioncore))
                    if os.path.exists(projectpath):
                        project = MLNProject.open(projectpath)
                    else:
                        infstep.outdbs.append(olddb)
                        logger.error(actioncore + ".pracmln does not exist.")
                        return
                else:
                    logger.debug(colorize('Loading Project from params', (None, 'cyan', True), True))
                    projectpath = os.path.join(params.get('projectpath', None) or os.path.join(pracloc.pracmodules, self.name), params.get('project').name)
                    project = params.get('project')
                        
    
                mlntext = project.mlns.get(project.queryconf['mln'], None)
                mln = parse_mln(mlntext, searchpaths=[self.module_path],
                                projectpath=projectpath,
                                logic=project.queryconf.get('logic', 'FirstOrderLogic'),
                                grammar=project.queryconf.get('grammar', 'PRACGrammar'))
                known_concepts = mln.domains.get('concept', [])
                wnmod = self.prac.module('wn_senses')
                
                #Merge domains of db and given mln to avoid errors due to role inference and the resulting missing fuzzy perdicates
                known_concepts = list(set(known_concepts).union(set(db_.domains.get('concept', []))))
                db = wnmod.get_senses_and_similarities(db_, known_concepts)
    
                unified_db = db_.union(db)
                dbnew = wnmod.add_sims(unified_db, unified_db)
    
                # Inference achieved_by predicate
                db_ = self.extendDBWithAchievedByEvidence(dbnew, mln, actioncore)
                # ==============================================================
                # Inference
                # ==============================================================
#                 db_.write()
                try:
                    infer = self.mlnquery(config=project.queryconf,
                                          verbose=self.prac.verbose > 2,
                                          db=db_, mln=mln)
                except NoConstraintsError:
                    logger.error('achieved_by inference failed due to NoConstraintsError: %s' % node.frame)
                    return
                result_db = infer.resultdb
    
                if self.prac.verbose == 2:
                    print()
                    print(prac_heading('INFERENCE RESULTS'))
                    infer.write()
                # ==============================================================
                # Postprocessing
                # ==============================================================
                # unified_db = result_db.union(kb.query_mln, db_)
                # only add inferred achieved_by atoms, leave out
                # 0-evidence atoms
                for qa in result_db.query('achieved_by(?ac1,?ac2)'):
                    if qa['?ac2'] == 'Complex': continue
                    unified_db << 'achieved_by({},{})'.format(qa['?ac1'], qa['?ac2'])
                    pngs[qa['?ac2']] = get_cond_prob_png(project.queryconf.get('queries', ''), dbs, filename=self.name)
                    newframe = Frame(self.prac, node.frame.sidx, '', words=[], syntax=[], actioncore=qa['?ac2'], actionroles={})
#                     out('->', newframe)
                    infstep.outdbs.append(unified_db)
                    yield FrameNode(node.pracinfer, newframe, node, pred=None, indbs=[unified_db], prevmod=self.name)
                    return
                infstep.outdbs.append(unified_db)
#             raise ActionKnowledgeError('I don\'t know how to %s' % node.frame.sentence)