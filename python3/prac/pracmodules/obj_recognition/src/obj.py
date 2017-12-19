# PROBABILISTIC ROBOT ACTION CORES 
#
# (C) 2014 by Mareike Picklum (mareikep@cs.uni-bremen.de)
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
from pracmln import MLN, Database
from pracmln.mln.base import parse_mln
from pracmln.mln.methods import LearningMethods
from pracmln.utils.project import MLNProject

from prac.core import locations as pracloc
from prac.core.base import PRACModule, PRACPIPE
from prac.core.inference import PRACInferenceStep
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)
possibleProps = ['color', 'size', 'shape', 'hypernym', 'hasa']  # , 'dimension', 'consistency', 'material']


class NLObjectRecognition(PRACModule):
    '''
    PRACModule used to infer an objects' identity given its attributes.
    '''

    @PRACPIPE
    def __call__(self, pracinference, **params):
        logger.info('Running {}'.format(self.name))

        print(prac_heading('Recognizing Objects'))

        # load default project
        projectpath = os.path.join(pracloc.pracmodules, self.name, self.defproject)
        project = MLNProject.open(projectpath)

        inf_step = PRACInferenceStep(pracinference, self)
        dbs = pracinference.inference_steps[-1].output_dbs

        mlntext = project.mlns.get(project.queryconf['mln'], None)
        mln = parse_mln(mlntext,
                        searchpaths=[self.module_path],
                        projectpath=projectpath,
                        logic=project.queryconf.get('logic', 'FuzzyLogic'),
                        grammar=project.queryconf.get('grammar',
                                                      'PRACGrammar'))

        wordnet_module = self.prac.module('wn_senses')

        # adding evidence properties to new query db
        for db in dbs:
            # find properties and add word similarities
            logger.error(db.domains)
            logger.error(mln.domains)
            output_db = wordnet_module.add_similarities(db, mln)
            output_db.write()

            # infer and update output dbs
            infer = self.mlnquery(config=project.queryconf,
                                  db=output_db, mln=mln)
            result_db = infer.resultdb

            inf_step.outdbs.append(result_db)

        return inf_step


    @PRACPIPE
    def train(self, praclearning):

        print(prac_heading('Training knowledgebase'))

        mlnName = praclearning.otherParams.get('mln', None)
        mlnLogic = praclearning.otherParams.get('logic', None)
        objName = praclearning.otherParams.get('concept', None)
        onTheFly = praclearning.otherParams.get('onthefly', False)

        mln = MLN(mlnfile=os.path.abspath(mlnName), logic=mlnLogic,
                  grammar='PRACGrammar')

        pracTrainingDBS = praclearning.training_dbs
        trainingDBS = []

        if len(pracTrainingDBS) >= 1 and type(
                pracTrainingDBS[0]) is str:  # db from file
            logger.info('Learning from db files...')
            inputdbs = Database.load(mln, dbfile=pracTrainingDBS,
                                     ignore_unknown_preds=True)
            trainingDBS += inputdbs
        elif len(pracTrainingDBS) > 1:
            logger.info('Learning from db files (xfold)...')
            trainingDBS = pracTrainingDBS
        else:  # db from inference result
            logger.info('Learning from inference result...')
            inputdbs = pracTrainingDBS
            for db in inputdbs:
                db << 'object(cluster, {})'.format(objName)
                trainingDBS.append(db)

        outputfile = '{}_trained.mln'.format(mlnName.split('.')[0])

        # learning mln
        trainedMLN = mln.learnWeights(trainingDBS, LearningMethods.DCLL,
                                      evidencePreds=possibleProps, partSize=1,
                                      gaussianPriorSigma=10, useMultiCPU=0,
                                      optimizer='cg', learningRate=0.9)

        print(prac_heading('Learnt Formulas'))

        trainedMLN.printFormulas()
        trainedMLN.write(file(outputfile, "w"))

        return trainedMLN
