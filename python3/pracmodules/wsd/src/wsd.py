from dnutils import logs

from prac.core.base import PRACModule, PRACPIPE
from prac.core.inference import PRACInferenceStep
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.INFO)


class PRACWSD(PRACModule):
    '''
    PRACModule used to perform word-sense disambiguation
    '''

    @PRACPIPE
    def __call__(self,pracinference, **params):

        print(prac_heading('Word Sense Disambiguation'))

        if params.get('kb', None) is None:
            # load the default arguments
            dbs = pracinference.inference_steps[-1].output_dbs
            kb = self.load_prac_kb('default')
            kb.dbs = dbs
        else:
            kb = params['kb']
        if not hasattr(kb, 'dbs'):
            kb.dbs = pracinference.inference_steps[-1].output_dbs
        mln = kb.query_mln
        mln.write()
        logic = kb.query_params['logic']
        fol =  False
        if(logic == 'FirstOrderLogic'):
            fol = True
        known_concepts = mln.domains.get('concept', [])
        inf_step = PRACInferenceStep(pracinference, self)
        wordnet_module = self.prac.module('wn_senses')

        for db in kb.dbs:
            db = wordnet_module.get_senses_and_similarities(db, known_concepts)
            result_db = list(kb.infer(db))
            inf_step.output_dbs.extend(result_db)
            print()
            for r_db in result_db:
                print(prac_heading('Inferred most probable word senses'))
                for q in r_db.query('has_sense(?w, ?s)'):
                    if q['?s'] == 'null': continue
                    print('{}:'.format(q['?w']))
                    wordnet_module.printWordSenses(wordnet_module.get_possible_meanings_of_word(r_db, q['?w']), q['?s'])
                    print()

        return inf_step
