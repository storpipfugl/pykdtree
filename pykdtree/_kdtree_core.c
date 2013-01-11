#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <float.h>

#define PA(i,d)			(pa[no_dims * pidx[i] + d])
#define PASWAP(a,b) { uint32_t tmp = pidx[a]; pidx[a] = pidx[b]; pidx[b] = tmp; }

typedef struct
{
    double cut_val;
    int8_t cut_dim;
    uint32_t start_idx;
    uint32_t n;
    double cut_bounds_lv;
    double cut_bounds_hv;
    struct Node *left_child;
    struct Node *right_child;
} Node;

typedef struct
{
    double *bbox;
    int8_t no_dims;
    uint32_t *pidx;
    struct Node *root; 
} Tree;

void get_bounding_box(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t n, double *bbox);
int partition(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, double *bbox, int8_t *cut_dim, 
              double *cut_val, uint32_t *n_lo);
Tree* construct_tree(double *pa, int8_t no_dims, uint32_t n, uint32_t bsp);
Node* construct_subtree(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, uint32_t bsp, double *bbox);
Node * create_node(uint32_t start_idx, uint32_t n);
void delete_subtree(Node *root);
void delete_tree(Tree *tree);
void print_tree(Node *root, int level);
double calc_dist(double *point1_coord, double *point2_coord, int8_t no_dims);
double get_cube_offset(int8_t dim, double *point_coord, double *bbox);
double get_min_dist(double *point_coord, int8_t no_dims, double *bbox);
void search_leaf(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, double *point_coord, 
                 uint32_t *closest_idx, double *closest_dist);
void search_splitnode(Node *root, double * restrict pa, uint32_t * restrict pidx, int8_t no_dims, double * restrict point_coord, 
                      double min_dist, uint32_t * restrict closest_idx, double * restrict closest_dist);
void search_tree(Tree *tree, double * restrict pa, double * restrict point_coords, 
                 uint32_t num_points, uint32_t * restrict closest_idxs, double * restrict closest_dists);

/************************************************
Get the bounding box of a set of points
Params:
    pa : data points
    pidx : permutation index of data points
    no_dims: number of dimensions
    n : number of points
    bbox : bounding box (return)
************************************************/
void get_bounding_box(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t n, double *bbox)
{
    double cur;
    int8_t bbox_idx;

    /* Use first data point to initialize */
    for (int8_t i = 0; i < no_dims; i++)
    {
        bbox[2 * i] = bbox[2 * i + 1] = PA(0, i);
    }

    /* Update using rest of data points */
    for (uint32_t i = 1; i < n; i++)
    {
        for (int8_t j = 0; j < no_dims; j++)
        {
            bbox_idx = 2 * j;
            cur = PA(i, j);
            if (cur < bbox[bbox_idx])
            {
                bbox[bbox_idx] = cur;
            }
            else if (cur > bbox[bbox_idx + 1])
            {
                bbox[bbox_idx + 1] = cur;
            }
        }
    }
}

