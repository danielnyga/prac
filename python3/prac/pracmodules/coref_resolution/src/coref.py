# PROBABILISTIC ROBOT ACTION CORES
#
# (C) 2016 by Mareike Picklum (mareikep@cs.uni-bremen.de)
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
import traceback
from pprint import pprint

from dnutils import logs
from pracmln.mln import NoConstraintsError, MLNParsingError
from pracmln.mln.base import parse_mln
from pracmln.mln.util import colorize, mergedom
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png

from prac.core import locations as pracloc
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import PRACInferenceStep, FrameNode
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)


class CorefResolution(PRACModule):
    '''
    PRACModule used to perform coreference resolution and simultaneous missing
    role inference.
    '''

    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================

        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Resolving Coreferences'))

        preds = list(node.rdfs(goaltest=lambda n: isinstance(n, FrameNode) and not n.children, all=True))[:2]
        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
        projectpath = os.path.join(pracloc.pracmodules, self.name)
        ac = None
        pngs = {}



#         if not preds: return []
        # ======================================================================
        # Preprocessing
        # ======================================================================

        # merge output dbs from senses_and_roles step, containing
        # roles inferred from multiple sentences.
        if not preds:
            # no coreferencing required - forward dbs and settings
            # from previous module
            infstep.indbs = [db.copy() for db in dbs]
            infstep.outdbs = [db.copy() for db in infstep.indbs]
            logger.debug('%s has no predecessors. Nothing to do here. Passing db...' % node)
            return [node]
    
        # retrieve all words from the dbs to calculate distances.
        # Do not use pracinference.instructions as they are not
        # annotated by the Stanford parser.
        sentences = [db.words() for pred in preds for db in pred.indbs]
        infstep.indbs = [db.copy() for db in dbs]
#         infstep.outdbs = [db.copy() for db in infstep.indbs]
        # query action core to load corresponding project

        actioncore = node.frame.actioncore
        # clear corefdb and unify current db with the two preceding ones
        corefdb = PRACDatabase(self.prac)
        corefdb = corefdb.union(dbs, self.prac.mln)
#         for s in range(max(0, i - 2), i+1):
#             corefdb = corefdb.union(dbs[s], self.prac.mln)
        for pred in preds:
            logger.debug('unifying with %s' % pred)
            for db in pred.indbs:
                corefdb = corefdb.union(db, self.prac.mln)

        # remove all senses from the databases' domain that are not
        # assigned to any word.
        for q in corefdb.query('!(EXIST ?w (has_sense(?w,?sense)))'):
            corefdb.rmval('sense', q['?sense'])
        try:
            # preprocessing: adding distance information for each
            # word in the instructions
#             s = words[max(0, i - 2):i+1]
#             snts = list(enumerate(s))
#             idx = len(snts) - 1  # idx of current sentence
#             for s in snts[:-1]:
#                 idx2 = s[0]
#                 for w in s[1]:
#                     corefdb << 'distance({},DIST{})'.format(w, idx - idx2)
            for sidx, s in enumerate(sentences):
                for w in s:
                    cont = True
                    for q in corefdb.query('distance({}, ?w)'.format(w)):
                        cont = False 
                        break
                    if not cont: continue
                    corefdb << 'distance({},DIST{})'.format(w, sidx)
