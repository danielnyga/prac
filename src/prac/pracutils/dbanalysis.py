#!/usr/bin/python
'''
Author: Jeremy M. Stober
Program: MDS.PY
Description: Multidimensional Scaling
'''

import pylab
from dnutils import logs
from matplotlib.pyplot import text
from nltk.corpus import wordnet as wn
from numpy import *
from numpy.linalg import *
from pracmln import Database
from pracmln.mln.util import mergedom

from prac.core.base import PRAC


logger = logs.getlogger(__name__, logs.INFO)


def doMDS(d, dimensions = 2):
    '''
    Multidimensional Scaling - Given a matrix of interpoint distances,
    find a set of low dimensional points that have similar interpoint
    distances.
    '''

    (n,n) = d.shape
    E = (-0.5 * d**2)

    # Use mat to get column and row means to act as column and row means.
    Er = mat(mean(E,1))
    Es = mat(mean(E,0))

    # From Principles of Multivariate Analysis: A User's Perspective (page 107).
    F = array(E - transpose(Er) - Es + mean(E))

    [U, S, V] = svd(F)

    Y = U * sqrt(S)

    return Y[:, 0:dimensions], S

def norm(vec):
    return sqrt(sum(vec**2))

def square_points(size):
    nsensors = size ** 2
    return array([(i / size, i % size) for i in range(nsensors)])

def test():

    points = square_points(10)
    print(points)

    distance = zeros((100,100))
    for (i, pointi) in enumerate(points):
        for (j, pointj) in enumerate(points):
            distance[i,j] = norm(pointi - pointj)
    print(distance)
    Y, eigs = doMDS(distance)

    pylab.figure(1)
    pylab.plot(Y[:,0],Y[:,1],'.')

    pylab.figure(2)
    pylab.plot(points[:,0], points[:,1], '.')

    pylab.show()


def show_clusters_of_concepts(*dbs):
    '''
    Takes a sequence of databases and performs a multi-dimensional scaling on
    the synsets given by the merged set of 'concept' domains in them.
    '''
    domains = mergedom(*[d.domains for d in dbs])
    concepts = domains.get('concept', None)
    if concepts is None:
        logger.error('Domain "concepts" not found in databases.')
        return
    if 'null' in concepts: # remove the null concept
        del concepts[concepts.index('null')]
    synsets = [wn.synset(x) for x in concepts]  # @UndefinedVariable
    distance = zeros((len(synsets),len(synsets)))
    for (i, pointi) in enumerate(synsets):
        for (j, pointj) in enumerate(synsets):
            sys.stdout.write('{:f} / {:f}      \r'.format(i, len(synsets)))
            sim = synsets[i].path_similarity(synsets[j])
            if sim is None: sim = 0
            distance[i,j] = 1. - sim
    Y, eig = doMDS(distance, dimensions=2)
    pylab.figure(1)
    for i, s in enumerate(synsets):
        text(Y[i,0],Y[i,1], s.name, fontsize=8)
    pylab.plot(Y[:,0],Y[:,1],'.')
    pylab.show()
    
if __name__ == '__main__':
    prac = PRAC()
    dbs = list(Database.load(prac.mln, os.path.join('/', 'home', 'nyga', 'work', 'nl_corpora', 'wikihow', 'Slicing.db')))
    domains = mergedom(*[d.domains for d in dbs])
    concepts = domains.get('concept', None)
