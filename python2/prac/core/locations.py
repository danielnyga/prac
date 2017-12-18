# 
#
# (C) 2011-2016 by Daniel Nyga (nyga@cs.uni-bremen.de)
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
import appdirs

from _version import APPNAME, APPAUTHOR

code_base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
home = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
# update home to point
if os.path.basename(home).startswith('python'):
    home = os.path.realpath(os.path.join(home, '..'))

datapathroot = appdirs.site_data_dir(APPNAME, APPAUTHOR)
datapathnonroot = appdirs.user_data_dir(APPNAME, APPAUTHOR)
pathoptions = [datapathnonroot, datapathroot]

projectpath = os.path.join(code_base, 'pracmodules')

datapath = home

# update datapath
for p in pathoptions:
    if os.path.exists(p):
        datapath = p
        break

trdparty = os.path.join(datapath, '3rdparty')
etc = os.path.join(datapath, 'etc')
examples = os.path.join(datapath, 'examples')
models = os.path.join(datapath, 'models')

data = os.path.join(datapath, 'data')
nltk_data = os.path.join(datapath, data, 'nltk_data')

