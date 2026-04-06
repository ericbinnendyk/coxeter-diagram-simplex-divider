from fractions import Fraction as F
from functools import reduce
from coxeter_diagram_text_parser import init_matrix
import coxeter_diagram_polygon_fields as f
import coxeter_diagram_text_parser as c
import coxeter_diagram_miscellaneous as misc

fields = ['Q', 'Qq', 'Qf']

# stores the value -2cos(pi/p) for each label p, for each possible field in which it can appear
label_matrix_entries = {
    ('Q', 1): 2,
    ('Q', 2): 0,
    ('Q', 3): -1,
    ('Q', F(3,2)): 1,
    ('Qq', 1): f.Zq(2),
    ('Qq', 2): f.Zq(0),
    ('Qq', 3): f.Zq(-1),
    ('Qq', F(3,2)): f.Zq(1),
    ('Qq', 4): f.Zq(0,-1),
    ('Qq', F(4,3)): f.Zq(0,1),
    ('Qf', 1): f.Zf(2),
    ('Qf', 2): f.Zf(0),
    ('Qf', 3): f.Zf(-1),
    ('Qf', F(3,2)): f.Zf(1),
    ('Qf', 5): f.Zf(0,-1),
    ('Qf', F(5,2)): f.Zf(1,-1),
    ('Qf', F(5,3)): f.Zf(-1,1),
    ('Qf', F(5,4)): f.Zf(0,1)
}

matrix_entry_labels = dict() # converts Schlafli matrix entries back into labels
for field, label in label_matrix_entries:
    entry = label_matrix_entries[(field, label)]
    entry_as_tup = f.field_value_to_tuple(field, entry) # Field element objects aren't hashable so we have to extract the information into a tuple
    matrix_entry_labels[entry_as_tup] = label

# this one should return both a Schlafli matrix and a description of the field the values are in
# I'm going to use exact field arithmetic, and I'm planning to define a different type for each field (Update: Done)
# I'm not sure how I'm going to use the field ID outside of this function, as long as I overload the same operations for all the fields, but it's definitely something I should keep track of in this function.
def coxeter_matrix_to_schlafli_matrix(coxeter_matrix):
    dim = len(coxeter_matrix)
    schlafli_matrix = [[0]*dim for i in range(dim)]
    # first check what values the labels take to find the field
    field = None
    cox_entries = reduce(lambda x, y: x + y, coxeter_matrix) # all the entries of the coxeter matrix, in a list
    if all([p.numerator in {1,2,3} for p in cox_entries]):
        field = 'Q'
    elif all([p.numerator in {1,2,3,4} for p in cox_entries]):
        field = 'Qq'
    elif all([p.numerator in (1,2,3,5) for p in cox_entries]):
        field = 'Qf'
    else:
        print("Processing for Coxeter diagrams with labels other than 2/n, 3/n, and at most one of 4/n and 5/n is not implemented yet.")
        return None
    for i in range(dim):
        for j in range(dim):
            schlafli_matrix[i][j] = label_matrix_entries[(field, coxeter_matrix[i][j])]
    return schlafli_matrix, field

def schlafli_matrix_to_coxeter_matrix(schlafli_matrix, field):
    dim = len(schlafli_matrix)
    coxeter_matrix = [[0]*dim for i in range(dim)]
    for i in range(dim):
        for j in range(dim):
            entry_as_tup = f.field_value_to_tuple(field, schlafli_matrix[i][j])
            coxeter_matrix[i][j] = matrix_entry_labels[entry_as_tup]
    return coxeter_matrix

# given a Schlafli matrix entry for -2cos(pi/(p/q)) (p, q are integers and q > 1), return the Schlafli matrix entries for angles of -2cos(pi/p) and -2cos(pi/(p/(q - 1)))
def find_sub_angle_entries(mat_entry, field):
    if field == 'Q':
        # we're working with bare integers
        # single case: 1 splits into -1, -1
        if mat_entry == 1:
            return -1, -1
    elif field == 'Qq':
        if mat_entry == f.Zq(1,0):
            # 1 splits into -1, -1
            return f.Zq(-1,0), f.Zq(-1,0)
        elif mat_entry == f.Zq(0,1):
            # sqrt(2) splits into -sqrt(2), 0
            return f.Zq(0,-1), f.Zq(0,0)
        elif mat_entry == f.Zq(0,0):
            # 0 splits into -sqrt(2), -sqrt(2), but only if it represents 4/2.
            # Note: 0 doesn't always represent 4/2, even in the field Qq, so you should never use this function to determine if an angle *can* be split.
            return f.Zq(0,-1), f.Zq(0,-1)
    elif field == 'Qf':
        if mat_entry == f.Zf(1,0):
            # 1 splits into -1, -1
            return f.Zf(-1,0), f.Zf(-1,0)
        elif mat_entry == f.Zf(1,-1):
            # 1 - phi splits into -phi, -phi
            return f.Zf(0,-1), f.Zf(0,-1)
        elif mat_entry == f.Zf(-1,1):
            # -1 + phi splits into -phi, 1 - phi
            return f.Zf(0,-1), f.Zf(1,-1)
        elif mat_entry == f.Zf(0,1):
            # -1 + phi splits into -phi, 1 - phi
            return f.Zf(0,-1), f.Zf(-1,1)
    else:
        print("Unable to find sub-angle matrix entries because either the field isn't implemented or the angle can't be divided")
        return None

