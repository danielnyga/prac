# PROBABILISTIC ROBOT ACTION CORES - LEARNING
#
# (C) 2012 by Daniel Nyga (nyga@cs.uni-bremen.de)
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

from dnutils import logs

from core.base import PRAC
from core.learning import PRACLearning


logger = logs.getlogger(__name__, logs.INFO)

    def parse_list(option, opt, value, parser):
        setattr(parser.values, option.dest, value.split(','))


def main():
    usage = 'Usage: praclearn [--core <actioncore1>[,<actioncore2>[,...]]] [--module <module1>[,<module2>[,...]]]'

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--mt', action='callback', type='string', callback=parse_list, dest='microtheories')
    parser.add_argument('--module', action='callback', type='string', callback=parse_list, dest='modules')
    parser.add_argument('--dbs', action='callback', type='string', callback=parse_list, dest='training_dbs')
    parser.add_argument('--mln', type='string', nargs=2, dest='mln', default=None)
    parser.add_argument('--onthefly', dest='onthefly', default=False, action='store_true', help="Generates MLN on the fly. No learning")

    args = parser.parse_args()
    opts_ = vars(args)

    prac = PRAC()
    praclearn = PRACLearning(prac)
    praclearn.microtheories = args.microtheories
    praclearn.modules = args.modules

    if praclearn.modules is None:
        praclearn.modules = ['prop_extraction']
    if args.training_dbs is not None:
        dbnames = args.training_dbs
        praclearn.training_dbs = dbnames
    if args.mln is not None:
        praclearn.otherParams['mln'] = args.mln[0]
        praclearn.otherParams['logic'] = args.mln[1]
        praclearn.otherParams['onthefly'] = args.onthefly

    for m in praclearn.modules:
        module = prac.module(m)
        module.train(praclearn)


if __name__ == '__main__':
    main()
