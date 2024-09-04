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

import numpy as np
from Cython.Build import build_ext
from Cython.Distutils import Extension
from setuptools import setup
from setuptools.command.build_ext import build_ext


OMP_SETTING_TABLE = {
    '1': 'probe',
    '0': None,
    'gcc': 'gomp',
    'gomp': 'gomp',
    'clang': 'omp',
    'omp': 'omp',
    'msvc': 'msvc',
    'probe': 'probe'
}

OMP_COMPILE_ARGS = {
    'gomp': ['-fopenmp'],
    'omp': ['-Xpreprocessor', '-fopenmp'],
    'msvc': ['/openmp']
}

OMP_LINK_ARGS = {
    'gomp': ['-lgomp'],
    'omp': ['-lomp'],
    'msvc': []
}


class build_ext_subclass(build_ext):
    """Custom extension building to have platform and compiler specific flags."""

    def build_extensions(self):
        comp = self.compiler.compiler_type
        omp_comp, omp_link = _omp_compile_link_args(comp)
        if comp in ('unix', 'cygwin', 'mingw32'):
            extra_compile_args = ['-std=c17', '-O3'] + omp_comp
            extra_link_args = omp_link
        elif comp == 'msvc':
            extra_compile_args = ['/Ox'] + omp_comp
            extra_link_args = omp_link
        else:
            # Add support for more compilers here
            raise ValueError('Compiler flags undefined for %s. Please modify setup.py and add compiler flags'
                             % comp)
        self.extensions[0].extra_compile_args = extra_compile_args
        self.extensions[0].extra_link_args = extra_link_args
        build_ext.build_extensions(self)


def _omp_compile_link_args(compiler):
    # Get OpenMP setting from environment
    use_omp = OMP_SETTING_TABLE[os.environ.get('USE_OMP', 'probe')]

    compile_args = []
    link_args = []
    if use_omp == "probe":
        use_omp, compile_args, link_args = _probe_omp_for_compiler_and_platform(compiler)

    print(f"Will use {use_omp} for OpenMP." if use_omp else "OpenMP support not available.")
    compile_args += OMP_COMPILE_ARGS.get(use_omp, [])
    link_args += OMP_LINK_ARGS.get(use_omp, [])
    print(f"Compiler: {compiler} / OpenMP: {use_omp} / OpenMP compile args: {compile_args} / OpenMP link args: {link_args}")
    return compile_args, link_args


def _probe_omp_for_compiler_and_platform(compiler):
    compile_args = []
    link_args = []
    if compiler == "msvc":
        use_omp = "msvc"
    elif _is_conda_interpreter():
        # Conda provides its own compiler which does support openmp
        use_omp = "gomp"
    elif _is_macOS():
        # OpenMP is not supported with system clang but homebrew and macports have libomp packages
        compile_args, link_args = _macOS_omp_options_from_probe()
        if not (compile_args or link_args):
            print("Probe for libomp failed, skipping use of OpenMP with clang.")
            print("It may be possible to build with OpenMP using USE_OMP=clang with CFLAGS and LDFLAGS explicit settings to use libomp.")
            use_omp = None
        else:
            use_omp = "omp"
    else:
        use_omp = "gomp"
    return use_omp, compile_args, link_args


def _is_conda_interpreter():
    """Is the running interpreter from Anaconda or miniconda?

    See https://stackoverflow.com/a/21318941/433202

    Examples::

        2.7.6 |Anaconda 1.8.0 (x86_64)| (default, Jan 10 2014, 11:23:15)
        2.7.6 |Continuum Analytics, Inc.| (default, Jan 10 2014, 11:23:15)
        3.6.6 | packaged by conda-forge | (default, Jul 26 2018, 09:55:02)

    """
    return 'conda' in sys.version or 'Continuum' in sys.version


def _is_macOS():
    return 'darwin' in sys.platform


def _macOS_omp_options_from_probe():
    """Get common include and library paths for libomp installation on macOS.

    For example ``(['-I/opt/local/include/libomp'], ['-L/opt/local/lib/libomp'])``.

    """
    for cmd in ["brew ls --verbose libomp", "port contents libomp"]:
        inc, lib = _compile_link_paths_from_manifest(cmd)
        if inc and lib:
            return [f"-I{inc}"], [f"-L{lib}"]
    return [], []    


def _compile_link_paths_from_manifest(cmd):
    """Parse include and library paths from OSX package managers.

    Example executions::

        # Homebrew
        $ brew ls --verbose libomp
        /opt/homebrew/Cellar/libomp/15.0.7/INSTALL_RECEIPT.json
        /opt/homebrew/Cellar/libomp/15.0.7/.brew/libomp.rb
        /opt/homebrew/Cellar/libomp/15.0.7/include/ompt.h
        /opt/homebrew/Cellar/libomp/15.0.7/include/omp.h
        /opt/homebrew/Cellar/libomp/15.0.7/include/omp-tools.h
        /opt/homebrew/Cellar/libomp/15.0.7/lib/libomp.dylib
        /opt/homebrew/Cellar/libomp/15.0.7/lib/libomp.a

        # MacPorts
        $ port contents libomp
        Port libomp contains:
          /opt/local/include/libomp/omp-tools.h
          /opt/local/include/libomp/omp.h
          /opt/local/include/libomp/ompt.h
          /opt/local/lib/libomp/libgomp.dylib
          /opt/local/lib/libomp/libiomp5.dylib
          /opt/local/lib/libomp/libomp.dylib
          /opt/local/share/doc/libomp/LICENSE.TXT
          /opt/local/share/doc/libomp/README.txt

    """
    from subprocess import run
    query = run(cmd, shell=True, check=False, capture_output=True)
    if query.returncode != 0:
        return None, None
    manifest = query.stdout.decode("UTF-8")
    # find all the unique directories mentioned in the manifest
    dirs = set(os.path.split(filename)[0] for filename in re.findall(r'^\s*(/.*?)\s*$', manifest, re.MULTILINE))
    # find a unique libdir and incdir
    inc = tuple(d for d in dirs if re.search(r'/include(\W|$)', d))
    lib = tuple(d for d in dirs if re.search(r'/lib(\W|$)', d))
    # only return success if there's no ambiguity
    return (inc + lib) if len(inc) == 1 and len(lib) == 1 else (None, None)


with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

extensions = [
    Extension('pykdtree.kdtree', sources=['pykdtree/kdtree.pyx', 'pykdtree/_kdtree_core.c'],
              include_dirs=[np.get_include()],
              define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
              cython_directives={"language_level": "3"},
              ),
]


setup(
    name='pykdtree',
    version='1.3.13',
    url="https://github.com/storpipfugl/pykdtree",
    description='Fast kd-tree implementation with OpenMP-enabled queries',
    long_description=readme,
    long_description_content_type="text/x-rst",
    author='Esben S. Nielsen',
    author_email='storpipfugl@gmail.com',
    packages=['pykdtree'],
    python_requires='>=3.9',
    install_requires=['numpy'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=extensions,
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