/************************************************
Partition a range of data points by manipulation the permutation index
Params:
    pa : data points
    pidx : permutation index of data points
    no_dims: number of dimensions
    start_idx : index of first data point to use
    n :  number of data points
    bbox : bounding box of data points
    cut_dim : dimension used for partition (return)
    cut_val : value of cutting point (return)
    n_lo : number of point below cutting plane (return)    
************************************************/
int partition(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, double *bbox, int8_t *cut_dim, double *cut_val, uint32_t *n_lo)
{
    int8_t dim = 0;
    uint32_t p, q;
    double size = 0, min_val, max_val, split, side_len, cur_val;
    uint32_t end_idx = start_idx + n - 1;
    
    /* Find largest bounding box side */
    for (int8_t i = 0; i < no_dims; i++)
    {
        side_len = bbox[2 * i + 1] - bbox[2 * i];
        if (side_len > size)
        {
            dim = i;
            size = side_len;
        }
    }
    
    min_val = bbox[2 * dim];
    max_val = bbox[2 * dim + 1];
    
    /* Check for zero length or inconsistent */
    if (min_val >= max_val)
        return 1;
    
    /* Use middle for splitting */    
    split = (min_val + max_val) / 2;
    
    /* Partition all data points around middle */
    p = start_idx;
    q = end_idx;
    while (p <= q)
    {
        if (PA(p, dim) < split)
        {
            p++;
        }
        else if (PA(q, dim) >= split)
        {
            /* Guard for underflow */
            if (q > 0) 
            {
                q--;
            }
            else
            {
                break; 
            }   
        }
        else
        {
            PASWAP(p, q);
            p++;
            q--;    
        } 
    }

    /* Check for empty splits */
    if (p == start_idx)
    {
        /* No points less than split. 
           Split at lowest point instead.
           Minimum 1 point will be in lower box.
        */
        
        uint32_t j = start_idx;
        split = PA(j, dim);
        for (uint32_t i = start_idx + 1; i <= end_idx; i++) 
        {
            /* Find lowest point */
            cur_val = PA(i, dim); 
            if (cur_val < split)
            {
                j = i;
                split = cur_val;
            }
        }
        PASWAP(j, start_idx);
        p = start_idx + 1;
    }
    else if (p == end_idx + 1)
    {
        /* No points greater than split. 
           Split at highest point instead.
           Minimum 1 point will be in higher box.
        */
        
        uint32_t j = end_idx;
        split = PA(j, dim);
        for (uint32_t i = start_idx; i < end_idx; i++)
        {
            /* Find highest point */
            cur_val = PA(i, dim);
            if (cur_val > split)
            {
                j = i;
                split = cur_val;
            }    
        }
        PASWAP(j, end_idx);
        p = end_idx;    
    }
    
    /* Set return values */
    *cut_dim = dim;
    *cut_val = split;
    *n_lo = p - start_idx;
    return 0;
}

/************************************************
Construct a sub tree over a range of data points.
Params:
    pa : data points
    pidx : permutation index of data points
    no_dims: number of dimensions
    start_idx : index of first data point to use
    n :  number of data points
    bsp : number of points per leaf
    bbox : bounding box of set of data points
************************************************/
Node* construct_subtree(double *pa, uint32_t *pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, uint32_t bsp, double *bbox)
{
    /* Create new node */
    Node *root = create_node(start_idx, n);
    if (n <= bsp)
    {   
        /* Make leaf node */
        root->cut_dim = -1;     
    }
    else
    {
        /* Make split node */
        int rval;
        int8_t cut_dim;
        uint32_t n_lo;
        double  cut_val;
        
        /* Partition data set and set node info */
        rval = partition(pa, pidx, no_dims, start_idx, n, bbox, &cut_dim, &cut_val, &n_lo);
        if (rval == 1)
        {
            root->cut_dim = -1;
            return root;         
        }
        root->cut_val = cut_val;
        root->cut_dim = cut_dim; 
        
        /* Recurse on both subsets */
        double lv = bbox[2 * cut_dim];
        double hv = bbox[2 * cut_dim + 1];
        
        root->cut_bounds_lv = lv;
        root->cut_bounds_hv = hv;
        
        bbox[2 * cut_dim + 1] = cut_val;
        root->left_child = (struct Node *)construct_subtree(pa, pidx, no_dims, start_idx, n_lo, bsp, bbox); 
        bbox[2 * cut_dim + 1] = hv;
        
        bbox[2 * cut_dim] = cut_val;
        root->right_child = (struct Node *)construct_subtree(pa, pidx, no_dims, start_idx + n_lo, n - n_lo, bsp, bbox); 
        bbox[2 * cut_dim] = lv;   
    }
    return root;    
}

/************************************************
Construct a tree over data points.
Params:
    pa : data points
    no_dims: number of dimensions
    n :  number of data points
    bsp : number of points per leaf
************************************************/
Tree* construct_tree(double *pa, int8_t no_dims, uint32_t n, uint32_t bsp)
{
    Tree *tree = (Tree *)malloc(sizeof(Tree));
    tree->no_dims = no_dims;
    
    /* Initialize permutation array */
    uint32_t *pidx = (uint32_t *)malloc(sizeof(uint32_t) * n);
    for (uint32_t i = 0; i < n; i++)
    {
        pidx[i] = i;
    }
    
    double *bbox = (double *)malloc(2 * sizeof(double) * no_dims);
    get_bounding_box(pa, pidx, no_dims, n, bbox);
    tree->bbox = bbox;

    /* Construct subtree on full dataset */
    tree->root = (struct Node *)construct_subtree(pa, pidx, no_dims, 0, n, bsp, bbox);

    tree->pidx = pidx;
    return tree;
}

