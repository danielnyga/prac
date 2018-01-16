# PROBABILISTIC ROBOT ACTION CORES 
#
# (C) 2012-2013 by Daniel Nyga (nyga@cs.tum.edu)
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

from prac.core.base import PRACModule, PRACPIPE, PRACDatabase
from prac.core.inference import PRACInferenceStep, FrameNode
from prac.pracutils.utils import prac_heading
from pracmln import Database
from pracmln.mln.base import parse_mln
from pracmln.mln.util import colorize
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png



logger = logs.getlogger(__name__, logs.DEBUG)

class ActionCoreIdentification(PRACModule):
    '''
    PRACModule used to identify action cores in natural-language instructions
    '''
#     @PRACPIPE
    def __call__(self, node, **params):
        # ======================================================================
        # Initialization
        # ======================================================================
        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Recognizing Action Cores'))

        if params.get('project', None) is None:
            # load default project
            projectpath = os.path.join(pracloc.pracmodules, self.name, self.defproject)
            ac_project = MLNProject.open(projectpath)
        else:
            logger.info(colorize('Loading Project from params', (None, 'cyan', True), True))
            projectpath = os.path.join(params.get('projectpath', None) or os.path.join(pracloc.pracmodules, self.name), params.get('project').name)
            ac_project = params.get('project')

        dbs = node.outdbs

        mlntext = ac_project.mlns.get(ac_project.queryconf['mln'], None)
        mln = parse_mln(mlntext, searchpaths=[self.module_path], projectpath=projectpath,
                        logic=ac_project.queryconf.get('logic', 'FirstOrderLogic'),
                        grammar=ac_project.queryconf.get('grammar', 'PRACGrammar'))
        known_concepts = mln.domains.get('concept', [])
        infstep = PRACInferenceStep(node, self)
        wnmod = self.prac.module('wn_senses')

        pngs = {}
        nlinstr = node.nlinstr()
        sidx = nlinstr.idx()
        sentence = nlinstr.instr
        
        for db_ in dbs:
            # ==================================================================
            # Preprocessing
            # ==================================================================
            db = wnmod.get_senses_and_similarities(db_, known_concepts)
            tmp_union_db = db.union(db_, mln=self.prac.mln)
            infstep.indbs.append(tmp_union_db)
            
            # ==================================================================
            # Inference
            # ==================================================================
            infer = self.mlnquery(config=ac_project.queryconf,
                                  verbose=self.prac.verbose > 2,
                                  db=tmp_union_db, mln=mln)
            resultdb = infer.resultdb
            if self.prac.verbose == 2:
                print()
                print(prac_heading('INFERENCE RESULTS'))
                infer.write()
            # ==================================================================
            # Postprocessing
            # ==================================================================
            unified_db = resultdb.union(tmp_union_db, mln=self.prac.mln)
            
#             infstep.outdbs
            infstep.outdbs.extend(self.extract_multiple_action_cores(self.prac, unified_db, wnmod, known_concepts))
            
            pngs[unified_db.domains.get('actioncore', [None])[0]] = get_cond_prob_png(ac_project.queryconf.get('queries', ''), dbs, filename=self.name)
        infstep.png = pngs
        infstep.applied_settings = ac_project.queryconf.config
        pred = None    
        for outdb in infstep.outdbs:
