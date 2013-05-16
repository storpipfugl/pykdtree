#pykdtree, Fast kd-tree implementation with OpenMP-enabled queries
# 
#Copyright (C) 2013  Esben S. Nielsen
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# Get OpenMP setting from environment  
try:
    use_omp = int(os.environ['USE_OMP'])
except KeyError:
    use_omp = True

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
        else:
            # Add support for more compilers here
            raise ValueError(('Compiler flags undefined for %s.', 
                             'Please modify setup.py and add compiler flags')
                             % comp)
        self.extensions[0].extra_compile_args = extra_compile_args
        self.extensions[0].extra_link_args = extra_link_args
        build_ext.build_extensions(self)
 
        
setup(
    name='pykdtree',
    version=0.2,
    description='Fast kd-tree implementation with OpenMP-enabled queries',
    author='Esben S. Nielsen',
    author_email='esn@dmi.dk',
    packages = ['pykdtree'],
    install_requires=['numpy'],
    ext_modules = [Extension('pykdtree.kdtree', 
                             ['pykdtree/kdtree.c', 'pykdtree/_kdtree_core.c'])], 
    cmdclass = {'build_ext': build_ext_subclass },
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python',
      'Operating System :: OS Independent',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering'
      ]
    )
    


