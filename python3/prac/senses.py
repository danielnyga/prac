'''
Created on Dec 4, 2012

@author: nyga, picklum
'''
import argparse

import nltk
from dnutils import logs
from nltk.corpus import wordnet as wn

from .core import locations as praclocations


nltk.data.path = [praclocations.nltk_data]

logger = logs.getlogger(__name__)

def main():
    usage = '''PRAC Senses
    Example usage:
    "pracsenses -a shark -t n"
    or
    "pracsenses shark.n.01"'''

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('word', type=str, help='the word to find the wordnet sense of')
    parser.add_argument('-t', '--tag', dest='tag', type=str, help='the part-of-speech tag the word has', required=False)
    parser.add_argument("-a", "--all", dest="all", default=False, action='store_true', help="whether all senses should be retrieved or not.")
    args = parser.parse_args()


    if args.all and (args.tag is None or args.word is None):
        parser.error("option -a requires a word and a part-of-speech tag!")

    opts_ = vars(args)
    logger.error(args)

    if args.all:
        synsets = wn.synsets(args.word, args.tag)
        for s in synsets:
            logger.info(s.name() + ": " + s.definition() + ' (' + ';'.join(s.examples()) + ')')
        print()
    else:
        synset = wn.synset(args.word)
        concepts = set()
        for path in synset.hypernym_paths():
            concepts.update([x.name for x in path])
        for c in concepts:
            logger.info('is_a({},{})'.format(args.word, c))
        print()


if __name__ == '__main__':
    main()
