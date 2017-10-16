import os

from setuptools import setup

import _version

__basedir__ = _version.__basedir__
__version__ = _version.__version__


def basedir(name):
    return os.path.join(__basedir__, name)


with open(os.path.join(os.path.dirname(__file__), __basedir__, 'requirements.txt'), 'r') as f:
    requirements = [l.strip() for l in f.readlines() if l.strip()]


def datafiles(d):
    data_files = []
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), d)):
        if not files: continue
        data_files.append((root, [os.path.join(root, f) for f in files]))
    return data_files

def pracmodules():
    data_files = []
    for root, dirs, files in os.walk(basedir('pracmodules')):
        if not files: continue
        data_files.append((os.path.sep.join(root.split(os.path.sep)[1:]), [os.path.join(root, f) for f in files]))
    return data_files

setup(
    name='prac',
    packages=['prac', 'prac._version', 'prac.core', 'prac.db', 'prac.db.ies',
        'prac.googlevoice', 'prac.pracutils', 'prac.pracutils.conv',
        'prac.text2speech',
    ],
    package_dir={
        'prac': basedir('prac'),
        'pracmodules': basedir('pracmodules'),
        'prac._version': '_version',
    },
    package_data={'pracmodules': ['*']},
    data_files=datafiles('examples') + datafiles('3rdparty') +
               datafiles('data') + datafiles('etc') + datafiles('models') + pracmodules(),
    version=__version__,
    description='PRAC - Probabilistic Action Cores - an interpreter for '
                'natural-language instructions which is able to resolve '
                'vagueness and ambiguity in natural language and infer missing '
                'information pieces that are required to render an instruction '
                'executable by a robot.',
    author='Daniel Nyga, Mareike Picklum',
    author_email='nyga@cs.uni-bremen.de, mareikep@cs.uni-bremen.de',
    url='https://actioncores.org',
    download_url='https://github.com/danielnyga/prac/archive/%s.tar.gz' % __version__,
    keywords=['natural-language interpretation', 'prac',
        'probabilistic action cores', 'robot instructions'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence ',
        'Topic :: Text Processing',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
	        'pracquery=prac.pracquery:main',
	        'pracparse=prac.pracparse:main',
	        'practell=prac.practell:main',
	        'pracsenses=prac.senses:main',
	        'pracxfold=prac.pracxfold:main',
        ],
    },
)
