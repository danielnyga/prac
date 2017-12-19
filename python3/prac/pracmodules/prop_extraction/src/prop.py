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
import traceback

from dnutils import logs
from pracmln.mln import NoConstraintsError
from pracmln.mln.base import parse_mln, MLN
from pracmln.utils.project import MLNProject
from pracmln.utils.visualization import get_cond_prob_png

from prac.core import locations as pracloc
from prac.core.base import PRACModule
from prac.core.inference import PRACInferenceStep
from prac.pracutils.utils import prac_heading


logger = logs.getlogger(__name__, logs.DEBUG)


class PropExtraction(PRACModule):
    '''
    PRACModule used extract properties of objects referenced in the NL
    instruction and perform simultaneous word sense disambiguation for these
    properties and objects.
    '''

    def initialize(self):
        self.mln = MLN.load(os.path.join(self.module_path, 'mln', 'predicates.mln'))


    def __call__(self, node, **params):

        # ======================================================================
        # Initialization
        # ======================================================================

        logger.debug('inference on {}'.format(self.name))

        if self.prac.verbose > 0:
            print(prac_heading('Property Extraction'))

        if params.get('project', None) is None:
            # load default project
            projectpath = os.path.join(pracloc.pracmodules, self.name, self.defproject)
            project = MLNProject.open(projectpath)
        else:
            # load project from params
            projectpath = os.path.join(params.get('projectpath', None) or os.path.join(pracloc.pracmodules, self.name), params.get('project').name)
            project = params.get('project')

        
        dbs = node.outdbs
        infstep = PRACInferenceStep(node, self)
        

        mlntext = project.mlns.get(project.queryconf['mln'], None)
        mln = parse_mln(mlntext, searchpaths=[self.module_path], projectpath=projectpath,
                        logic=project.queryconf.get('logic', 'FuzzyLogic'),
                        grammar=project.queryconf.get('grammar', 'PRACGrammar'))
        wnmod = self.prac.module('wn_senses')

        pngs = {}
        for i, db in enumerate(dbs):
            # ==================================================================
            # Preprocessing
            # ==================================================================
            db_ = wnmod.add_sims(db, mln)
            infstep.indbs.append(db_)
            try:
                # ==============================================================
                # Inference
                # ==============================================================

                infer = self.mlnquery(config=project.queryconf,
                                      verbose=self.prac.verbose > 2,
                                      db=db_, mln=mln)
                result_db = infer.resultdb

                if self.prac.verbose == 2:
                    print()
                    print(prac_heading('INFERENCE RESULTS'))
                    print()
                    infer.write()

                # ==============================================================
                # Postprocessing
                # ==============================================================
                unified_db = db.copy(self.prac.mln)
                props = [p for p in project.queryconf.get('queries', '').split(',') if p != 'has_sense']
                for p in props:
                    for q in result_db.query('{}(?w1,?w2) ^ has_sense(?w2,?s2)'.format(p)):
                        unified_db << '{}({},{})'.format(p, q['?w1'], q['?w2'])
                        unified_db << 'has_sense({},{})'.format(q['?w2'], q['?s2'])

                infstep.outdbs.append(unified_db)
            except NoConstraintsError:
                logger.debug('No properties found. Passing db...')
                infstep.outdbs.append(db.copy())
            except Exception:
                logger.error('Something went wrong')
                traceback.print_exc()

            pngs['PropExtraction - ' + str(i)] = get_cond_prob_png(project.queryconf.get('queries', ''), infstep.indbs, filename=self.name)
            infstep.png = pngs

        infstep.applied_settings = project.queryconf.config
        return [node]
