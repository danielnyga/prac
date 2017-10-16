# Markov Logic Networks -- WCSP conversion
#
# (C) 2012 by Daniel Nyga (nyga@cs.tum.edu)
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

import copy
from collections import Iterable

class VarSet(object):
    '''
        Represents a set of positive and negative (binary) random variables
    '''
    
    def __init__(self, posVars=None, negVars=None):
        '''
            posVars and negVars being sets
        '''
        if posVars is None:
            posVars = frozenset()
        else:
            posVars = frozenset(posVars)
        if negVars is None:
            negVars = frozenset()
        else:
            negVars = frozenset(negVars)
        self.__vars = (posVars, negVars)
    
    def isDisjoint(self, other):
        return len(self.pos().intersection(other.pos())) == 0 and len(self.neg().intersection(other.pos())) == 0
    
    def pos(self):
        return self.__vars[0]
    
    def neg(self):
        return self.__vars[1]

    def remove(self, other):
        self.__vars = (self.pos() - other.pos(), self.neg() - other.neg())
        
    def isEmpty(self):
        return len(self.pos()) == 0
    
    def union(self, varset):
        return (self.pos().union(varset.pos()), self.neg().union(varset.neg()))
    
    def __hash__(self):
        return self.__vars.__hash__()
    
    def __eq__(self, other):
        return self.pos() == other.pos() and self.neg() == other.neg()
    
    def __len__(self):
        return len(self.pos()) + len(self.neg())
    
    def __str__(self):
        pos = list(self.pos())
        neg = list(self.neg())
        retStr = ';'.join(map(lambda x: str(x), sorted(pos)))
        if len(self.neg()) > 0:
            retStr += ';$'
        return retStr + ';$'.join(map(lambda x: str(x), sorted(neg)))

class Node(object):
    '''
    Represents a node in a graph
    '''
    
    def __init__(self, node_id, data=None):
        self.id = node_id
        self.data = data
        self.children = set()
        self.parents = set()
        
    def addChild(self, child):
        '''
        Adds a child to the node.
        '''
        self.children.add(child)
        child.parents.add(self)
        
    def addChildren(self, children):
        for c in children:
            self.addChild(c)
        
    def addParent(self, parent):
        '''
        Adds a parent to the node.
        '''
        self.parents.add(parent)
        parent.children.add(self)
        
    def addParents(self, parents):
        for p in parents:
            self.addParent(p)
            
    def removeChild(self, child):
        child.parents.remove(self)
        self.children.remove(child)
    
    def siblings(self, excludeMyself=True):
        '''
        Returns all siblings (children of parents) of this node, excluding the node itself (or not).
        '''
        sibl = set()
        for p in self.parents:
            sibl.update(p.children)
        if self in sibl and excludeMyself is True:
            sibl.remove(self)
        return sibl

    def stepParents(self):
        '''
        Returns the set of all stepparents (i.e. the set of all parents of all siblings
        that are not parents of this node.
        '''
        stepParents = set()
        for s in self.siblings():
            stepParents.update(s.parents)
        return stepParents.difference(self.parents)
    
    def stepChildren(self):
        stepChildren = set()
        cParents = set()
        for c in self.children:
            cParents.update(c.parents.difference([self]))
            for cp in cParents:
                stepChildren.update(cp.children.difference(self.children))
        return stepChildren
    
    def __str__(self):
        return '{}'.format(str(self.id))
    
    def __eq__(self, other):
        return self.id == other.id

    
    