#             out('in ac rec:')
#             for w, ac in outdb.actioncores():
#                 out(w, ac)
            for frame in node.pracinfer.buildframes(outdb, sidx, sentence): 
                node_ = FrameNode(node.pracinfer, frame, node, pred, indbs=[outdb], prevmod=self.name)
                pred = node_
                yield node_
                break
            else: 
                logger.error('no actioncore recognized in %s' % node)
                raise Exception('no actioncore recognized in %s' % node)


    def extract_multiple_action_cores(self, prac, db, wordnet_module, known_concepts):
        '''
        TODO

        :param prac:            the PRAC instance
        :param db:              an instance of Database
        :param wordnet_module:  the wordnet PRACModule
        :param known_concepts:  a list of known concepts
        :return:                a list of databases
        '''
        dbs = []
        verb_list = []
        
        for word, _ in db.actioncores():
            verb_list.append(word)

        if len(verb_list) < 2:
            return [db]

        # sort list according to word ID to keep order of actions
        verb_list = sorted(verb_list, key=lambda x: x.split('-')[-1])


        # TODO improve the handling
        # Handle sentence with start with .....
        '''
        if len(verb_list) == 2:
            db.write()
            for word in ['start', 'Start']:
                for _ in db.query('prepc_with({}-1,?p)'.format(word)):
                    return [db]
        '''
        
        for verb in verb_list:
            db_ = PRACDatabase(prac)
            processed_word_set = set()
            remaining_word_set = set()
            remaining_word_set.add(verb)

            while remaining_word_set:
                processed_word = remaining_word_set.pop()
                is_condition = False

                for atom, truth in sorted(db.evidence.items()):
                    
                    _, pred, args = db.mln.logic.parse_literal(atom)
                    
                    if pred == "is_a" or pred == "has_sense":
                        continue
                    if pred == "action_core" and args[0] == processed_word:
                        db_ << (atom,truth)
                    elif len(args) == 1 and args[0] == processed_word:
                        db_ << (atom,truth)
                        is_condition = True
                    elif len(args) > 1:
                        word1 = args[0]
                        word2 = args[1]

                        dependency_word = ""
                        if word1 == processed_word:
                            dependency_word = word2
                        elif word2 == processed_word:
                            dependency_word = word1

                        if dependency_word and (
                                        dependency_word not in verb_list or
                                        pred == "event") and (
                                    dependency_word not in processed_word_set):
                            if pred != 'event' or not is_condition:
                                db_ << (atom,truth)
                            if pred != 'has_pos' and pred != 'event':
                                remaining_word_set.add(dependency_word)
                processed_word_set.add(processed_word)
            
        
            #Add valid senses and is_a concepts
            temp_sense_db = wordnet_module.get_senses_and_similarities(db_, known_concepts)
            valid_sense_list = temp_sense_db.domain('sense')
            valid_word_list = temp_sense_db.domain('word')
            
            for atom, truth in sorted(db.evidence.items()):
                _, pred, args = db.mln.logic.parse_literal(atom)
                if pred != "is_a" and pred != "has_sense": continue
                
                if pred == "is_a" and args[0] in valid_sense_list:
                    db_ << (atom,truth)
                elif pred == "has_sense" and args[0] in valid_word_list and args[1] in valid_sense_list:
                    db_ << (atom,truth)
            dbs.append(db_)
            
        return dbs


    @PRACPIPE
    def train(self, praclearning):
        prac = praclearning.prac
        # get all the relevant training databases
        db_files = prac.training_dbs()
        nl_module = prac.module('nl_parsing')
        syntactic_preds = nl_module.mln.predicates
        logger.debug(db_files)
        dbs = [x for x in [Database(self.mln, dbfile=name, ignore_unknown_preds=True) for name in db_files] if type(x) is Database]
        logger.debug(dbs)
        new_dbs = []
        training_dbs = []
        known_concepts = []
        logger.debug(self.mln.domains)
        for db in dbs:
            if not 'actioncore' in db.domains: continue
            if not 'concept' in db.domains: continue
            for c in db.domains['concept']:
                known_concepts.append(c)
            new_dbs.append(db)
        wordnet = prac.wordnet
        for db in new_dbs:
            new_db = db.duplicate()
            for sol in db.query('has_sense(?w, ?s) ^ is_a(?s, ?c)'):
                word = sol['?w']
                sense = sol['?s']
                concept = sol['?c']
                synset = wordnet.synset(concept)
                for known_concept in known_concepts:
                    known_synset = wordnet.synset(known_concept)
                    if known_synset is None or synset is None: sim = 0
                    else: sim = wordnet.wup_similarity(synset, known_synset)
                    new_db << ('is_a(%s,%s)' % (sense, known_concept), sim)
            training_dbs.append(new_db)

        logger.info('Starting training with %d databases'.format(len(training_dbs)))