def get_breakable_entries(field):
    # saving this old code because it has some important comments in it
    '''if field == 'Q':
        return [1] # corresponding to 3/2, integers are stored natively
    elif field == 'Qq':
        return [f.Zq(1,0), f.Zq(0,1)] # corresponding to 3/2 and 4/3 respectively, 2 might sometimes be breakable (as 4/2) but there's no way of telling when AFAIK without building up the diagram from elementary diagrams
        # and as I mentioned elsewhere, this shouldn't be a problem because every time a diagram associated with this field contains a 4/2 it should also contain 3/2 and/or 4/3. Otherwise, the 4/2 can be replaced with a 2 to get a diagram with the same fundamental simplex, which is already convex.
        # in fact, for hypercubic symmetry at least, it seems like 4/2 can *always* be replaced by 2 to get a subsymmetric diagram
    elif field == 'Qf':
        return [f.Zf(1,0), f.Zf(1,-1), f.Zf(-1,1), f.Zf(0,1)]'''
    if field in fields:
        return [val for ((f, p), val) in label_matrix_entries.items() if f == field and type(p) == F and p.denominator > 1]
    else:
        print(f"Not yet able to find which entries in the Schlafli matrix are breakable in the field {field}")
        return None

# finds a pair of indices, representing a ridge, along which to divide the generator simplex (this might get more complicated as this program develops)
def find_indices_to_divide_on(m, field):
    # saving this code as it may have some important comments
    '''if field == 'Q':
        # CD contains 3, 2, and 3/2 and condition is equivalent to vertices having a label of 3/2
        for index1 in range(len(m)):
            for index2 in range(len(m[0])):
                if m[index1][index2] == 1:
                    return index1, index2
    elif field == 'Qq':
        # Searching for a label of 3/2 or 4/3, corresponding to a Schlafli matrix entry of 1 or sqrt(2)
        # We could also divide on a label of 4/2 if we knew it wasn't just 2. But with the way I'm storing these simplices, there's no way to obtain that information.
        # Besides, it's not necessary: if all labels were 2, 3, and 4, it would already represent a convex symmetry
        for index1 in range(len(m)):
            for index2 in range(len(m[0])):
                if m[index1][index2] in [f.Zq(1,0), f.Zq(0,1)]:
                    return index1, index2
    elif field == 'Qf':
        # Searching for a label of 3/2, 5/2, 5/3, or 5/4
        for index1 in range(len(m)):
            for index2 in range(len(m[0])):
                if m[index1][index2] in [f.Zf(1,0), f.Zf(1,-1), f.Zf(-1,1), f.Zf(0,1)]:
                    return index1, index2'''
    if field in fields:
        breakable_entries = get_breakable_entries(field)
        for index1 in range(len(m)):
            for index2 in range(len(m[0])):
                if m[index1][index2] in breakable_entries:
                    return index1, index2
    else:
        print(f"Finding a ridge on which to divide the spherical simplex not implemented for field {field} yet.")
        return None
    return None, None # need to return two values due to how we'll be unpacking them

# This is the main formula for finding angles between mirrors in a divided fundamental simplex, in terms of angles of the original simplex and the angle of the dividing plane.
# Given mirrors with unit normal vectors v1 and v2 and a specific angle at which to break the mirror intersection, you get a third vector w in the same plane, normal to the new mirror.
# Define w to be pointing outward in a way such that the v1 mirror is on the "inside" of the w mirror
# The angles between the mirrors and the w-mirror are given by the inner products <v1, w> and <v2, w>
# Given another vector vi, we can calculate <vi, w> in terms of <v1, w>, <v2, w>, <v1, v2>, <v1, vi>, and <v2, vi> by the formula given here
# Except that because this function is designed for use in the Schlafli matrix, all of these inner products are doubled, as is the output.
def angle_division_formula(twice_v1w, twice_v2w, twice_v1v2, twice_v1vi, twice_v2vi):
    return ((2*twice_v1w - twice_v2w*twice_v1v2)*twice_v1vi + (2*twice_v2w - twice_v1w*twice_v1v2)*twice_v2vi)//(4 - twice_v1v2**2)

