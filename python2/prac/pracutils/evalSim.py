# Classifier Evaluation incorporating similarity
#
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

from subprocess import Popen
from prac.core.wordnet import WordNet
from pracmln.utils.eval import ConfusionMatrix


class ConfusionMatrixSim(ConfusionMatrix):
    '''
    Subclass of ConfusionMatrix incorporating similarities
    between concepts into the precisions calculations
    '''

    def __init__(self):
        super(ConfusionMatrixSim, self).__init__()
        self.wordnet = WordNet()

    def countClassifications(self, classname, sim=False):
        '''
        Returns the true positive, true negative, false positive, false negative
        classification counts (in this order).
        False positives and false negatives consider concept similarity.
        '''
        tp = self.matrix.get(classname,{}).get(classname,0)
        classes = self.matrix.keys()

        fp = 0.
        wn = self.wordnet
        classSyn = wn.synset(classname)
        for c in classes:
            if c != classname:
                if sim:
                    cSyn = wn.synset(c)
                    fp += (self.getMatrixEntry(classname, c) * (1- wn.similarity(classSyn,cSyn)))
                else:
                    fp += self.getMatrixEntry(classname, c)

        fn = 0.
        for c in classes:
            if c != classname:
                if sim:
                    cSyn = wn.synset(c)
                    fn += (self.getMatrixEntry(c, classname) * (1- wn.similarity(classSyn,cSyn)))
                else:
                    fn += self.getMatrixEntry(c, classname)
        
        tn = 0.
        for c in classes:
            if c != classname:
                for c2 in classes:
                    if c2 != classname:
                        tn += self.getMatrixEntry(c, c2)
        if not sim:
            assert sum([tp, tn, fp, fn]) == self.instanceCount
        return tp, tn, fp, fn
        
    def getMetrics(self, classname, sim=False):
        '''
        Returns the classifier evaluation metrices in the following order:
        Accuracy, Precision, Recall, F1-Score.
        '''
        classes = []
        for classification in self.matrix:
            for truth in self.matrix.get(classification,{}):
                try:
                    classes.index(truth)
                except ValueError:
                    classes.append(truth)
        
        classes = sorted(classes)
    
        tp, tn, fp, fn = self.countClassifications(classname, sim)
        acc = None
        if tp + tn + fp + fn > 0:
            acc = (tp + tn) / float(tp + tn + fp + fn)
        
        pre = 0.0
        if tp + fp > 0:
            pre = tp / float(tp + fp)
        
        rec = 0.0
        if tp + fn > 0:
            rec = tp / float(tp + fn)
        
        f1 = 0.0
        if pre + rec > 0:
            f1  = (2.0 * pre * rec) / (pre + rec)
            
        return acc, pre, rec, f1

    def getLatexTable(self, sim=False):
        '''
        Returns LaTex code for the confusion matrix.
        '''
        grid = "|l|"
        for cl in sorted(self.labels):
            grid += "l|"
        endl = '\n'
        result = ''
        result += r'\footnotesize' + endl
        result += r'\begin{tabular}{' + grid + '}' + endl
        
        headerRow = r"Prediction/Ground Truth"
        for cl in sorted(self.labels):
            headerRow += r" & \begin{turn}{90}" + cl.replace('_', r'\_') + r'\end{turn}' 
        
        # count number of actual instances per class label
        examplesPerClass = {}
        for label in self.labels:
            tp, tn, fp, fn = self.countClassifications(label)
            examplesPerClass[label] = sum([tp, fp, fn])
            
        result += r'\hline' + endl
        result += headerRow + r'\\ \hline' + endl
        
        #for each class create row
        for clazz in sorted(self.labels):
            values = []
            #for each row fill colum
            for cl2 in sorted(self.labels):
                counts = self.getMatrixEntry(clazz, cl2)
                if sim:
                    classSyn = self.wordnet.synset(clazz)
                    cl2Syn = self.wordnet.synset(cl2)
                    counts *= self.wordnet.similarity(classSyn, cl2Syn)
                values.append('\cellcolor{{cfmcolor!{0}}}{1}'.format(int(round(counts/examplesPerClass[clazz] * 100)), ('\\textbf{{{:g}}}' if clazz == cl2 else '{:g}').format(float('{:.2f}'.format(counts)))))
            result += clazz.replace('_', r'\_') + ' & ' + ' & '.join(values) + r'\\ \hline' + endl
            
        result += r"\end{tabular}" + endl
        return result

    def printPrecisions(self, sim=False):
        '''
        Prints to the standard out a table of the class-specific error measures accurracy, precision, recall, F score.
        '''
        classes = []
        for classification in self.matrix:
            for truth in self.matrix.get(classification,{}):
                try:
                    classes.index(truth)
                except ValueError:
                    classes.append(truth)
        
        classes = sorted(classes)
        
        s = ''
        precs = {}
        for cf in classes:
            acc,pre,rec,f1 = self.getMetrics(cf, sim)

            print '{}: - Acc={:2f}, Pre={:2f}, Rec={:2f}, F1={:2f}\n'.format(cf, acc, pre, rec, f1)
            precs[cf] = 'Acc={:2f}, Pre={:2f}, Rec={:2f}, F1={:2f}'.format(acc, pre, rec, f1)
        return precs
            

    def precisionsToFile(self, filename, sim=False):
        '''
        Prints to the standard out a table of the class-specific error measures accurracy, precision, recall, F score.
        '''
        precisions = self.printPrecisions(sim=sim)
        f = open(filename, 'w+')
        for prec in precisions:
            f.write('{}: {}\n'.format(prec, precisions[prec]))
        f.write('Total Accuracy: {}\n'.format(self.getTotalAccuracy()))
        f.write('Average Precision: Acc={0[0]}, Pre={0[1]}, Rec={0[2]}, F1={0[3]}\n'.format(self.printAveragePrecision(sim=sim)))

    def printAveragePrecision(self, sim=False):
        classes = []
        for classification in self.matrix:
            for truth in self.matrix.get(classification,{}):
                try:
                    classes.index(truth)
                except ValueError:
                    classes.append(truth)
        
        classes = sorted(classes)
        aAcc = 0.0
        aPre = 0.0
        aRec = 0.0
        aF1 = 0.0
        
        for cf in classes:
            acc,pre,rec,f1 = self.getMetrics(cf, sim)
            aAcc += acc
            aPre += pre
            aRec += rec
            aF1 += f1
            
        print '{}: - Acc={:2f}, Pre={:2f}, Rec={:2f} F1={:2f}\n'.format('Average: ', aAcc/len(classes), aPre/len(classes), aRec/len(classes), aF1/len(classes)) 
        print ""
        return aAcc/len(classes), aPre/len(classes), aRec/len(classes), aF1/len(classes)


    def __str__(self):
        maxNumDigits = max(max(map(lambda x: x.values(), self.matrix.values()), key=max))
        maxNumDigits = len(str(maxNumDigits))
        maxClassLabelLength = max(map(len, self.matrix.keys()))
        padding = 1
        numLabels = len(self.matrix.keys())
        cellwidth = max(maxClassLabelLength, maxNumDigits, 3) + 2 * padding
        # create an horizontal line
        print maxNumDigits
        hline = '|' + '-' * (cellwidth) + '+'
        hline += '+'.join(['-' * (cellwidth)] * numLabels) + '|'
        sep = '|'
        outerHLine = '-' * len(hline)
        
        def createTableRow(args):
            return sep + sep.join(map(lambda a: str(a).rjust(cellwidth-padding) + ' ' * padding, args)) + sep           
        endl = '\n'
        # draw the table
        table = outerHLine + endl
        table += createTableRow(['P\C'] + sorted(self.matrix.keys())) + endl
        table += hline + endl
        for i, clazz in enumerate(sorted(self.labels)):
            classSyn = self.wordnet.synset(clazz)
            table += createTableRow([clazz] + map(lambda x: ('{:g}'.format(self.getMatrixEntry(clazz, x) * self.wordnet.similarity(classSyn, self.wordnet.synset(x)))), sorted(self.labels))) + endl
            if i < len(self.matrix.keys()) - 1:
                table += hline + endl
        table += outerHLine
        return table
        
    def toPDF(self, filename, sim=False):
        '''
        Creates a PDF file of this matrix. Requires 'pdflatex' and 'pdfcrop' installed.
        '''
        texFileName = filename + '.tex'
        texFile = open(texFileName, 'w+')
        texFile.write(r'''
        \documentclass[10pt]{{article}}
        \usepackage{{color}}
        \usepackage{{rotating}}
        \usepackage[table]{{xcolor}}
        \definecolor{{cfmcolor}}{{rgb}}{{0.2,0.4,0.6}}
        \begin{{document}}
        \pagenumbering{{gobble}}
        \resizebox{{\columnwidth}}{{!}}{{{}}}
        \end{{document}}
        '''.format(self.getLatexTable(sim)))
        texFile.close()
        cmd = 'pdflatex -halt-on-error {}'.format(texFileName)
        p = Popen(cmd, shell=True)
        if p.wait() != 0:
            raise Exception('Couldn\'t compile LaTex.')
        else:
            cmd = 'pdfcrop {}.pdf {}.pdf'.format(filename, filename)
            p = Popen(cmd, shell=True)
            if p.wait() != 0:
                raise Exception('Couldn\'t crop pdf')
        

if __name__ == '__main__':
    cm = ConfusionMatrixSim()
    
    for _ in range(10):
        cm.addClassificationResult("lemon.n.01","lemon.n.01")
        cm.addClassificationResult("lemon.n.01","lemon.n.01")
        cm.addClassificationResult("lemon.n.01","lemon.n.01")
        cm.addClassificationResult("orange.n.01","lemon.n.01")
        cm.addClassificationResult("orange.n.01","lemon.n.01")
        cm.addClassificationResult("lemon.n.01","orange.n.01")
        cm.addClassificationResult("orange.n.01","orange.n.01")
        cm.addClassificationResult("orange.n.01","orange.n.01")
    
    cm.printTable()
    cm.printPrecisions()
    print cm.getLatexTable()
    cm.toPDF('tmp')
    cm.toPDF('tmp_sim', sim=True)
