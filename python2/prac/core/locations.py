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

from prac._version import APPNAME, APPAUTHOR

root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
code_base = root
user_data = appdirs.user_data_dir(APPNAME, APPAUTHOR)

if os.path.basename(root).startswith('python'):
    root = os.path.realpath(os.path.join(root, '..'))
    app_data = root
else:
    app_data = appdirs.site_data_dir(APPNAME, APPAUTHOR)
    if not os.path.exists(app_data):
        app_data = user_data


trdparty = os.path.join(app_data, '3rdparty')
data = os.path.join(app_data, 'data')
nltk_data = os.path.join(data, 'nltk_data')
etc = os.path.join(app_data, 'etc')
examples = os.path.join(app_data, 'examples')
models = os.path.join(app_data, 'models')
pracmodules = os.path.join(code_base, 'prac', 'pracmodules')
