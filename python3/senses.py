'''
Created on Dec 4, 2012

@author: nyga, picklum
'''
import argparse

import nltk
from dnutils import logs
from nltk.corpus import wordnet as wn

from prac.core import locations as praclocations


nltk.data.path = [praclocations.nltk_data]

logger = logs.getlogger(__name__)


def main():
    usage = '''PRAC Senses
    Example usage:
    "pracsenses -a shark -t n"
    or
    "pracsenses shark.n.01"'''

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('words', type=str, nargs='+', help='the word to find the wordnet sense of')
    parser.add_argument('-t', '--tag', dest='tag', type=str, help='the part-of-speech tag the word has', required=False)
    parser.add_argument("-a", "--all", dest="all", default=False, action='store_true', help="whether all senses should be retrieved or not.")
    parser.add_argument('--wupsim', action='store_true', default=False, help='compute the WUP similairty of two synsets')
    args = parser.parse_args()

    if args.all and (args.tag is None or args.words is None):
        parser.error("option -a requires a word and a part-of-speech tag!")
    if args.wupsim and len(args.words) != 2:
        parser.error("option --wupsim requires two synset ids.")

    if args.all:
        for word in args.words:
            synsets = wn.synsets(word, args.tag)
            for s in synsets:
                print(s.name() + ": " + s.definition() + ' (' + ';'.join(s.examples()) + ')')
            print
    elif args.wupsim:
        w1, w2 = args.words
        s1, s2 = wn.synset(w1), wn.synset(w2)
        print('%s ~ %s: %s' % (s1.name(), s2.name(), s1.wup_similarity(s2)))
    else:
        for word in args.words:
            synset = wn.synset(word)
            concepts = set()
            for path in synset.hypernym_paths():
                concepts.update([x.name for x in path])
            for c in concepts:
                logger.info('is_a({},{})'.format(args.word, c))


if __name__ == '__main__':
    main()
