import time
import threading

import numpy as np
cimport numpy as np
from libc.stdint cimport uint32_t
cimport cython


# Node structure
cdef struct node:
    double cut_val
    int cut_dim
    int start_idx
    int n
    double cut_bounds_lv
    double cut_bounds_hv
    node *left_child
    node *right_child
    
cdef struct tree:
    double *bbox
    int no_dims
    int *pidx
    node *root    
    

cdef extern tree* construct_tree(double *pa, int no_dims, int n, int bsp) nogil
cdef extern void search_tree(tree *kdtree, double *pa, double *point_coords, int num_points, int *closest_idxs, double *closest_dists) nogil
cdef extern void delete_tree(tree *kdtree)

cdef class KDTree:

    cdef tree *_kdtree
    cdef np.ndarray _data_array
    cdef double *_data_array_data
    cdef int n
    cdef int ndim
    
    def __init__(KDTree self, np.ndarray data_pts not None, int leafsize=10):
        cdef np.ndarray[double, ndim=1] data_array = np.ascontiguousarray(data_pts.ravel(), dtype=np.float64)
        self._data_array = data_array
        self._data_array_data = <double *>data_array.data
        self.n = data_pts.shape[0]
        if data_pts.ndim == 1:
            self.ndim = 1
        else:
            self.ndim = data_pts.shape[1] 
        
        with nogil:
            self._kdtree = construct_tree(self._data_array_data, self.ndim, self.n, leafsize) 
        
    def query(KDTree self, np.ndarray query_pts not None, sqr_dists=False):
        cdef np.ndarray[double, ndim=1] query_array = np.ascontiguousarray(query_pts.ravel(), dtype=np.float64)
        cdef double *query_array_data = <double *>query_array.data
        
        num_qpoints = query_pts.shape[0]
        cdef np.ndarray[int, ndim=1] closest_idxs = np.empty(num_qpoints, dtype=np.int32)
        cdef np.ndarray[double, ndim=1] closest_dists = np.empty(num_qpoints, dtype=np.float)
        cdef int *closest_idxs_data = <int *>closest_idxs.data
        cdef double *closest_dists_data = <double *>closest_dists.data
    
        with nogil:
            search_tree(self._kdtree, self._data_array_data, query_array_data, num_qpoints, closest_idxs_data, closest_dists_data)
        
        if sqr_dists:
            return np.sqrt(closest_dists), closest_idxs
        else:    
            return closest_dists, closest_idxs
    
    def __dealloc__(KDTree self):
        if <int>(self._kdtree) == 0:
            # should happen only if __init__ was never called
            return
        delete_tree(self._kdtree)
        

    
                        
            
    

    