/************************************************
Create a tree node.
Params:
    start_idx : index of first data point to use
    n :  number of data points    
************************************************/
Node* create_node(uint32_t start_idx, uint32_t n)
{
    Node *new_node = (Node *)malloc(sizeof(Node));
    new_node->n = n;
    new_node->start_idx = start_idx;
    return new_node;
}

/************************************************
Delete subtree
Params:
    root : root node of subtree to delete
************************************************/
void delete_subtree(Node *root)
{
    if (root->cut_dim != -1)
    {
        delete_subtree((Node *)root->left_child);
        delete_subtree((Node *)root->right_child);
    }
    free(root);
}

/************************************************
Delete tree
Params:
    tree : Tree struct of kd tree
************************************************/
void delete_tree(Tree *tree)
{
    delete_subtree((Node *)tree->root);
    free(tree->bbox);
    free(tree->pidx);
    free(tree);
}

/************************************************
Print
************************************************/
void print_tree(Node *root, int level)
{
    for (int i = 0; i < level; i++)
    {
        printf(" ");
    }
    printf("(cut_val: %f, cut_dim: %i)\n", root->cut_val, root->cut_dim);
    if (root->cut_dim != -1)
        print_tree((Node *)root->left_child, level + 1);
    if (root->cut_dim != -1)
        print_tree((Node *)root->right_child, level + 1);
}

/************************************************
Calculate squared cartesian distance between points
Params:
    point1_coord : point 1
    point2_coord : point 2
************************************************/
double calc_dist(double * restrict point1_coord, double * restrict point2_coord, int8_t no_dims)
{
    /* Calculate squared distance */    
    double dist = 0, dim_dist;
    for (int8_t i = 0; i < no_dims; i++)
    {
        dim_dist = point2_coord[i] - point1_coord[i];
        dist += dim_dist * dim_dist;
    }
    return dist;
}

/************************************************
Get squared distance from point to cube in specified dimension
Params:
    dim : dimension
    point_coord : cartesian coordinates of point
    bbox : cube
************************************************/
double get_cube_offset(int8_t dim, double * restrict point_coord, double * restrict bbox)
{
    double dim_coord = point_coord[dim];
    
    if (dim_coord < bbox[2 * dim])
    {
        /* Left of cube in dimension */
        return dim_coord - bbox[2 * dim];  
    }
    else if (dim_coord > bbox[2 * dim + 1])
    {
        /* Right of cube in dimension */
        return dim_coord - bbox[2 * dim + 1];
    }
    else
    {
        /* Inside cube in dimension */
        return 0.;
    }    
}

/************************************************
Get minimum squared distance between point and cube.
Params:
    point_coord : cartesian coordinates of point
    no_dims : number of dimensions
    bbox : cube
************************************************/
double get_min_dist(double * restrict point_coord, int8_t no_dims, double * restrict bbox)
{
    double cube_offset = 0, cube_offset_dim;

    for (int8_t i = 0; i < no_dims; i++)
    {
        cube_offset_dim = get_cube_offset(i, point_coord, bbox);
        cube_offset += cube_offset_dim * cube_offset_dim; 
    }

    return cube_offset;
}

/************************************************
Search a leaf node for closest point
Params:
    pa : data points
    pidx : permutation index of data points
    no_dims : number of dimensions    
    start_idx : index of first data point to use
    size :  number of data points
    point_coord : query point
    closest_idx : index of closest data point found (return)
    closest_dist : distance to closest point (return) 
************************************************/
void search_leaf(double * restrict pa, uint32_t * restrict pidx, int8_t no_dims, uint32_t start_idx, uint32_t n, double * restrict point_coord, 
                 uint32_t * restrict closest_idx, double * restrict closest_dist)
{
    double cur_dist;
    /* Loop through all points in leaf */    
    for (uint32_t i = 0; i < n; i++)
    {
        /* Get distance to query point */
        cur_dist = calc_dist(&PA(start_idx + i, 0), point_coord, no_dims);
        /* Update closest info if new point is closest so far*/
        if (cur_dist < *closest_dist)
        {
            *closest_idx = pidx[start_idx + i];
            *closest_dist = cur_dist;
        }
    }
}

