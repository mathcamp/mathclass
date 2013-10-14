""" Setup file """
import os

from setuptools import setup, find_packages
from version_helper import get_version


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.txt')).read()

DATA = {'name': 'mathclass',
        'version': get_version('mathclass'),
        'description': 'mathclass',
        'long_description': README,
        'classifiers': [
            "Programming Language :: Python",
            "Framework :: Pyramid",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
        'author': 'Steven Arcangeli',
        'author_email': 'steven@highlig.ht',
        'url': 'http://highlig.ht',
        'keywords': 'web wsgi bfg pylons pyramid',
        'packages': find_packages(),
        'include_package_data': True,
        'zip_safe': False,
        'test_suite': 'nose.collector',
        'install_requires': [
            'pyramid==1.4',
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
        'tests_require': [
            'coverage',
        ],
        'setup_requires': [
            'nose>=1.0',
        ],
        'entry_points': """\
      [paste.app_factory]
      main = mathclass:main
      """,
        }

if __name__ == "__main__":
    setup(**DATA)