# divides the spherical simplex in two by bisecting the ditopal angle between the two facets given by the two indices
# Assumes that the ditopal angle has already been found to be dividable
# Important: if we break on an n/d label, the first matrix returned has an n label and the second has an n/(d - 1) label.
def divideInTwo(m, field, index1, index2): # should return two matrices
    # this was too long to just get rid of
    '''if field == 'Q':
        if m[index1][index2] != 1: # corresponding to branch label of 3/2
            print("Cannot break simplex at this angle")
        half_angle_entry = None
        if m[index1][index2] == 1:
            half_angle_entry = -1
        new_m_1 = init_matrix(len(m), len(m[0]))
        new_m_2 = init_matrix(len(m), len(m[0]))
        for i in range(len(m)):
            for j in range(len(m[0])):
                if i != index2 and j != index2:
                    new_m_1[i][j] = m[i][j]
        new_m_1[index2][index2] = -2
        new_m_1[index1][index2] = half_angle_entry
        new_m_1[index2][index1] = half_angle_entry
        for i in range(len(m)):
            if i != index1 and i != index2:
                new_m_1[i][index2] = (m[i][index2] - m[i][index1])//(-half_angle_entry) # this integer division will need to become something more complicated when i deal with other fields
                new_m_1[index2][i] = new_m_1[i][index2]
        for i in range(len(m)):
            for j in range(len(m[0])):
                if i != index1 and j != index1:
                    new_m_2[i][j] = m[i][j]
        new_m_2[index1][index1] = 1
        new_m_2[index1][index2] = half_angle_entry
        new_m_2[index2][index1] = half_angle_entry
        for i in range(len(m)):
            if i != index1 and i != index2:
                new_m_2[i][index1] = (m[i][index1] - m[i][index2])//(-half_angle_entry)
                new_m_2[index1][i] = new_m_1[i][index1]
        return new_m_1, new_m_2'''
    if field in fields:
        sub_angle_entry_1, sub_angle_entry_2 = find_sub_angle_entries(m[index1][index2], field) # the Schlafli matrix entries corresponding to the two partitioned angles
        new_m_1 = init_matrix(len(m), len(m[0]))
        new_m_2 = init_matrix(len(m), len(m[0]))
        # let's say we're breaking the angle between the mirrors perpendicular to vectors v1 and v2
        # replacing vector v2 (index2) in original matrix by w
        # all inner products that don't involve v2 stay the same
        for i in range(len(m)):
            for j in range(len(m[0])):
                if i != index2 and j != index2:
                    new_m_1[i][j] = m[i][j]
        # fill in 2<w, w> = 2 and 2<v1, w>
        new_m_1[index2][index2] = f.field_equivalent_int(field, 2)
        new_m_1[index1][index2] = sub_angle_entry_1
        new_m_1[index2][index1] = sub_angle_entry_1
        # fill in 2<vi, w> entries
        for i in range(len(m)):
            if i != index1 and i != index2:
                new_m_1[i][index2] = angle_division_formula(sub_angle_entry_1, -sub_angle_entry_2, m[index1][index2], m[index1][i], m[index2][i]) # division formula for arbitrary angles, written in terms of 2<vi, vj>
                new_m_1[index2][i] = new_m_1[i][index2]
        # now to fill in matrix 2
        # replacing vector v1 (index1) in original matrix by -w
        # all inner products that don't involve v1 stay the same
        for i in range(len(m)):
            for j in range(len(m[0])):
                if i != index1 and j != index1:
                    new_m_2[i][j] = m[i][j]
        # fill in 2<-w, -w> = 2 and 2<v2, -w>
        new_m_2[index1][index1] = f.field_equivalent_int(field, 2)
        new_m_2[index1][index2] = sub_angle_entry_2
        new_m_2[index2][index1] = sub_angle_entry_2
        # fill in <vi, -w> entries (actually Schalfli matrix entry is 2<vi, -w>)
        for i in range(len(m)):
            if i != index1 and i != index2:
                new_m_2[i][index1] = angle_division_formula(sub_angle_entry_2, -sub_angle_entry_1, m[index1][index2], m[index2][i], m[index1][i]) # this should be just the negative of the first entry, because it's 2<-w, vi> while the previous was 2<w, vi>
                new_m_2[index1][i] = new_m_2[i][index1]
        return new_m_1, new_m_2
    else:
        print(f"Dividing a spherical simplex not implemented for field {field} yet.")
        return None

