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
from collections import defaultdict

from dnutils import logs
from nltk.corpus.reader.wordnet import Synset

from prac.core.base import PRACModule, PRACPIPE, DB_TRANSFORM
from prac.core.inference import PRACInferenceStep
from prac.core.wordnet import WordNet, POS_MAP

from pracmln import MLN, Database
from pracmln.mln.util import colorize, mergedom


logger = logs.getlogger(__name__, logs.INFO)


class WNSenses(PRACModule):
    '''
    Extracts possible word senses from WordNet given the part of speech
    of a word. Depends on the 'syntax' feature extractor.
    '''

    def initialize(self):
        self.mln = MLN(mlnfile=os.path.join(self.module_path, 'mln', 'predicates.mln'),
                       logic='FuzzyLogic',
                       grammar='PRACGrammar')
        self.wordnetKBs = {}


    @DB_TRANSFORM
    def get_senses_and_similarities(self, db, concepts):
        '''
        Returns a new database with possible senses and the pairwise
        semantic similarities asserted. Assumes the part-of-speeches
        'has_pos' and the syntactic predicates from the parsing module
        to be given. Also asserts all negative evidences which cannot
        be true given the word senses from WordNet (eg, 'pancake' cannot
        have any meaning of milk).

        Example: 'Flip the pancake.'

        has_pos(pancake-3,NN) ---> 0.0  has_sense(pancake-3, Flip-1-sense-1)
                                   ....
                                   1.0  is_a(pancake-1-sense, pancake.n.01)
                                   0.6  is_a(pancake-1-sense, milk.n.01)
                                   ....

        All the reference concepts which are supposed to be considered
        need to be given by means of the 'concept' argument.
        NB: The existing databases are _not_ modified. Instead, copies
        of them are created and returned.

        '''
        wordnet = self.prac.wordnet
        word2senses = defaultdict(list)
        db_ = db.copy(self.prac.mln)

        for res in db.query('has_pos(?word,?pos)'):
            word_const = res['?word']
            pos = POS_MAP.get(res['?pos'], None)
            # if no possible sense can be determined by WordNet, skip word
            # for now. False senses will be asserted later
            if pos is None:
                continue
            # extract everything except the number (e.g. compound words like
            # heart-shaped from heart-shaped-4)
            word = '-'.join(word_const.split('-')[:-1])
            for i, synset in enumerate(wordnet.synsets(word, pos)):
                sense_id = synset.name()
                word2senses[word_const].append(sense_id)
                for concept in concepts:
                    sim = wordnet.similarity(synset, concept, 'path')
                    db_ << ('is_a({},{})'.format(sense_id, concept), sim)

        for word in word2senses:
            for word2, senses in list(word2senses.items()):
                if word2 == word:
                    continue
                else:
                    for s in senses:
                        if not s in word2senses[word]:
                            db_ << '!has_sense({},{})'.format(word, s)

        # assert false for combinations of possible senses and
        # words without POS tag
        for res in db.query('has_pos(?word,?pos)'):
            word_const = res['?word']
            pos = POS_MAP.get(res['?pos'], None)
            # if no possible sense can be determined by WordNet, assert false
            # for all possible senses
            if pos is None or not wordnet.synsets('-'.join(word_const.split('-')[:-1]),pos):
                for s in db_.domain('sense'):
                    db_ << '!has_sense({},{})'.format(word_const, s)
        return db_


    def add_sims(self, db_, mln):
        '''
        Adds for each sense s_db in the database the similarities to each
        concept in the mln c_mln, i.e. the atom 'is_a(s_db,c_mln)'
        Example:

        ``senses_db = [pancake.n.01, spatula.n.01]``
        ``concepts_mln = [milk.n.01, pot.n.01]``

        will be transformed into

        ``1.000  is_a(milk.n.01, pancake.n.01)
          0.300  is_a(milk.n.01, spatula.n.01)
          0.300  is_a(pot.n.01, pancake.n.01)
          1.000  is_a(pot.n.01, spatula.n.01)``
        '''

        db = db_.copy(self.prac.mln)
        mlndomains = mln.domains.get('concept', []) + db_.domains.get('concept', [])
        for s in db_.domains['sense']:
            sense = self.prac.wordnet.synset(s)
            for c in mlndomains:
                syn = self.prac.wordnet.synset(c)
                # this is a workaround! use sense.name and syn.name instead of
                # s and c, once misleading data is removed from mlns and dbs
                # example:
                # self.prac.wordnet.synset('make.v.39').name == 'cook.v.02'!
                db << ('is_a(%s, %s)' % (s, c), self.prac.wordnet.similarity(sense, syn))
        return db


    def add_similarities(self, db, mln):
        '''
        For each cluster add the similarities for each value of each property
        in the db domains to each value of the respective property in the
        mln domains. The degree of truth of the new atom is the similarity
        between the two properties (= wordnet concepts). This enables us to
        use previously unknown concepts.

        only used in module obj_recognition

        Example:
        If the evidence contains

        ``color(c, orange.s.01)'',

        the atoms

        ``0.9 color(c, yellow.s.01)''
        ``0.95 color(c, red.s.01)''

        are added if yellow.s.01 and red.s.01 are in the color domain of the
        mln.

        '''
        db_ = db.copy()
        dbdomains = db.domains
        for cl in dbdomains.pop('cluster'):
            for propkey in dbdomains:
                if propkey not in mln.domains: continue
                for propval in dbdomains[propkey]:
                    for propval2 in mln.domains[propkey]:
                        synset1 = self.prac.wordnet.synset(propval)
                        synset2 = self.prac.wordnet.synset(propval2)
                        sim = self.prac.wordnet.similarity(synset1, synset2,
                                                           'wup')
                        db_ << ('{}({}, {})'.format(propkey, cl, propval2),
                                sim)
        return db_



    def printWordSenses(self, synsets, tick):
        '''
        Prints the list of synsets or synset ids and ticks the one specified
        by the given index.
        tick may be either the index or the sense id itself or the synset
        instance.
        '''
        if type(tick) is str:
            tick = self.prac.wordnet.synset(tick)
        synsets_ = []
        for idx, sense in enumerate(synsets):
            if isinstance(sense, str):
                sense = self.prac.wordnet.synset(sense)
            synsets_.append(sense)
        if isinstance(tick, Synset):
            tick = synsets_.index(tick)
        for idx, sense in enumerate(synsets_):
            print('    [{}] {}: {} ({})'.format('X' if tick == idx else ' ',
                                                colorize(sense.name(), (None, {True: 'yellow', False: 'white'} [tick == idx], True), True),
                                                sense.definition(),
                                                ';'.join(sense.examples())))


    def get_possible_meanings_of_word(self, db, word):
        '''
        Returns a list of synsets for the given word (the constant with index)
        in the given database. Assumes that parts-of-speech are known.
        '''
        for q in db.query('has_sense({}, ?s) ^ has_pos({}, ?pos)'.format(word,
                                                                         word)):
            pos = q['?pos']
            pos = POS_MAP.get(pos, None)
            if pos is None: continue
            # make sure that words like bowl-shaped are left untouched
            # bowl-shaped-5 should become bowl-shaped and not bowl
            word = '-'.join(word.split('-')[:-1])
            return self.prac.wordnet.synsets(word, pos)
        return None


    def get_similarities(self, *dbs):
        '''
        Returns a database containing all possible similarities for the senses
        of the input databases.

        :param dbs: the input databases to be queried
        :return:    a generator yielding an instance of Database
        '''
        wordnet = self.prac.wordnet
        full_domain = mergedom(*[db.domains for db in dbs])
        for db in dbs:
            db_ = Database(self.mln)
            for q in db.query('has_sense(?w, ?s) ^ is_a(?s, ?c)'):
                sense = q['?s']
                concept = q['?c']
                for c in full_domain['concept']:
                    sim = wordnet.similarity(c, concept)
                    db_ << ('is_a({},{})'.format(sense, c), sim)
            yield db_


    def addFuzzyEvidenceToDBs(self, *dbs):
        '''
        Adds to the databases dbs all fuzzy 'is_a' relationships
        for all senses contained in the DB and in the MLN.
        (has side effects on the original one)
        '''
        mln_domains = dbs[0].domains
        domains_full = mergedom(mln_domains, *[db.domains for db in dbs])
        concepts = domains_full['concept']
        wordnet = WordNet()
        for db in dbs:
            for res in db.query('is_a(?sense, ?concept)'):
                sense = res['?sense']
                concept = res['?concept']
                for c in concepts:
                    similarity = wordnet.semilarity(concept, c)
                    logger.info('{} ~ {} = {:.2f}'.format(concept, c, similarity))
                    db << ('is_a({},{})'.format(sense, c), similarity)
        return dbs


    def addPossibleWordSensesToDBs(self, *dbs):
        '''
        Adds to the databases dbs all possible word senses (and fuzzy meanings)
        based on their part of speech.
        '''
        wordnet = WordNet()
        for db in dbs:
            word2senses = defaultdict(list)
            logger.info(db.mln.domains['concept'])
            for res in db.query('has_pos(?word,?pos)'):
                word_const = res['?word']
                pos = POS_MAP.get(res['?pos'], None)
                if pos is None:
                    continue
                word = word_const.split('-')[0]
                for i, synset in enumerate(wordnet.synsets(word, pos)):
                    sense_id = '%s-%.2d' % (word_const, i + 1)
                    word2senses[word_const].append(sense_id)
                    for concept in db.mln.domains['concept']:
                        sim = wordnet.semilarity(synset, concept)
                        db << ('is_a(%s,%s)' % (sense_id, concept), sim)
            for word in word2senses:
                for word2, senses in list(word2senses.items()):
                    if word2 == word:
                        continue
                    else:
                        for s in senses: db << (
                            '!has_sense(%s,%s)' % (word, s))


    @PRACPIPE
    def infer(self, pracinference):
        inf_step = PRACInferenceStep(pracinference, self)
        for db in pracinference.get_inference_steps_of_module(
                'nl_parsing').output_dbs:

            database = Database(self.prac.mln)
            for truth, gndLit in db.iterGroundLiteralStrings():
                database << (gndLit, truth)
                logger.info(gndLit)
            logger.info('Adding all similarities...')
            self.addPossibleWordSensesToDBs(database)
            inf_step.output_dbs.append(database)
        return inf_step


    @PRACPIPE
    def train(self, prac_learning):

        training_dbs = []
        if hasattr(prac_learning,
                   'training_dbs') and prac_learning.training_dbs is not None:
            for dbfile in prac_learning.training_dbs:
                training_dbs.extend(Database(self.mln, dbfile=dbfile, ignore_unknown_preds=True))
        else:
            for dbfile in self.prac.training_dbs():
                db = Database(self.mln, dbfile=dbfile, ignore_unknown_preds=True)
                training_dbs.append(db)
