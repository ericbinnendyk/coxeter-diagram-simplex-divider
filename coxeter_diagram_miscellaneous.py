# Miscellaneous Coxeter diagram related functions for the simplex division program.

from math import pi, cos

def numerical_cox_mat_to_sch_mat(cox_mat):
    n = len(cox_mat)
    sch_mat = [[0]*n for i in range(n)]
    for i, row in enumerate(cox_mat):
        for j, label in enumerate(row):
            sch_mat[i][j] = -2*cos(pi/label)
    return sch_mat

def determinant(sch_mat):
    calculated = dict()
    n = len(sch_mat)
    def remove_elem(l, elem):
        return [x for x in l if x != elem]
    def alternating_sum(l):
        s = 0
        sign = 1
        for x in l:
            s += sign*x
            sign = -sign
        return s
    def memoized_subdeterminant(indices):
        starting_index = n - len(indices)
        if starting_index == n - 1:
            return sch_mat[-1][indices[0]]
        if tuple(indices) in calculated:
            return calculated[tuple(indices)]
        subsubdeterminants = [memoized_subdeterminant(remove_elem(indices, i)) for i in indices]
        multiplied_subsubdeterminants = [sch_mat[starting_index][i]*subsubdeterminants[index] for index, i in enumerate(indices)]
        det = alternating_sum(multiplied_subsubdeterminants)
        calculated[tuple(indices)] = det
        return det
    return memoized_subdeterminant(list(range(n)))

# Note: I suspect this might be wrong sometimes, like with noncompact hyperbolic groups.
def numerical_sphericality_check(cox_mat):
    sch_mat = numerical_cox_mat_to_sch_mat(cox_mat)
    sch_mat_det = determinant(sch_mat)
    return sch_mat_det > 0.0000001 # to account for floating point error if the determinant is exactly 0

# a dictionary mapping Coxeter diagrams to names of Coxeter groups (requires the canonical form of the diagram)
symmetry_group_names = {\
    'o3o3o': 'A(3)',
    'o4o3o': 'C(3)',
    'o5o3o': 'G(3)',
    'o3o3o3o': 'A(4)',
    'o3o3o *b3o': 'B(4)',
    'o4o3o3o': 'C(4)',
    'o3o4o3o': 'F(4)',
    'o5o3o3o': 'G(4)',
    'o3o3o3o3o': 'A(5)',
    'o3o3o3o *b3o': 'B(5)',
    'o4o3o3o3o': 'C(5)',
    'o3o3o3o3o3o': 'A(6)',
    'o3o3o3o3o *b3o': 'B(6)',
    'o4o3o3o3o3o': 'C(6)',
    'o3o3o3o3o *c3o': 'E(6)',
    'o3o3o3o3o3o3o': 'A(7)',
    'o3o3o3o3o3o *b3o': 'B(7)',
    'o4o3o3o3o3o3o': 'C(7)',
    'o3o3o3o3o3o *c3o': 'E(7)',
    'o3o3o3o3o3o3o3o': 'A(8)',
    'o3o3o3o3o3o3o *b3o': 'B(8)',
    'o4o3o3o3o3o3o3o': 'C(8)',
    'o3o3o3o3o3o3o *c3o': 'E(8)'}