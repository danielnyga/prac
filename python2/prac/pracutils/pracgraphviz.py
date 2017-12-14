# 
#
# (C) 2011-2015 by Daniel Nyga (nyga@cs.uni-bremen.de)
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
import errno
import subprocess
import xml.etree.ElementTree as ET
from subprocess import PIPE
from tempfile import NamedTemporaryFile
from xml.etree.ElementTree import ElementTree

from dnutils import logs
from graphviz._compat import text_type


logger = logs.getlogger(__name__)


def render_gv(graph, filename=None, directory='/tmp'):
    '''
    A modification of the original graphviz rendering, which 
    Save the source to file and render with the Graphviz engine.
    :param graph:   an instance of a graphviz graph.
    :return:        the rendered content.
    '''
    
    rendered = ''
    try:
        with NamedTemporaryFile(suffix='dot', delete=False) as tmpfile:
            tmpfile.write(text_type(graph.source))
        cmd = [graph._engine, '-T{}'.format(graph._format), tmpfile.name]
        p = subprocess.Popen(' '.join(cmd), shell=True, stderr=PIPE, stdout=PIPE)
        while True:
            l = p.stdout.readline()
            if not l: break
            rendered += l
        p.wait()
        try:
            os.remove(tmpfile.name)
        except OSError:
            logger.warning('could not remove temporary file {}'.format(tmpfile.name))
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise RuntimeError('failed to execute {}, '
                'make sure the Graphviz executables '
                'are on your systems\' path'.format(cmd))
        else:
            raise e

    # scale generated svg to 100%
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    rootSVG = ET.fromstring(rendered)
    rootSVG.set('width', '100%')
    rootSVG.set('height', '100%')

    # create xml tree and write to file
    if filename is not None:
        tree = ElementTree(rootSVG)
        tree.write(os.path.join(directory, filename), encoding='UTF-8', method="xml")

    return ET.tostring(rootSVG, encoding='UTF-8')
