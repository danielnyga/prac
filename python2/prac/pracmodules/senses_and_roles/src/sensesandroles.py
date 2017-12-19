# PROBABILISTIC ROBOT ACTION CORES 
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
import os
from collections import defaultdict

from dnutils import logs
from pracmln.mln.base import parse_mln
from pracmln.mln.util import colorize
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png

from prac.core import locations as pracloc
from prac.core.base import PRACModule, PRACDatabase
from prac.core.inference import PRACInferenceStep, FrameNode
from prac.core.wordnet import WordNet
from prac.db.ies.models import Object, Frame
from prac.pracutils.pracgraphviz import render_gv
from prac.pracutils.utils import prac_heading, splitd
from prac.sense_distribution import add_all_wordnet_similarities, get_prob_color


logger = logs.getlogger(__name__, logs.DEBUG)


class SensesAndRoles(PRACModule):
    '''
    PRACModule used identify the roles for the given action core and perform
    a simultaneous word sense disambiguation.
    '''

#     @PRACPIPE
    def __call__(self, node, **params):
        # ======================================================================
        # Initialization
        # ======================================================================
        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print prac_heading('Recognizing {} Roles'.format({True: 'MISSING', False: 'GIVEN'}[params.get('missing', False)]))

        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
        queries = ''
        wnmod = self.prac.module('wn_senses')
        actionroles = defaultdict(list)
        pngs = {}
        for n, olddb in enumerate(dbs):
            db_copy = olddb.copy(mln=self.prac.mln)
            actioncore = node.frame.actioncore
            logger.debug(actioncore)
            if params.get('project', None) is None:
                logger.debug('Loading Project: {}.pracmln'.format(colorize(actioncore, (None, 'cyan', True), True)))
                projectpath = os.path.join(pracloc.pracmodules, self.name, '{}.pracmln'.format(actioncore))
                project = MLNProject.open(projectpath)
            else:
                logger.debug(colorize('Loading Project from params', (None, 'cyan', True), True))
                projectpath = os.path.join(params.get('projectpath', None) or os.path.join(pracloc.pracmodules, self.name), params.get('project').name)
                project = params.get('project')

            queries = project.queryconf.get('queries', '')
            mlntext = project.mlns.get(project.queryconf['mln'], None)
            mln = parse_mln(mlntext,
                            searchpaths=[self.module_path],
                            projectpath=projectpath,
                            logic=project.queryconf.get('logic', 'FuzzyLogic'),
                            grammar=project.queryconf.get('grammar', 'PRACGrammar'))
            known_concepts = mln.domains.get('concept', [])

            # ==============================================================
            # Preprocessing
            # ==============================================================
            # adding senses and similarities. might be obsolete as it has
            # already been performed in ac recognition
            logger.debug('adding senses. concepts={}'.format(known_concepts))
            db = wnmod.get_senses_and_similarities(db_copy, known_concepts)

            # we need senses and similarities as well as original evidence
            tmp_union_db = db.union(db_copy, mln=self.prac.mln)

            # ignore roles of false ac's
            new_tmp_union_db = tmp_union_db.copy(mln=self.prac.mln)
            roles = self.prac.actioncores[actioncore].roles
            for ac in tmp_union_db.domains['actioncore']:
                if ac == actioncore: continue
                for r in roles:
                    for w in new_tmp_union_db.words():
                        new_tmp_union_db << ('{}({},{})'.format(r, w, ac), 0)
                        
            infstep.indbs.append(new_tmp_union_db)
            # ==============================================================
            # Inference
            # ==============================================================

            infer = self.mlnquery(config=project.queryconf,
                                  verbose=self.prac.verbose > 2,
                                  db=new_tmp_union_db, mln=mln)
            resultdb = infer.resultdb

            if self.prac.verbose == 2:
                print
                print prac_heading('INFERENCE RESULTS')
                infer.write()

            # ==============================================================
            # Postprocessing
            # ==============================================================
            # get query roles for given actioncore and add inference results
            # for them to final output db. ignore 0-truth results.
            unified_db = new_tmp_union_db.union(resultdb, mln=self.prac.mln)
#             node.frame.actionroles = defaultdict(list)
            for role, word in unified_db.rolesw(actioncore):
                sense = unified_db.sense(word)
                props = dict(unified_db.properties(word))
                obj = Object(self.prac, id_=word, type_=sense, props=props, syntax=node.pracinfer.buildword(unified_db, word))
                actionroles[role].append(obj)

            # argdoms = kb.query_mln.predicate(role).argdoms
            roles = self.prac.actioncores[actioncore].roles
            new_result = PRACDatabase(self.prac)
            for atom, truth in unified_db.evidence.iteritems():
                if any(r in atom for r in roles):
                    (_, predname, args) = self.prac.mln.logic.parse_literal(atom)
                    if not args[-1] == actioncore:
                        continue
                new_result << (atom, truth)

            for q in unified_db.query('has_sense(?w, ?s)'):
                # TODO Add additional formulas to avoid the using of null values
                if self.prac.verbose > 1:
                    print colorize('  WORD:', (None, 'white', True), True), q['?w']
                    print colorize('  SENSE:', (None, 'white', True), True), q['?s']
                    wnmod.printWordSenses(wnmod.get_possible_meanings_of_word(
                            unified_db, q['?w']), q['?s'])
                    print

            infstep.outdbs.append(new_result)

            pngs['Recognizing {} roles - {}'.format('given', str(n))] = get_cond_prob_png(queries,
                                                                                          infstep.indbs, 
                                                                                          filename=self.name)
            infstep.png = pngs
            
            if 'project' not in locals():
                raise Exception('no actioncore in database: %s' % olddb)
            
            infstep.applied_settings = project.queryconf.config
