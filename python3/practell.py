'''
Created on Jul 11, 2016

@author: nyga
'''
import argparse
import itertools
import multiprocessing
import os
import traceback

from dnutils import out
from pracmln.utils import multicore

from prac.core.base import PRAC
from prac.pracutils.utils import prac_heading


def main():
    #===========================================================================
    # Parse command line arguments
    #===========================================================================
    usage = 'PRAC Tell'

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--howto', '-H', type=str, help='Title of the howto, e.g. "Make pancakes"')
    parser.add_argument('--steps', '-s', nargs='+', type=str, dest='steps', help='A list of instruction steps in natural language. If set, his option must be the last in the list of options followed by the list of instructions.')
    parser.add_argument('--batch', '-b', dest='batch', default=False, action='store_true', help='Import a list of howtos in batch processing whose filenames are given the respective howto title, e.g. "Make a pancake." The file content must then be given by the single instruction steps, one by line.')
    parser.add_argument('--recursive', '-r', dest='recursive', default=False,  help='Apply the import of instructions recursively to subdirectories.')
    parser.add_argument("--verbose", "-v", dest="verbose", default=1, type=int, action="store", help="Set verbosity level {0..3}. Default is 1.")
    parser.add_argument('--quiet', '-q', dest='quiet', action='store_true', default=False, help='Do not print any status messages.')
    parser.add_argument('--multicore', '-m', dest='multicore', action='store_true', default=False, help='Perform information extraction in multicore modus')
    parser.add_argument('--save', action='store_true', default=False, help='Store the howto in the PRAC database permanently.')

    args = parser.parse_args()

    if args.quiet: args.verbose = 0

    if args.verbose:
        print(prac_heading('Telling PRAC, how to {}'.format(args.howto)))

    # ===========================================================================
    # If the 'steps' flag is set, take all arguments as the list of instructions
    # ===========================================================================
    howtos = []
    if args.steps:
        howtos = [{args.howto: args.steps}]
    elif args.batch:
        for path in args:
            if args.recursive:
                for loc, dirs, files in os.walk(path):
                    for filename in files:
                        with open(os.path.join(loc, filename)) as f:
                            howtos.append({' '.join(filename.split('-')): [_f for _f in (line.strip() for line in f) if _f]})
            else:
                for filename in os.listdir(path):
                    if os.path.isdir(filename): continue
                    with open(os.path.join(path, filename)) as f:
                        howtos.append({' '.join(filename.split('-')): [_f for _f in (line.strip() for line in f) if _f]})
    else:
        for filename in args:
            with open(filename) as f:
                howtos.append({' '.join(filename.split('-')): [_f for _f in (line.strip() for line in f) if _f]})

    # ===========================================================================
    # start the import
    # ===========================================================================
    try:
        cpu_count = multiprocessing.cpu_count() if args.multicore else 1
        pool = multicore.NonDaemonicPool(cpu_count)
        pool.map(multicore.with_tracing(import_howto), list(zip(howtos, itertools.repeat(args.verbose), itertools.repeat(args.save))))
    except KeyboardInterrupt:
        traceback.print_exc()
        pool.terminate()
    else:
        # =======================================================================
        # finished
        # =======================================================================
        if args.verbose:
            print('Done. Imported %d howtos' % len(howtos))
    finally:
        pool.close()
        pool.join()


def import_howto(args):
    try:
        howto_steps, verbose, save = args
        prac = PRAC()
        prac.verbose = verbose
        for howto, steps in list(howto_steps.items()):
            prac.tell(howto=howto, steps=steps, save=save)
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
