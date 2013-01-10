import os
from setuptools import setup, Extension


try:
    use_omp = int(os.environ['USE_OMP'])
except KeyError:
    use_omp = True

print use_omp    
if use_omp:
    extra_compile_args = ['-std=c99', '-O3', '-fopenmp']
    extra_link_args=['-lgomp']
else:
    extra_compile_args = ['-std=c99', '-O3']
    extra_link_args = []
    

        
setup(
    name='pykdtree',
    packages = ['pykdtree'],
    ext_modules = [Extension('pykdtree.kdtree', ['pykdtree/kdtree.c', 'pykdtree/_kdtree_core.c'], extra_compile_args=extra_compile_args, extra_link_args=extra_link_args)]
    )
    