# similar to divideInTwo, but if the label of the edge (index1, index2) is p/d, divides the domain into d domains with labels of p
def divide_in_d(m, field, index1, index2):
    # First of all, we can't just repeatedly call divideInTwo until get_breakable_entries reports that the angle is indivisible.
    # If we start with a 4/3 label, that test would report that a 4/2 label is indivisible because its Schlafli matrix entry equals that of a 2 label.
    # Instead, we need to find the value of d first and force a division that many times, minus one.
    d = matrix_entry_labels[f.field_value_to_tuple(field, m[index1][index2])].denominator
    division_matrices = []
    for i in range(d - 1):
        sub_matrix, m = divideInTwo(m, field, index1, index2)
        division_matrices.append(sub_matrix)
    division_matrices.append(m)
    return division_matrices

def print_matrix(m):
    padding = 1
    for row in m:
        for val in row:
            if len(str(val)) > padding:
                padding = len(str(val))
    for row in m:
        print('[', end='')
        for i, val in enumerate(row):
            print(str(val) + ' '*(padding - len(str(val))), end='')
            if i < len(row) - 1:
                print(' ', end='')
        print(']')
    print() # empty row at the end of the matrix in case we're printing multiple matrices in succession

# only tests whether the entries correspond to rational angles. doesn't test whether entries along the diagonal are 2 or the matrix is symmetric.
def is_valid_schlafli_matrix(m, field):
    m_entries = reduce(lambda x, y: x + y, m) # all the entries of m, in a list
    if field in fields:
        allowed = [label_matrix_entries[(f, label)] for f, label in label_matrix_entries if f == field]
    else:
        print(f"Error: checking if the Schlafli matrix is valid is not implemented for field {field}")
        return None
    return all([x in allowed for x in m_entries])

# The main function that gets called to find the symmtery of the Coxeter diagram.
def find_and_print_symmetry(cox_mat):
    schlafli_matrix, field = coxeter_matrix_to_schlafli_matrix(cox_mat)
    print("Field:", field)
    print("Initial Schlafli matrix:")
    print_matrix(schlafli_matrix)
    num_steps = 0
    while True:
        index1, index2 = find_indices_to_divide_on(schlafli_matrix, field)
        if index1 == None:
            print(f"Reached a convex Coxeter diagram in {num_steps} steps.")
            convex_diagram = c.coxeter_matrix_to_cox_str(cox_mat)
            extra_info = '(' + misc.symmetry_group_names[convex_diagram] + ')' if convex_diagram in misc.symmetry_group_names else ''
            print(f"Symmetry: {convex_diagram}", extra_info)
            break
        print(f"Dividing on mirrors {index1}, {index2}")
        print("New Schlafli matrix:")
        new_matrix = divideInTwo(schlafli_matrix, field, index1, index2)[0]
        print_matrix(new_matrix)
        num_steps += 1
        if is_valid_schlafli_matrix(new_matrix, field):
            schlafli_matrix = new_matrix
            cox_mat = schlafli_matrix_to_coxeter_matrix(schlafli_matrix, field)
            print("Coxeter-Dynkin diagram:", c.coxeter_matrix_to_cox_str(cox_mat))
        else:
            print("Reached a fundamental domain with irrational angles.")
            print("Group is dense.")
            break

# Finds the density of the fundamental domain tiling given by Schlafli matrix m with entries in given field,
# equal to the number of elementary domains that make it up
# One might wonder, considering that n-demicubic symmetry is a subgroup of n-cubic symmetry, if the method of simply counting elementary domains is reliable.
# After all, it seems conceivable that one of the subdomains of a cubic symmetry domain might "appear" elementary demicubic because it contains 2, 3, and 4/2, and the 4/2 is indistinguishable from 2.
# I have a proof that that never happens, which is too long to fit in these comments.
# It comes from the idea that every transformation between a pair of fundamental simplices (i.e. sets of group generators) is "reversible" in some sense.
def find_density(m, field):
    index1, index2 = find_indices_to_divide_on(m, field)
    if index1 == None:
        return 1 # reached a convex diagram
    sub_m_list = divide_in_d(m, field, index1, index2)
    return sum(find_density(mi, field) for mi in sub_m_list)

'''print_matrix(schlafli_matrix)
while True:
    index1, index2 = find_indices_to_divide_on(schlafli_matrix)
    if index1 == None:
        print("Reached a convex Coxeter diagram.")
        break
    print(f"Bisecting on mirrors {index1}, {index2}")
    new_matrix = divideInTwo(schlafli_matrix, index1, index2)[0]
    print_matrix(new_matrix)
    schlafli_matrix = new_matrix'''