#         pprint(actionroles)
        newframes = splitd(actionroles)
        pred = None
        for newframe in newframes:
#             pprint(newframe)
            f = Frame(self.prac, node.frame.sidx, node.frame.sentence, syntax=list(olddb.syntax()), 
                      words=node.frame.words, actioncore=node.frame.actioncore, actionroles=newframe)
            logger.debug('created new frame %s' % f)
#             for db in infstep.outdbs:
#                 out(db.syntax())
            pred = FrameNode(node.pracinfer, f, node, pred, indbs=infstep.outdbs, prevmod=self.name)
            yield pred


    def role_distributions(self, step):
        '''
        TODO

        :param step:
        :return:
        '''
        distrs = {}
        for db_ in step.output_dbs:
            for word in db_.domains['word']:
                for q in db_.query('action_core(?w,?ac)'):

                    # ==========================================================
                    # Initializaton
                    # ==========================================================

                    actioncore = q['?ac']
                    projectpath = os.path.join(self.module_path, '{}.pracmln'.format(actioncore))
                    project = MLNProject.open(projectpath)
                    mlntext = project.mlns.get(project.queryconf['mln'], None)
                    mln = parse_mln(mlntext,
                                    searchpaths=[self.module_path],
                                    projectpath=projectpath,
                                    logic=project.queryconf.get('logic', 'FirstOrderLogic'),
                                    grammar=project.queryconf.get('grammar', 'PRACGrammar'))

                    # ==========================================================
                    # Preprocessing
                    # ==========================================================

                    # add inferred concepts to known_concepts to display
                    # them in the graph. Ignore verbs and adjectives,
                    # as they do not have hypernym relations to nouns
                    concepts = self.prac.config.getlist('wordnet', 'concepts')
                    for con in db_.query('has_sense(?w,?s)'):
                        if con['?s'].split('.')[1] in ['a', 's', 'v']:
                            continue
                        concepts.append(con['?s'])
                    wn = WordNet(concepts=concepts)

                    db = db_.copy(mln=mln)
                    for qs in db_.query('!(EXIST ?w (has_sense(?w,?s)))'):
                        db.rmval('sense', qs['?s'])
                    for concept in db_.domains['concept']:
                        if concept not in mln.domains['concept']:
                            db.rmval('concept', concept)
                    for res in db_.query('has_sense({}, ?s)'.format(word)):
                        sense = res['?s']
                        if sense == 'null': continue
                        roles = self.prac.actioncores[actioncore].roles
                        role = None
                        for r in roles:
                            vars = ['?v{}'.format(i) for i in range(len(db_.mln.predicate(r).argdoms) - 1)]
                            br = False
                            for qr in db_.query('{}({},{})'.format(r, ','.join(vars), actioncore)):
                                for v in vars:
                                    if qr[v] == word:
                                        role = r
                                        br = True
                                        break
                                if br: break
                            if br: break
                        if role is None: continue
                        db.retract('has_sense({},{})'.format(word, sense))
                        add_all_wordnet_similarities(db, wn)

                        # ======================================================
                        # Inference
                        # ======================================================

                        infer = self.mlnquery(method='EnumerationAsk',
                                              mln=mln,
                                              db=db,
                                              queries='has_sense',
                                              cw=True,
                                              multicore=True,
                                              verbose=self.prac.verbose > 2)

                        result = infer.resultdb

                        if self.prac.verbose == 2:
                            print
                            print prac_heading('INFERENCE RESULTS')
                            print
                            infer.write()

                        # ======================================================
                        # Graph generation
                        # ======================================================

                        g = wn.to_dot()
                        maxprob = 0.
                        for atom, truth in result.gndatoms():
                            _, predname, args = db.mln.logic.parse_literal(atom)
                            concept = args[1]
                            if predname == 'has_sense' and args[0] == word and concept != 'null':
                                maxprob = max(maxprob, truth)

                        for atom, truth in result.gndatoms():
                            _, predname, args = db.mln.logic.parse_literal(atom)
                            concept = args[1]
                            if predname == 'has_sense' and args[0] == word and concept != 'null':
                                if concept in concepts:
                                    g.node(concept, fillcolor=get_prob_color(truth / maxprob))
                        distrs[role] = render_gv(g)
        return distrs
