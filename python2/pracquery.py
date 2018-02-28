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

import sys

from dnutils import logs

from prac.core.base import PRAC
from prac.core.inference import PRACInference
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
    parser.add_argument("instruction", help="The instruction.")
    parser.add_argument("-i", "--interactive", dest="interactive", default=False, action='store_true', help="Starts PRAC inference with an interactive GUI tool.")
    parser.add_argument("-v", "--verbose", dest="verbose", default=1, type=int, action="store", help="Set verbosity level {0..3}. Default is 1.")

    args = parser.parse_args()
    opts_ = vars(args)

    sentences = args.instruction
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

            #Started control structure handling
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
    infer = PRACInference(prac, sentences)
    infer.run()

    print(headline('inference results'))
    print('instructions:')
    for i in infer.root:
        print(i)
    frames = []
    for step in infer.steps():
        print(step.frame)
    print(prac_heading('cram plans', color='blue'))
    for step in infer.steps():
        if hasattr(step, 'plan'):
            print(step.plan)
#     infer.write()
    exit(0)


if __name__ == '__main__':
    main()