/************************************************
Search subtree for nearest to query point
Params:
    root : root node of subtree
    pa : data points
    pidx : permutation index of data points
    no_dims : number of dimensions
    point_coord : query point
    min_dist : minumum distance to nearest neighbour
    closest_idx : index of closest data point found (return)
    closest_dist : distance to closest point (return) 
************************************************/
void search_splitnode(Node *root, double * restrict pa, uint32_t * restrict pidx, int8_t no_dims, double * restrict point_coord, 
                      double min_dist, uint32_t * restrict closest_idx, double * restrict closest_dist)
{
    int8_t dim;
    double dist_left, dist_right;
    double new_offset;
    double box_diff;
    
    dim = root->cut_dim;
    
    /* Handle leaf node */
    if (dim == -1)
    {
        search_leaf(pa, pidx, no_dims, root->start_idx, root->n, point_coord, closest_idx, closest_dist);
        return;
    }
    
    /* Get distance to cutting plane */
    new_offset = point_coord[dim] - root->cut_val;
    
    if (new_offset < 0)
    {
        /* Left of cutting plane */
        dist_left = min_dist;
        if (dist_left < *closest_dist)
        {
            /* Search left subtree */ 
            search_splitnode((Node *)root->left_child, pa, pidx, no_dims, point_coord, dist_left, closest_idx, closest_dist);
        }
        
        /* Right of cutting plane. Update minimum distance. Ref: D. Mount.*/
        box_diff = root->cut_bounds_lv - point_coord[dim];
        if (box_diff < 0)			
			box_diff = 0;
		dist_right = min_dist - box_diff * box_diff + new_offset * new_offset;
		if (dist_right < *closest_dist)
        {
            /* Search right subtree */ 
            search_splitnode((Node *)root->right_child, pa, pidx, no_dims, point_coord, dist_right, closest_idx, closest_dist);
        }
    }
    else
    {
        /* Right of cutting plane */
        dist_right = min_dist;
        if (dist_right < *closest_dist)
        {
            /* Search right subtree */ 
            search_splitnode((Node *)root->right_child, pa, pidx, no_dims, point_coord, dist_right, closest_idx, closest_dist);
        }
        
        /* Left of cutting plane. Update minimum distance. Ref: D. Mount.*/
        box_diff = point_coord[dim] - root->cut_bounds_hv;
        if (box_diff < 0)			
			box_diff = 0;
		dist_left = min_dist - box_diff * box_diff + new_offset * new_offset;
		if (dist_left < *closest_dist)
        {
            /* Search left subtree */ 
            search_splitnode((Node *)root->left_child, pa, pidx, no_dims, point_coord, dist_left, closest_idx, closest_dist);
        }
    }
}

/************************************************
Search for nearest neighbour for a set of query points
Params:
    tree : Tree struct of kd tree
    pa : data points
    pidx : permutation index of data points
    point_coords : query points
    closest_idx : index of closest data point found (return)
    closest_dist : distance to closest point (return) 
    bbox : bounding box of data points
************************************************/
void search_tree(Tree *tree, double * restrict pa, double * restrict point_coords, 
                 uint32_t num_points, uint32_t * restrict closest_idxs, double * restrict closest_dists)
{
    double min_dist;
    int8_t no_dims = tree->no_dims;
    double *bbox = tree->bbox;
    uint32_t *pidx = tree->pidx;
    Node *root = (Node *)tree->root;

    /* Queries are OpenMP enabled */
    #pragma omp parallel
    {
        /* The low chunk size is important to avoid L2 cache trashing  
           for spatial coherent query datasets
        */
        #pragma omp for schedule(static, 100) nowait
        for (uint32_t i = 0; i < num_points; i++)
        {
            closest_idxs[i] = UINT32_MAX;
            closest_dists[i] = DBL_MAX;
            min_dist = get_min_dist(point_coords + no_dims * i, no_dims, bbox);
            search_splitnode(root, pa, pidx, no_dims, point_coords + no_dims * i, min_dist,
                             &closest_idxs[i], &closest_dists[i]);
        }
    }
}

