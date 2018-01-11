import distutils
import os
from distutils.core import setup

import _version
import pip
pip.main(['install', 'appdirs'])
# from setuptools.command import build_py


__basedir__ = _version.__basedir__
__version__ = _version.__version__


appname = 'prac'
appauthor = 'danielnyga'


def iamroot():
    '''Checks if this process has admin permissions.'''
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def basedir(name):
    return os.path.join(__basedir__, name)


with open(os.path.join(os.path.dirname(__file__), __basedir__, 'requirements.txt'), 'r') as f:
    requirements = [l.strip() for l in f.readlines() if l.strip()]


def datafiles(d):
    data_files = []
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), d)):
        if not files: continue
        root_ = root.replace(os.getcwd() + os.path.sep, '')
        data_files.append((root_, [os.path.join(root_, f) for f in files]))
    return data_files


def datapath():
    '''Returns the path where app data is to be installed.'''
    import appdirs
    if iamroot():
        return appdirs.site_data_dir(appname, appauthor)
    else:
        return appdirs.user_data_dir(appname, appauthor)


class myinstall(distutils.command.install.install):

    def __init__(self, *args, **kwargs):
        distutils.command.install.install.__init__(self, *args, **kwargs)
        self.distribution.get_command_obj('install_data').install_dir = datapath()

setup(
    name='prac',
    packages=['prac',
              'prac._version',
              'prac.core',
              'prac.db', 'prac.db.ies',
              'prac.googlevoice',
              'prac.pracutils', 'prac.pracutils.conv',
              'prac.text2speech',
              'prac.pracmodules',
              'prac.pracmodules.ac_recognition', 'prac.pracmodules.ac_recognition.src', 'prac.pracmodules.ac_recognition.mln',
              'prac.pracmodules.achieved_by', 'prac.pracmodules.achieved_by.src', 'prac.pracmodules.achieved_by.mln',
              'prac.pracmodules.complex_achieved_by', 'prac.pracmodules.complex_achieved_by.src',
              'prac.pracmodules.coref_resolution', 'prac.pracmodules.coref_resolution.src', 'prac.pracmodules.coref_resolution.mln',
              'prac.pracmodules.cs_recognition', 'prac.pracmodules.cs_recognition.src', 'prac.pracmodules.cs_recognition.mln',
              'prac.pracmodules.nl_parsing', 'prac.pracmodules.nl_parsing.src', 'prac.pracmodules.nl_parsing.mln',
              'prac.pracmodules.obj_recognition', 'prac.pracmodules.obj_recognition.src', 'prac.pracmodules.obj_recognition.mln',
              'prac.pracmodules.plan_generation', 'prac.pracmodules.plan_generation.src',
              'prac.pracmodules.prop_extraction', 'prac.pracmodules.prop_extraction.src', 'prac.pracmodules.prop_extraction.mln',
              'prac.pracmodules.role_look_up', 'prac.pracmodules.role_look_up.src',
              'prac.pracmodules.roles_transformation', 'prac.pracmodules.roles_transformation.src',
              'prac.pracmodules.senses_and_roles', 'prac.pracmodules.senses_and_roles.src', 'prac.pracmodules.senses_and_roles.mln',
              'prac.pracmodules.wn_senses', 'prac.pracmodules.wn_senses.src', 'prac.pracmodules.wn_senses.mln', 'prac.pracmodules.wn_senses.bin',
              'prac.pracmodules.wsd', 'prac.pracmodules.wsd.src', 'prac.pracmodules.wsd.mln', 'prac.pracmodules.wsd.bin',
              ],
    py_modules=[
        'practell',
        'pracquery',
        'pracparse',
        'senses'
    ],
    package_dir={
        'prac': basedir('prac'),
        'prac._version': '_version',
        '': __basedir__
    },
    package_data={'': ['*']},
    data_files=datafiles('examples') + datafiles('3rdparty') +
               datafiles('data') + datafiles('etc') + datafiles('models'),
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
            'pracquery=pracquery:main',
            'pracparse=pracparse:main',
            'practell=practell:main',
            'pracsenses=senses:main',
            'pracxfold=pracxfold:main',
        ],
    },
    cmdclass={'install': myinstall}
)
