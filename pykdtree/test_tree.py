import numpy as np

from pykdtree.kdtree import KDTree


def test1d():
    data = np.arange(1000)
    kdtree = KDTree(data, 10)
    qpts = np.arange(400, 300, -10)
    idx, dist = kdtree.query(qpts)
    assert idx[0] == 400    
    
    
