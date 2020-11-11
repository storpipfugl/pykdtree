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


# Get OpenMP setting from environment
try:
    use_omp = int(os.environ['USE_OMP'])
except KeyError:
    # OpenMP is not supported with default clang
    # Conda provides its own compiler which does support openmp
    use_omp = 'darwin' not in sys.platform or is_conda_interpreter()


def set_builtin(name, value):
    if isinstance(__builtins__, dict):
        __builtins__[name] = value
    else:
        setattr(__builtins__, name, value)


# Custom builder to handler compiler flags. Edit if needed.
class build_ext_subclass(build_ext):
    def build_extensions(self):
        comp = self.compiler.compiler_type
        if comp in ('unix', 'cygwin', 'mingw32'):
            # Check if build is with OpenMP
            if use_omp:
                extra_compile_args = ['-std=c99', '-O3', '-fopenmp']
                extra_link_args=['-lgomp']
            else:
                extra_compile_args = ['-std=c99', '-O3']
                extra_link_args = []
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
    version='1.3.4',
    url="https://github.com/storpipfugl/pykdtree",
    description='Fast kd-tree implementation with OpenMP-enabled queries',
    long_description=readme,
    author='Esben S. Nielsen',
    author_email='storpipfugl@gmail.com',
    packages=['pykdtree'],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=['numpy'],
    setup_requires=['numpy'],
    tests_require=['nose'],
    zip_safe=False,
    test_suite='nose.collector',
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
