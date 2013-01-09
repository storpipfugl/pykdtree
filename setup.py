from setuptools import setup, Extension

setup(
    name='pykdtree',
    packages = ['pykdtree'],
    ext_modules = [Extension('pykdtree.kdtree', ['pykdtree/kdtree.c', 'pykdtree/_kdtree_core.c'], extra_compile_args = ['-std=c99', '-O3', '-fopenmp'], extra_link_args=['-lgomp'])]
    )
    


