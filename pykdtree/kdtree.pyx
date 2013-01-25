import time
import threading

import numpy as np
cimport numpy as np
from libc.stdint cimport uint32_t, int8_t
cimport cython


# Node structure
cdef struct node:
    double cut_val
    int8_t cut_dim
    uint32_t start_idx
    uint32_t n
    double cut_bounds_lv
    double cut_bounds_hv
    node *left_child
    node *right_child
    
cdef struct tree:
    double *bbox
    int8_t no_dims
    uint32_t *pidx
    node *root    
    

cdef extern tree* construct_tree(double *pa, int8_t no_dims, uint32_t n, uint32_t bsp) nogil
cdef extern void search_tree(tree *kdtree, double *pa, double *point_coords, uint32_t num_points, uint32_t k, uint32_t *closest_idxs, double *closest_dists) nogil
cdef extern void delete_tree(tree *kdtree)

cdef class KDTree:

    cdef tree *_kdtree
    cdef np.ndarray _data_array
    cdef double *_data_array_data
    cdef uint32_t n
    cdef int8_t ndim
    cdef uint32_t leafsize
    
    def __init__(KDTree self, np.ndarray data_pts not None, int leafsize=10):
        cdef np.ndarray[double, ndim=1] data_array = np.ascontiguousarray(data_pts.ravel(), dtype=np.float64)
        self._data_array = data_array
        self._data_array_data = <double *>data_array.data
        self.n = <uint32_t>data_pts.shape[0]
        self.leafsize = <uint32_t>leafsize
        if data_pts.ndim == 1:
            self.ndim = 1
        else:
            self.ndim = <int8_t>data_pts.shape[1] 
        
        with nogil:
            self._kdtree = construct_tree(self._data_array_data, self.ndim, self.n, self.leafsize) 
        
    def query(KDTree self, np.ndarray query_pts not None, k=1, distance_upper_bound=None, sqr_dists=False):
        cdef np.ndarray[double, ndim=1] query_array = np.ascontiguousarray(query_pts.ravel(), dtype=np.float64)
        cdef double *query_array_data = <double *>query_array.data
        
        cdef uint32_t num_qpoints = query_pts.shape[0]
        cdef uint32_t num_n = k
        cdef np.ndarray[uint32_t, ndim=1] closest_idxs = np.empty(num_qpoints * k, dtype=np.uint32)
        cdef np.ndarray[double, ndim=1] closest_dists = np.empty(num_qpoints * k, dtype=np.float64)
        cdef uint32_t *closest_idxs_data = <uint32_t *>closest_idxs.data
        cdef double *closest_dists_data = <double *>closest_dists.data
    
        with nogil:
            search_tree(self._kdtree, self._data_array_data, query_array_data, num_qpoints, num_n, closest_idxs_data, closest_dists_data)
        
        if sqr_dists:
            return np.sqrt(closest_dists), closest_idxs
        else:    
            return closest_dists, closest_idxs
    
    def __dealloc__(KDTree self):
        if <int>(self._kdtree) == 0:
            # should happen only if __init__ was never called
            return
        delete_tree(self._kdtree)
        

    
                        
            
    

    