class DAG(object):
    '''
    Represents a (rooted) directed acyclic graph (DAG)
    '''
    
    def __init__(self, root):
        self.root = root
    
    def traverse(self, algo='DFS', direction='down', root=None):
        '''
        Iterates over the graph nodes according to the given strategy. 
        Currently, depth-first search (DFS) and breadth first search 
        (BFS) are supported. Caution: Since children are sets, this 
        is nondeterministic! If an id is given (!=None), then the algorithm
        stops at the first node, the id field of which is equal to id.
        '''
        if root is None:
            root = self.root
        queue = [root]
        processed = set()
        processed.add(root)
        while len(queue) > 0:
            n = queue.pop()
            yield n
            if algo == 'BFS':
                queue = self.bfsEnqueue(n, queue, processed, direction)
            elif algo == 'DFS':
                queue = self.dfsEnqueue(n, queue, processed, direction)
    
    def dfsEnqueue(self, node, queue, processed, direction):
        if direction == 'up':
            nodes = sorted(filter(lambda x: x not in processed, node.parents))
        elif direction == 'down':
            nodes = sorted(filter(lambda x: x not in processed, node.children))
        processed.update(nodes)
        return queue + nodes

    def bfsEnqueue(self, node, queue, processed, direction):
        if direction == 'up':
            nodes = sorted(filter(lambda x: x not in processed, node.parents))
        elif direction == 'down':
            nodes = sorted(filter(lambda x: x not in processed, node.children))
        processed.update(nodes)
        return nodes + queue
    
    def getLeafNodes(self):
        leaves = set()
        for n in self.traverse():
            if len(n.children) == 0:
                leaves.add(n)
        return leaves
    
    def getNextNode(self):
        multipleInheritanceNodes = {}
        transClosureUp = set()
        for n in self.traverse():
            if len(n.parents) > 1:
                multipleInheritanceNodes[n] = self.transitiveClosure(n, 'down')
                multipleInheritanceNodes[n].remove(n)
                transClosure = self.transitiveClosure(n, 'up')
                transClosure.remove(n)
                transClosureUp.update(transClosure)
        for n in multipleInheritanceNodes.keys():
            if not multipleInheritanceNodes[n].isdisjoint(multipleInheritanceNodes.keys()) or not transClosureUp.isdisjoint(n.siblings()):
                continue
            else:
                return n
        return None
            
    
    def ancestorSubgraph(self, nodes):
        '''
        Returns the subgraph from the given node to the root node(s).
        The result is a new instance of a graph and nodes.
        '''
        visited = set()
        newGraph = copy.deepcopy(self)
        if not isinstance(nodes, Iterable):
            nodes = [nodes]
        for n in nodes:
            visited.update(newGraph.transitiveClosure(n, direction='up'))
        for n in newGraph.traverse(algo='DFS', method='graph', direction='down'):
            if n in visited:
                n.children = visited.intersection(n.children)
        return newGraph
    
    def transitiveClosure(self, node, direction='down'):
        '''
        Returns the transitive closure for the given node
        '''
        for start in self.traverse(id = node.id): pass
        closure = set()
        for n in self.traverse(root=start, direction=direction):
            closure.update([n])
        return closure
    
    def findNodeByID(self, node_id):
        for n in self.traverse(id=node_id,algo='DFS'): pass
        return n
    
def processNode(dag, node):
    if len(node.parents) == 0:
        return None
    if len(node.parents) == 1:
        for p in node.parents: pass
        return p
    
    siblings = node.siblings(False)
    # determine all nodes that need to be processed
    nodesToMerge = set()
    for s in siblings:
        nodesToMerge.update(s.parents)
#    nodesToMerge.intersection_update(transHulls[node])
    # determine all transitive closures
    
    sndSiblings = set()
    for n in nodesToMerge:
        sndSiblings.update(n.children.difference(nodesToMerge))
    transHulls = {}
    for s in sndSiblings:
        transHulls[s] = dag.transitiveClosure(s, 'up')
        
    grandParents = set()
    for n in nodesToMerge:
        grandParents.update(n.parents.difference(nodesToMerge))
    grandParentsChildren = {}
    for gp in grandParents:
        grandParentsChildren[gp] = copy.copy(gp.children)
    
    # create the new node by merging all parents
