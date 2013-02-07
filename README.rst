========
pykdtree
========

Objective
---------
pykdtree is a kd-tree implementation for fast nearest neighbour search.
The aim is to be the fastest implementation around for common use cases (low dimensions and low number of neighbours).

The implementation is based on scipy.spatial.cKDTree and libANN by combining the best features from both and focus on implementation efficiency.

The interface is similar to that of scipy.spatial.cKDTree except only Euclidean distance measure is supported.

Installation
------------
Default build of pykdtree with OpenMP enabled queries using libgomp

.. code-block:: bash

    $ cd <pykdtree_dir>
    $ python setup.py install

If it fails with undefined compiler flags or you want to use another OpenMP implementation please modify setup.py at the indicated point to match your system.

Building without OpenMP support is controlled by the USE_OMP environment variable

.. code-block:: bash

    $ cd <pykdtree_dir>
    $ export USE_OMP=0
    $ python setup.py install

Usage
-----
The usage of pykdtree is similar to scipy.spatial.cKDTree so for now refer to it's documentation

    >>> from pykdtree.kdtree import KDTree
    >>> kd_tree = KDTree(data_pts)
    >>> dist, idx = pkd_tree.query(query_pts, k=8)
    
The number of threads to be used in OpenMP enabled queries can be controlled with the standard OpenMP environment variable OMP_NUM_THREADS.

Test
----
Run the unit tests using nosetest

.. code-block:: bash

    $ cd <pykdtree_dir>
    $ python setup.py nosetests
