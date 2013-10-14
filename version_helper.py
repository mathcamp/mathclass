"""
Helper file to generate package version numbers on the fly

Wouldn't it be great if every time you bundled a python package, it was tagged
with a unique version number that reflected the current git ref? It's almost
like that's a feature that should be available without stupid hacks.

But it's not. So here's how the stupid hacks work.

When you run ``python setup.py``, if you are running it from inside of a git
repository this script with generate a unique version number and embed it in an
auto-generated file in your package. By default the file is named
'__version__.py', and you should add it to your ``.gitignore``. Since this is a
python file and it's in your package, it will get bundled up and distributed
with your package. Then during the installation process, this script will
recognize that it is not longer being run from within a git repository and find
the version number from the file it generated earlier.

"""
import os
import re

import subprocess

DEV_BUILD = re.compile('.*-[0-9]+-g[0-9a-f]{7}')


def _git_describe(describe_cmd):
    """ Describe the current revision """
    try:
        out = subprocess.check_output(describe_cmd)
        return out.strip()
    except subprocess.CalledProcessError as e:
        print "Error parsing git revision!"
        print e.output
        raise


def _parse_constants(filename):
    """ Parse python constants from a file """
    constants = {}
    with open(filename, 'r') as infile:
        for line in infile:
            components = line.split('=')
            if len(components) <= 1:
                continue
            key = components[0].strip(' _')
            value = components[1].strip().strip('\'\"')
            constants[key] = value
    return constants


def _write_constants(filename, **constants):
    """ Write python constants to a file """
    with open(filename, 'w') as outfile:
        outfile.write('"""This file is auto-generated during the '
                      'package-building process"""%s' % os.linesep)
        for key, value in constants.iteritems():
            outfile.write("__%s__ = '%s'%s" % (key, value, os.linesep))


def get_version(package,
                describe_cmd=('git', 'describe'),
                describe_args=('--tags', '--dirty', '--match=[0-9]*'),
                version_mod='__version__.py'):
    """
    Generate the version from the git revision, or retrieve it from the
    auto-generated module

    Parameters
    ----------
    package : str
        The name of the directory that contains the package's code
    describe_cmd : list
        Command passed to subprocess to generate the version (default ['git',
        'describe'])
    describe_args : list
        Arguments for ``describe_cmd`` to be passed to subprocess (default
        ['--tags', '--dirty', '--match=[0-9]*'])
    version_mod : str, optional
        The name of the file to write the version into (default '__version__.py')

    Returns
    -------
    version : str
        The unique version of this package formatted for `PEP 440
        <http://www.python.org/dev/peps/pep-0440>`_
    source_label : str
        The unique version of this package with the git ref embedded, as per
        the output of ``git describe``.

    """
    here = os.path.abspath(os.path.dirname(__file__))
    version_file_path = os.path.join(here, package, version_mod)

    if os.path.isdir(os.path.join(here, '.git')):
        source_label = _git_describe(describe_cmd + describe_args)
        if DEV_BUILD.match(source_label):
            components = source_label.split('-')
            if components[-1] == 'dirty':
                components = components[:-1]
            parent_count = components[-2]
            version = '-'.join(components[:-2]) + '.dev%s' % parent_count
        else:
            version = source_label
        _write_constants(version_file_path, source_label=source_label,
                         version=version)
        return version, source_label
    else:
        constants = _parse_constants(version_file_path)
        return constants['version'], constants['source_label']
