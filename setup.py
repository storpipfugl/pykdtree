#pykdtree, Fast kd-tree implementation with OpenMP-enabled queries
#
#Copyright (C) 2013 - present  Esben S. Nielsen
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re
from functools import lru_cache
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


def is_conda_interpreter():
    """Is the running interpreter from Anaconda or miniconda?

    See https://stackoverflow.com/a/21318941/433202

    Examples::

        2.7.6 |Anaconda 1.8.0 (x86_64)| (default, Jan 10 2014, 11:23:15)
        2.7.6 |Continuum Analytics, Inc.| (default, Jan 10 2014, 11:23:15)
        3.6.6 | packaged by conda-forge | (default, Jul 26 2018, 09:55:02)

    """
    return 'conda' in sys.version or 'Continuum' in sys.version

def is_macOS():
    return 'darwin' in sys.platform


# HOMEBREW_SAMPLE = """$ brew ls --verbose libomp
# /opt/homebrew/Cellar/libomp/15.0.7/INSTALL_RECEIPT.json
# /opt/homebrew/Cellar/libomp/15.0.7/.brew/libomp.rb
# /opt/homebrew/Cellar/libomp/15.0.7/include/ompt.h
# /opt/homebrew/Cellar/libomp/15.0.7/include/omp.h
# /opt/homebrew/Cellar/libomp/15.0.7/include/omp-tools.h
# /opt/homebrew/Cellar/libomp/15.0.7/lib/libomp.dylib
# /opt/homebrew/Cellar/libomp/15.0.7/lib/libomp.a
# """
#
# MACPORTS_SAMPLE = """$ port contents libomp
# Port libomp contains:
#   /opt/local/include/libomp/omp-tools.h
#   /opt/local/include/libomp/omp.h
#   /opt/local/include/libomp/ompt.h
#   /opt/local/lib/libomp/libgomp.dylib
#   /opt/local/lib/libomp/libiomp5.dylib
#   /opt/local/lib/libomp/libomp.dylib
#   /opt/local/share/doc/libomp/LICENSE.TXT
#   /opt/local/share/doc/libomp/README.txt
# """


def compile_link_paths_from_manifest(cmd):
    from subprocess import run
    query = run(cmd, shell=True, check=False, capture_output=True)
    if query.returncode != 0:
        return None, None
    manifest = query.stdout.decode("UTF-8")
    # find all the unique directories mentioned in the manifest
    dirs = set(os.path.split(filename)[0] for filename in re.findall(r'^\s*(/.*?)\s*$', manifest, re.MULTILINE))
    # find a unique libdir and incdir
    inc = tuple(d for d in dirs if '/include/' in d)
    lib = tuple(d for d in dirs if '/lib/' in d)
    # only return success if there's no ambiguity
    return (inc + lib) if len(inc) == 1 and len(lib) == 1 else (None, None)


@lru_cache(maxsize=1)
def macOS_omp_options_from_probe():
    """Get common include and library paths for libomp installation on macOS.
       For example ``(['-I/opt/local/include/libomp'], ['-L/opt/local/lib/libomp'])``.
    """
    if is_macOS():
        for cmd in ["brew ls --verbose libomp", "port contents libomp"]:
            inc, lib = compile_link_paths_from_manifest(cmd)
            if inc and lib:
                return [f"-I{inc}"], [f"-L{lib}"]
    return [], []

def is_macOS_with_libomp():
    if not is_macOS():
        return False
    inc, lib = macOS_omp_options_from_probe()
    return bool(inc) and bool(lib)

OMP_TAB = {
    '1': 'gomp',
    '0': None,
    'gcc': 'gomp',
    'gomp': 'gomp',
    'clang': 'omp',
    'omp': 'omp',
    'probe': ('gomp' if (not is_macOS() or is_conda_interpreter())
              else ('omp' if is_macOS_with_libomp() else None))
}

OMP_COMPILE_ARGS = {
    'gomp': ['-fopenmp'],
    'omp': ['-Xpreprocessor', '-fopenmp']
}

OMP_LINK_ARGS = {
    'gomp': ['-lgomp'],
    'omp': ['-lomp']
}

# Get OpenMP setting from environment
# OpenMP is not supported with default clang
# Conda provides its own compiler which does support openmp
use_omp = OMP_TAB[os.environ.get('USE_OMP', 'probe')]


def set_builtin(name, value):
    if isinstance(__builtins__, dict):
        __builtins__[name] = value
    else:
        setattr(__builtins__, name, value)


# Custom builder to handler compiler flags. Edit if needed.
class build_ext_subclass(build_ext):
    def build_extensions(self):
        comp = self.compiler.compiler_type
        omp_probed_incl_args, omp_probed_link_args = macOS_omp_options_from_probe() if use_omp=="omp" else ([], [])
        omp_comp = OMP_COMPILE_ARGS.get(use_omp, []) + omp_probed_incl_args
        omp_link = OMP_LINK_ARGS.get(use_omp, []) + omp_probed_link_args
        print(f">>>> {comp} {use_omp} {omp_comp} {omp_link}")
        if comp in ('unix', 'cygwin', 'mingw32'):
            extra_compile_args = ['-std=c99', '-O3'] + omp_comp
            extra_link_args = omp_link
        elif comp == 'msvc':
            extra_compile_args = ['/Ox']
            extra_link_args = []
            if use_omp:
                extra_compile_args.append('/openmp')
        else:
            # Add support for more compilers here
            raise ValueError('Compiler flags undefined for %s. Please modify setup.py and add compiler flags'
                             % comp)
        self.extensions[0].extra_compile_args = extra_compile_args
        self.extensions[0].extra_link_args = extra_link_args
        build_ext.build_extensions(self)

    def finalize_options(self):
        '''
        In order to avoid premature import of numpy before it gets installed as a dependency
        get numpy include directories during the extensions building process
        http://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
        '''
        build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        set_builtin('__NUMPY_SETUP__', False)
        import numpy
        self.include_dirs.append(numpy.get_include())

with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

setup(
    name='pykdtree',
    version='1.3.6',
    url="https://github.com/storpipfugl/pykdtree",
    description='Fast kd-tree implementation with OpenMP-enabled queries',
    long_description=readme,
    author='Esben S. Nielsen',
    author_email='storpipfugl@gmail.com',
    packages=['pykdtree'],
    python_requires='>=3.7',
    install_requires=['numpy'],
    setup_requires=['numpy'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=[Extension('pykdtree.kdtree',
                           ['pykdtree/kdtree.c', 'pykdtree/_kdtree_core.c'])],
    cmdclass={'build_ext': build_ext_subclass},
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      ('License :: OSI Approved :: '
          'GNU Lesser General Public License v3 (LGPLv3)'),
      'Programming Language :: Python',
      'Operating System :: OS Independent',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering'
      ]
    )
