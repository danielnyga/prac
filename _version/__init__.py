"""
_version
Version information for PRAC.
"""
import sys

__all__ = [
    'VERSION_MAJOR',
    'VERSION_MINOR',
    'VERSION_PATCH',
    'VERSION_STRING_FULL',
    'VERSION_STRING_SHORT',
    'APPNAME',
    'APPAUTHOR',
    '__version__',
    '__basedir__'
]

APPNAME = 'prac'
APPAUTHOR = 'danielnyga'

VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0

VERSION_STRING_FULL = '%s.%s.%s' % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
VERSION_STRING_SHORT = '%s.%s' % (VERSION_MAJOR, VERSION_MINOR)

__version__ = VERSION_STRING_FULL

if sys.version_info[0] == 2:
    __basedir__ = 'python2'
elif sys.version_info[0] == 3:
    __basedir__ = 'python3'
else:
    raise Exception('Unsupported Python version: %s' % sys.version_info[0])
