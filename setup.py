import os
import subprocess

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

DATA = {'name':'mathclass',
      'description':'mathclass',
      'long_description':README,
      'classifiers':[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
        'author':'Steven Arcangeli',
        'author_email':'steven@highlig.ht',
        'url':'http://highlig.ht',
        'keywords':'web wsgi bfg pylons pyramid',
        'packages':find_packages(),
        'include_package_data':True,
        'zip_safe':False,
        'test_suite':'nose.collector',
        'install_requires':[
            'pyramid',
            'SQLAlchemy',
            'transaction',
            'pyramid_tm',
            'pyramid_jinja2',
            'pyramid_debugtoolbar',
            'pyramid_beaker',
            'pycrypto',
            'zope.sqlalchemy',
            'colander',
            'velruse',
        ],
        'tests_require':[
            'coverage',
        ],
        'setup_requires':[
            'nose>=1.0',
        ],
        'entry_points':"""\
      [paste.app_factory]
      main = mathclass:main
      """,
        }

DIRNAME = os.path.dirname(__file__)
PACKAGE = os.path.join(DIRNAME, DATA['name'])
VERSION_MODULE = '__version__'
VERSION_MODULE_PATH = os.path.join(PACKAGE, VERSION_MODULE + ".py")

def _git_describe():
    """Describe the current revision"""
    try:
        out = subprocess.check_output(['git', 'describe', '--tags',
            '--dirty', '--match=[0-9]*'])
        return out.strip()
    except subprocess.CalledProcessError as e:
        print "Error parsing git revision!"
        print e.output
        raise

def get_version():
    """Calculate the version, which is the git revision"""
    if os.path.isdir(os.path.join(DIRNAME, '.git')):
        version = _git_describe()
        # Make sure we write the version number to the file so it gets
        # distributed with the package
        with open(VERSION_MODULE_PATH, 'w') as version_file:
            version_file.write('"""This file is auto-generated during the '
                'package-building process"""\n')
            version_file.write("__version__ = '" + version + "'")
        return version
    else:
        # If we already have a version file, use the version there
        with open(VERSION_MODULE_PATH, 'r') as version_file:
            version_line = version_file.readlines()[1]
            version = version_line.split("'")[1]
            return version

DATA['version'] = get_version()

if __name__ == "__main__":
    setup(**DATA)