#                     print 'distance({},DIST{})'.format(w, sidx) 
            
            logger.debug('loading Project: {}'.format(colorize(actioncore, (None, 'cyan', True), True)))
            project = MLNProject.open(os.path.join(projectpath, '{}.pracmln'.format(actioncore)))
            mlntext = project.mlns.get(project.queryconf['mln'], None)
            mln = parse_mln(mlntext, searchpaths=[self.module_path],
                            projectpath=projectpath,
                            logic=project.queryconf.get('logic', 'FuzzyLogic'),
                            grammar=project.queryconf.get('grammar', 'PRACGrammar'))
        except MLNParsingError:
            logger.warning('Could not use MLN in project {} for coreference resolution'.format(colorize(actioncore, (None, 'cyan', True), True)))
            infstep.outdbs = [db.copy(self.prac.mln) for db in dbs]
            infstep.png = node.parent.laststep.png
            infstep.applied_settings = node.parent.laststep.applied_settings
            return [node]
        except Exception:
            infstep.outdbs = [db.copy(self.prac.mln) for db in dbs]
            infstep.png = node.parent.laststep.png
            infstep.applied_settings = node.parent.laststep.applied_settings
            logger.warning('Could not load project "{}". Passing dbs to next module...'.format(ac))
            return [node]

        # adding similarities
        wnmod = self.prac.module('wn_senses')
        newdatabase = wnmod.add_sims(corefdb, mln)

        # update queries depending on missing roles
        acroles = [role for role in self.prac.actioncores[actioncore].roles if role != 'action_verb']
        missingroles = [ar for ar in acroles if len(list(newdatabase.query('{}(?w,{})'.format(ar, actioncore)))) == 0]
        conf = project.queryconf
        conf.update({'queries': ','.join(missingroles)})
        print(colorize('querying for missing roles {}'.format(conf['queries']), (None, 'green', True), True))

        # asserting impossible role-ac combinations, leaving previously
        # inferred roles untouched
        fulldom = mergedom(mln.domains, newdatabase.domains)
        ac_domains = [dom for dom in fulldom if '_ac' in dom]
        acs = list(set([v for a in ac_domains for v in fulldom[a]]))
        acs = [ac_ for ac_ in acs if ac_ != actioncore]

        for ac1 in acs:
            for r in missingroles:
                for w in newdatabase.domains['word']:
                    # words with no sense are asserted false
                    if list(corefdb.query('!(EXIST ?sense (has_sense({},?sense)))'.format(w))):
                        newdatabase << '!{}({},{})'.format(r, w, actioncore)
                    # leave previously inferred information roles
                    # untouched
                    if list(newdatabase.query('{}({},{})'.format(r, w, ac1))):
                        continue
                    else:
                        newdatabase << '!{}({},{})'.format(r, w, ac1)
        try:
            # ==========================================================
            # Inference
            # ==========================================================
            infer = self.mlnquery(config=conf,
                                  verbose=self.prac.verbose > 2,
                                  db=newdatabase, mln=mln)
            if self.prac.verbose == 2:
                print()
                print(prac_heading('INFERENCE RESULTS'))
                infer.write()
            # ==========================================================
            # Postprocessing
            # ==========================================================
            # merge initial db with results
            for db in infstep.indbs:
                resultdb = db.copy()
                for res in list(infer.results.keys()):
                    if infer.results[res] != 1.0:
                        continue
                    resultdb << str(res)
                    _, _, args = self.prac.mln.logic.parse_literal(res)
                    w = args[0]
                    for q in newdatabase.query('has_sense({0},?s) ^ has_pos({0},?pos)'.format(w)):
                        resultdb << 'has_sense({},{})'.format(w, q['?s'])
                        resultdb << 'is_a({0},{0})'.format(q['?s'])
                        resultdb << 'has_pos({},{})'.format(w, q['?pos'])
                resultdb = wnmod.add_sims(resultdb, mln)
                # enhance the frame data
                for mrole in missingroles:
                    for q in resultdb.query('{role}(?w, {actioncore}) ^ has_sense(?w, ?s)'.format(role=mrole, actioncore=actioncore)):
                        for p in preds:
                            if p.frame.object(q['?w']) is not None:
                                node.frame.actionroles[mrole] = p.frame.object(q['?w']) 
                                break
                infstep.outdbs.append(resultdb)
            pprint(node.frame.tojson())
        except NoConstraintsError:
            logger.debug('No coreferences found. Passing db...')
            infstep.outdbs.append(db)
        except Exception:
            logger.error('Something went wrong')
            traceback.print_exc()

        pngs['Coref - ' + str(node)] = get_cond_prob_png(project.queryconf.get('queries', ''), dbs, filename=self.name)
        infstep.png = pngs
        infstep.applied_settings = project.queryconf.config
        return [node]