# Useful list of examples
'''
cd_diagram = 'o3o3o3o3o3*a3/2*c' # house-shaped diagram that has B(5) (D_5 if you're a normie) symmetry
cd_diagram = 'o3o3o3o *b4/3o4*c' # diagram associated with the ENS prefix dogeo- with C(5) (BC_5) symmetry
cd_diagram = 'o3o3/2o3/2o *b4/3o4/3*c'
cd_diagram = 'o3o4o4/3*a3o *b3/2*d *c4*d' # kavahto family
cd_diagram = 'o3o4o4/3*a' # gocco family - a simple test for Qq angle dividing
cd_diagram = 'o3o3o4o4/3*b'
cd_diagram = 'o3o4o3o4/3*b'
cd_diagram = 'o4o3o4/3o' # This is Euclidean. Apparently the standard algorithm to find a convex diagram (which only goes down one path of the recursion tree) breaks here, because it gives a result containing an edge labeled 1 (or infinity'). I'm not sure if doing a BFS over all branches will always find a valid convex diagram. A DFS runs the risk of going into an infinite loop if the fundamental domain is infinite. Not to mention, the "fundamental domain" concept doesn't even apply to all sets of mirrors in Euclidean and hyperbolic space.
cd_diagram = 'o3o3/2o4*a' # a non-example, spherical but dense, should fail to find convex diagram
cd_diagram = 'o3o5/2o' # first test with 5's
cd_diagram = 'o3o5/2o3o' # a non-example, a dense conjugate of a hyperbolic diagram
cd_diagram = 'o3o3o5/2o'
cd_diagram = 'o5o5/3o5/4o'
cd_diagram = 'o3o3/2o'
'''
cd_diagram = input("Enter Coxeter-Dynkin diagram here: ")
cox_mat = c.cox_str_to_coxeter_matrix(cd_diagram)

# check connectivity before proceeding; non-connected diagrams won't be processed because they're trivial and the canonizer doesn't work on them (yet)
if not c.check_connectivity(cox_mat):
    print("The CD entered is disconnected. Please enter its components separately.")
    exit()

# check if it is less than 3 dimensions, in which case it's trivial (plus, I haven't implemented all the infinitely many polygon fields)
n = len(cox_mat)
if n == 2:
    sym = F(cox_mat[0][1]).numerator
    density = F(cox_mat[0][1]).denominator
    print(f"The CD is 2D. It has {sym}-gonal symmetry and a density of {density}.")
    exit()
if n < 2:
    print("The CD is trivial.")
    exit()

# check that it is spherical, not Euclidean or hyperbolic
if not misc.numerical_sphericality_check(cox_mat):
    print("This CD is not spherical. The program only works for spherical diagrams.")
    exit()

# convert to canonical form for display purposes
cd_diagram = c.coxeter_matrix_to_cox_str(cox_mat)
print("Coxeter-Dynkin diagram entered:", cd_diagram)

print("You can:")
print("1. Find the symmetry")
print("2. Find the density")
choice = input("Enter choice here: ")
try:
    choice = int(choice)
    if choice not in {1,2}:
        raise RuntimeError
except:
    print("Invalid choice entered.")
    print("Goodbye.")
    exit()

if choice == 1:
    find_and_print_symmetry(cox_mat)
if choice == 2:
    print("Note: Memoization hasn't been implemented, so this may take a long time for large symmetry groups.")
    print("If the density is n, this operation will take n steps.")
    schlafli_matrix, field = coxeter_matrix_to_schlafli_matrix(cox_mat)
    d = find_density(schlafli_matrix, field)
    print(f"The density of {cd_diagram} is {d}")

'''# texsting a new in-progress coxeter matrix to coxeter diagram converter
# cypit (cyclopentachoric tetracomb/pyratilithoteron) family
M = \
[[1,3,2,2,3],
 [3,1,3,2,2],
 [2,3,1,3,2],
 [2,2,3,1,3],
 [3,2,2,3,1]]'''
'''# demipenteract family except w/ 3/2
M = \
[[1,3,2,2,2],
 [3,1,3,2,F(3,2)],
 [2,3,1,3,2],
 [2,2,3,1,2],
 [2,F(3,2),2,2,1]]
# a loop-n-tail diagram
# should be o3o5/2o3o *a3*c under the default ordering
# should be o3o5/2o3o3*b under the ordering [3,2,1,0]
M = \
[[1,3,3,2],
 [3,1,F(5,2),2],
 [3,F(5,2),1,3],
 [2,2,3,1]]

print(coxeter_matrix_to_cox_str(M))'''