#    parNodeIdUnion = set()
#    for p in parents:
#        parNodeIdUnion.update(p.id.pos())
#    newNode = Node(VarSet(parNodeIdUnion))    
#    node.parents = set()
#    newNode.addChild(node)
#    newNodes = {newNode.id: newNode}
    newNodes = {}
    
    # create corresponding nodes for all siblings
    for sibl in sndSiblings:
        siblParents = transHulls[sibl]
        parentsDiff = nodesToMerge.difference(siblParents)
        parentsIntersect = nodesToMerge.intersection(siblParents)
        posClasses = set()
        for p in parentsIntersect:
            posClasses.update(p.id.pos())
        negClasses = set()
        for p in parentsDiff:
            negClasses.update(p.id.pos())
        negClasses.difference_update(posClasses)
        nodeId = VarSet(map(lambda x: str(x), posClasses), map(lambda x: str(x), negClasses))
        newNode = newNodes.get(nodeId, None)
        if newNode is None:
            newNode = Node(nodeId)
            newNodes[nodeId] = newNode
        newNode.addChild(sibl)
        sibl.parents.difference_update(parentsIntersect)
    
#    for newNode in newNodes.values():
#        positives = newNode.id.pos()
#        for n in nodesToMerge:

    for gp in grandParents:
        for sp in newNodes.values():
            children = set()
            for gpc in grandParentsChildren[gp]:
                if not sp.id.pos().isdisjoint(gpc.id.pos()):
                    children.add(sp)
            gp.addChildren(children)
        gp.children.difference_update(nodesToMerge)
        
    # eliminate transitive edges
    for nn in newNodes.values():
        newParents = set()
        nnParents = nn.parents
        for par in nnParents:
            parents_ = nnParents.difference(set([par]))
            queue = list(parents_)
            notTransitive = True
            while len(queue) > 0:
                q = queue.pop()
                if q == par:
                    notTransitive = False
                    break
                queue.extend(q.parents)
            if notTransitive == True:
                newParents.add(par)
            else:
                par.children.remove(nn)
        nn.parents = newParents
    return newNode

if __name__ == '__main__':
    pass
#    a = Node(VarSet('A'))
#    b = Node(VarSet('B'))
#    c = Node(VarSet('C'))
#    d = Node(VarSet('D'))
#    e = Node(VarSet('E'))
#    f = Node(VarSet('F'))
#    g = Node(VarSet('G'))
##    h = Node(VarSet('H'))
##    t = Node(VarSet('T'))
##    r = Node('R')
##    z = Node('Z')
#    a.addChildren([b,d])
#    b.addChildren([c])
#    d.addChildren([e])
#    f.addParents([c,e])
#    c.addChild(g)
#    a.addChildren([b,c])
#    b.addChildren([f,e])
#    c.addChild(d)
#    d.addChildren([e])
#    s.addParents([d])
#    s.addChildren([e])
#    d.addChild(r)

#    t = Node(VarSet(['T']))
#    f = Node(VarSet(['F']))
#    g = Node(VarSet(['G']))
#    d = Node(VarSet(['D']))
#    s = Node(VarSet(['S']))
#    e = Node(VarSet(['E']))
#    r = Node(VarSet(['R']))
#    a = Node(VarSet(['A']))
#    b = Node(VarSet(['B']))
#    
#    t.addChildren([f, s, g])
#    f.addChildren([a,d])
#    g.addChildren([e,b,r])
#    d.addChildren([b])
#    s.addChildren([a,b])
#    e.addChildren([a])
#
#    dag = DAG(t)
#    
#    nextNode = dag.getNextNode()
#    while nextNode != None:
#        for n in dag.traverse():
#            print n, '(children:',
#            for c in n.children:
#                print c,
#            print ')'
#        print 
#
#        print 'processing', nextNode 
#        processNode(dag, nextNode)
#        nextNode = dag.getNextNode()
#            
#    for n in dag.traverse():
#        print n, '(children:',
#        for c in n.children:
#            print c,
#        print ')'
#    print 