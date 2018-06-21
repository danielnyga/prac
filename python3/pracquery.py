# (C) 2015 by Mareike Picklum (mareikep@cs.uni-bremen.de)
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
import argparse
import json
import os

import sys
from pprint import pprint, pformat

from dnutils import logs

from prac.core.base import PRAC
from prac.core.inference import PRACInference
from prac.db.ies.models import Worldmodel, Object, toplan
from prac.gui import PRACQueryGUI, DEFAULT_CONFIG
from prac.pracutils.utils import prac_heading
from pracmln.mln.util import headline
from pracmln.utils.project import PRACMLNConfig


logger = logs.getlogger(__name__)

try:
    from pymongo import MongoClient
except ImportError:
    logger.warning('MongoDB modules cannot be used.')


def are_requirements_set_to_load_module(module_name):
    if module_name == 'role_look_up' or module_name == 'complex_achieved_by':
        if 'pymongo' in sys.modules:
            client = MongoClient()
            try:
                database_name_list = client.database_names()

                if 'prac' in database_name_list:
                    database = client.prac
                    collections = database.collection_names()

                    if module_name == 'role_look_up':
                        if 'howtos' in collections:
                            return True
                        else:
                            print('"Role look up" module needs a "Frames" collection.')
                            return False
                    elif module_name == 'complex_achieved_by':
                        if 'howtos' in collections:
                            return True
                        else:
                            print('"Complex achieved by module" needs a "Instructions" collection.')
                            return False

                else:
                    print('No PRAC database is stored at local MongoDB server instance.')
                    return False

            except:
                print('No local MongoDB server instance is running.')
                return False
            #IsCollection available
        else:
            return False

    return True


def main():
    logger.level = logs.DEBUG

    usage = 'PRAC Query Tool'

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("instructions", help="The instructions.", nargs='+')
    parser.add_argument("-i", "--interactive", dest="interactive", default=False, action='store_true', help="Starts PRAC inference with an interactive GUI tool.")
    parser.add_argument("-v", "--verbose", dest="verbose", default=1, type=int, action="store", help="Set verbosity level {0..3}. Default is 1.")
    parser.add_argument("-s", "--sim", default=1, type=float, help="Threshold for the similarity value for plan adaptation")
    parser.add_argument('-w', '--world', default=None, type=str, help='Path to the world-model file')

    args = parser.parse_args()
    opts_ = vars(args)

    sentences = args.instructions
    prac = PRAC()
    prac.verbose = args.verbose

    conf = PRACMLNConfig(DEFAULT_CONFIG)

    if args.interactive:  # use the GUI
        from tkinter import Tk
        root = Tk()
        # in case we have natural-language parameters, parse them
        infer = PRACInference(prac, sentences)
        if len(sentences) > 0:
            # module = prac.module('nl_parsing')
            # prac.run(infer, module)
            n = infer.runstep()

            # print parsing result
            for odb in n.outdbs:
                odb.write()

            # print input sentence
            print(n.nlinstr())

            # Started control structure handling
            '''
            cs_recognition = prac.module('cs_recognition')
            prac.run(inference, cs_recognition)
            
            
            dbs = inference.inference_steps[-1].output_dbs
            dbs_ = []
            
            for db in dbs:
                dbs_.extend(parser.extract_multiple_action_cores(db)) 
            inference.inference_steps[-1].output_dbs = dbs_
            '''
            app = PRACQueryGUI(root, infer.prac, n, conf, directory=args[0] if args else None)
            root.mainloop()
        exit(0)
    # regular PRAC pipeline

    # load the world model file if any is given
    if args.world is not None:
        with open(args.world, 'r') as f:
            wm = Worldmodel.fromjson(prac, json.load(f))
        logger.info('loaded world model from %s:' % os.path.abspath(args.world))
        logger.debug(pformat(wm.tojson()))
    else:
        wm = None
    infer = PRACInference(prac, sentences, worldmodel=wm, similarity=args.sim)
    infer.run()
    groundedplan = None
    if wm is not None:
        gnd = prac.module('grounding')
        groundedplan = gnd(infer, wm)
        if prac.verbose:
            json.dumps(toplan([n.frame for n in groundedplan], 'json'))

    print(headline('inference results'))
    print('instructions:')
    for i in infer.root:
        print(i)
    print(prac_heading('intermediate plans', color='blue'))
    for step in infer.steps():
        if hasattr(step, 'plan'):
            print(step.plan)
    print(prac_heading('grounded plans', color='blue'))
    if groundedplan is not None:
        for step in groundedplan:
            if hasattr(step, 'plan'):
                print(step.plan)
    exit(0)


if __name__ == '__main__':
    main()
