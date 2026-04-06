# I guess this will get added to coxeter_diagram_simplex_division.py later.

# Coxeter diagram parser, text to Coxeter matrix (not Schlafli matrix, for now)

from fractions import Fraction as F

class CDToken:
    # type - either 'branch', 'node', 'virtualnode', 'space'
    # content - how the token displays as text; always a string, even when it represents an integer
    def __init__(self, type, content):
        self.type = type
        self.content = content
    def __repr__(self):
        return self.content

def init_matrix(x, y, val=0):
    m = []
    for i in range(x):
        m.append([val]*y)
    return m

# returns the first token plus the rest
def next_token(cox_str_suffix, prev_tokens):
    if cox_str_suffix == '':
        return None
    if cox_str_suffix[0] in 'abcdefghijklmnopqrstuvwxyz' and (len(prev_tokens) == 0 or len(prev_tokens) > 0 and (prev_tokens[-1].type == 'space' or prev_tokens[-1].type == 'branch')):
        next = CDToken('node', cox_str_suffix[0])
        rest = cox_str_suffix[1:]
        return (next, rest)
    if cox_str_suffix[0] == '*' and cox_str_suffix[1] in 'abcdefghijklmnopqrstuvwxyz' and (len(prev_tokens) > 0 and (prev_tokens[-1].type == 'space' or prev_tokens[-1].type == 'branch')):
        next = CDToken('virtualnode', cox_str_suffix[:2])
        rest = cox_str_suffix[2:]
        return (next, rest)
    if cox_str_suffix[0] in '0123456789' and (len(prev_tokens) > 0 and prev_tokens[-1].type in {'node', 'virtualnode'}):
        # looks like a branch label, which could be multiple digits or a fraction
        # let's find where it ends
        j = 1
        while j < len(cox_str_suffix) and cox_str_suffix[j] in '0123456789':
            j += 1
        if j < len(cox_str_suffix) and cox_str_suffix[j] == '/':
            j += 1
            while j < len(cox_str_suffix) and cox_str_suffix[j] in '0123456789':
                j += 1
        next = CDToken('branch', cox_str_suffix[:j])
        rest = cox_str_suffix[j:]
        return (next, rest)
    if cox_str_suffix[0] == ' ':
        j = 1
        while j < len(cox_str_suffix) and cox_str_suffix[j] == ' ':
            j += 1
        next = CDToken('space', ' ') # the token is just one space even if the user entered multiple ones
        rest = cox_str_suffix[j:]
        return (next, rest)

def cox_str_to_tokens(cox_str):
    prev_tokens = []
    cox_str_suffix = cox_str
    while cox_str_suffix != '':
        next, cox_str_suffix = next_token(cox_str_suffix, prev_tokens)
        prev_tokens.append(next)
    return prev_tokens

# ...
# next step would be numbering the nodes and making a list of edges between nodes that have been marked as branches

# returns a list mapping indices/serial numbers of nodes to locations in the token list
def get_node_locations(tokens):
    return [i for i, tok in enumerate(tokens) if tok.type == 'node']

# finds the index described by a virtual node token
def decode_virtual_node(vn_token):
    if vn_token.content[0] == '*' and len(vn_token.content) == 2:
        return 'abcdefghijklmnopqrstuvwxyz'.index(vn_token.content[1:])

# in this function, the edge set returned uses the serial numbers of the nodes
def tokens_to_edge_list(tokens, node_locations):
    edges = set()
    for pos, token in enumerate(tokens):
        if pos < len(tokens) - 2 and token.type in {'node', 'virtualnode'} and tokens[pos + 2].type in {'node', 'virtualnode'} and tokens[pos + 1].type in {'branch'}:
            if token.type == 'node':
                node1 = node_locations.index(pos)
            else:
                node1 = decode_virtual_node(token)
            if tokens[pos + 2].type == 'node':
                node2 = node_locations.index(pos + 2)
            else:
                node2 = decode_virtual_node(tokens[pos + 2])
            branch_label = tokens[pos + 1].content
            edge = ((node1, node2), branch_label)
            edges.add(edge)
    return edges

# actually makes the Coxeter matrix (adjacency matrix form of the Coxeter-Dynkin diagram)
# entries are stored in Fraction format, not as strings because we want non-reduced fractions to be equivalent to reduced fractions
# as far as I know, we won't actually be doing arithmetic on these fractions, but we will be checking their numerators to find our field extension
# dinkum
def edges_to_coxeter_matrix(edges, dim):
    coxeter_mat = [[F(2)]*dim for i in range(dim)]
    # set entries along the diagonal to 1
    for i in range(dim):
        coxeter_mat[i][i] = F(1)
    for verts, label in edges:
        v1, v2 = verts
        coxeter_mat[v1][v2] = F(label)
        coxeter_mat[v2][v1] = F(label)
    return coxeter_mat

# The final unified function. Converts a textual Coxeter-Dynkin diagram represented as a string of text to a Coxeter matrix
def cox_str_to_coxeter_matrix(cox_str):
    tokens = cox_str_to_tokens(cox_str)
    node_locations = get_node_locations(tokens)
    edges = tokens_to_edge_list(tokens, node_locations)
    dim = len(node_locations)
    return edges_to_coxeter_matrix(edges, dim)

def to_virtual_node(node_index):
    if node_index >= 26:
        raise RuntimeError("Not yet able to create Coxeter diagrams with more than 26 nodes due to virtual node constraints.")
    content = '*' + 'abcdefghijklmnopqrstuvwxyz'[node_index]
    return CDToken('virtualnode', content)

# Creates a list of tokens for a textual diagram from a Coxeter matrix with a specified order of the vertices
# Soon I plan to write a program to find a "canonical" node order that gets translated to an especially aethetically pleasing Coxeter diagram.
# order is a list mapping indices in the matrix to ranks in the specific order
# Let me see. By default, go through the nodes one by one in the order provided. But only when there's a non-2 branch (hereafter called a branch)
# between every consecutive pair. When there's not a branch to the next one, check if there's a branch back to an earlier one and add.
# ~~Then start at the first node that has another branch to a future node. Follow that path as long as you can, choosing the earliest node at each time.~~
# I changed my mind. Find the earliest visited node A that is connected to the earliest unvisited note B. Then follow the path A, B, B + 1, ... as long as you can.
# If such a node A doesn't exist, just start from node B and follow.
# Every time you reach a node with no branch to the next larger node, check to see if there's a branch back to an earlier node and follow the earliest such branch.
# If there isn't, just skip this step.
# Repeat this process until all nodes are mentioned - they will be mentioned in the specified order.
# Then go through the remaining branches in order of the rank of their larger node first, and then their smaller node.
# To do: I have to add spaces to the CD.
def coxeter_matrix_to_tokens_with_order(coxeter_matrix, order=None):
    n = len(coxeter_matrix)

    if order == None:
        order = list(range(n)) # default order is the one provided in the matrix

    # initialize matrix of which branches are visited in the textual diagram
    visited = init_matrix(n, n, False)
    # mark all 2-branches as visited, and diagonal entries (which don't represent branches)
    for i in range(n):
        for j in range(n):
            if coxeter_matrix[i][j] in {1, 2}:
                visited[i][j] = True
    # the goal is to visit every entry of the matrix

    i = 0
    node_token = CDToken('node', 'o')
    tokens = [node_token]
    # add first path through neighboring vertices, as long as it can be
    while True:
        if i < n - 1: # otherwise there's no next index to connect to
            label = coxeter_matrix[order.index(i)][order.index(i + 1)]
            if label != 2:
                # add an edge
                tokens.append(CDToken('branch', str(label)))
                tokens.append(node_token)
                visited[order.index(i)][order.index(i + 1)] = True
                visited[order.index(i + 1)][order.index(i)] = True
        if i == n - 1 or coxeter_matrix[order.index(i)][order.index(i + 1)] == 2:
            # look for an edge back to an earlier vertex, then break
            for j in range(i - 1):
                label = coxeter_matrix[order.index(j)][order.index(i)]
                if label != 2:
                    tokens.append(CDToken('branch', str(label)))
                    tokens.append(to_virtual_node(j)) # I still need to define this function
                    visited[order.index(j)][order.index(i)] = True
                    visited[order.index(i)][order.index(j)] = True
                    break
            break
        i += 1
    # now i has the value of the last node of the path
    # go through all the rest of the nodes making the maximum length chains between neighboring nodes
    while i < n - 1:
        tokens.append(CDToken('space', ' ')) # put a space token between two "disconnected" parts of the textual diagram
        i += 1 # go to beginning of next path
        # first try to find a branch from an earlier node to the current node before beginning the path
        for j in range(i - 1): # no node from i-1 to i, so we can leave i-1 out of the range
            label = coxeter_matrix[order.index(j)][order.index(i)]
            if label != 2:
                # add an edge
                tokens.append(to_virtual_node(j))
                tokens.append(CDToken('branch', str(label)))
                visited[order.index(j)][order.index(i)] = True
                visited[order.index(i)][order.index(j)] = True
                break
        # now start the path
        tokens.append(node_token)
        while True:
            if i < n - 1: # otherwise there's no next index to connect to
                label = coxeter_matrix[order.index(i)][order.index(i + 1)]
                if label != 2:
                    # add an edge
                    tokens.append(CDToken('branch', str(label)))
                    tokens.append(node_token)
                    visited[order.index(i)][order.index(i + 1)] = True
                    visited[order.index(i + 1)][order.index(i)] = True
            if i == n - 1 or coxeter_matrix[order.index(i)][order.index(i + 1)] == 2:
                # look for an edge back to an earlier vertex, then break
                for j in range(i - 1):
                    label = coxeter_matrix[order.index(j)][order.index(i)]
                    if label != 2 and not visited[order.index(j)][order.index(i)]:
                        tokens.append(CDToken('branch', str(label)))
                        tokens.append(to_virtual_node(j)) # I still need to define this function
                        visited[order.index(j)][order.index(i)] = True
                        visited[order.index(i)][order.index(j)] = True
                        break
                break
            i += 1
    # finally, add the remaining edges
    for i in range(n):
        for j in range(i):
            if not visited[order.index(j)][order.index(i)]:
                label = coxeter_matrix[order.index(j)][order.index(i)]
                tokens.append(CDToken('space', ' ')) # every remaining edge is a separate "component" of the textual diagram
                tokens.append(to_virtual_node(j))
                tokens.append(CDToken('branch', str(label)))
                tokens.append(to_virtual_node(i))
                visited[order.index(j)][order.index(i)] = True
                visited[order.index(i)][order.index(j)] = True
    return tokens
    # finished!

def tokens_to_cox_str(tokens):
    return ''.join(token.content for token in tokens)

# Final unified reverse function: converts a Coxeter matrix back into a Coxeter-Dynkin diagram
# Now with canonical ordering as the default!
def coxeter_matrix_to_cox_str(coxeter_matrix, order=None):
    if order == None:
        inv_order = canonical_ordering(coxeter_matrix)
        # Except the format of the order vector in the target function is reversed.
        # In canonical_ordering, the values represent ranks in the matrix and indices represent positions in the ordering.
        # In coxeter_matrix_to_tokens_with_order, the values represent positions in the ordering and the indices represent ranks in the matrix.
        # So we need to "invert" the ordering
        order = [0]*len(inv_order)
        for i, j in enumerate(inv_order):
            order[j] = i
    return tokens_to_cox_str(coxeter_matrix_to_tokens_with_order(coxeter_matrix, order))

# Now for a new test: Making a canonizer of Coxeter diagrams.
# This finds a single canonical form for any Coxeter matrix based on re-ordering the columns. The primary goal is simplicity. The secondary goal is that feeding a canonical Coxeter matrix into the above coxeter_matrix_to_cox_str function produces a nice-looking, relatively unfragmented diagram.
# Okay, maybe the first and second goals should be reversed.

# returns a list of the longest paths of (non-2) edges in a CD given a Coxeter matrix, with the paths given as lists of vertex indices.
# and also returns the longest path length
# Really, this should work with any adjacency matrix of an undirected graph.
def longest_paths(coxeter_matrix):
    n = len(coxeter_matrix)
    # use an intermediate recursive function storing (as an argument) the list of record breaking paths, the length, and the list of previously seen vertices.
    # hm, I suppose I could make this more efficient by only updating record_path and record_length when I reach a dead end; i.e. when len(unseen_neighbors) == 0
    # in that case, record_paths and record_length would represent the longest *complete* path found
    def helper_fn(record_paths, record_length, prev_verts):
        # if we've seen previous vertices, only look at the neighbors of the last one
        if len(prev_verts) > 0:
            i = prev_verts[-1]
            unseen_neighbors = [j for j in range(n) if coxeter_matrix[i][j] != 2 and j not in prev_verts]
        # otherwise, look at all vertices
        else:
            unseen_neighbors = list(range(n))
        if len(unseen_neighbors) == 0:
            return record_paths, record_length # I'm not sure what we should return yet
        # update running tally of record path(s)
        for j in unseen_neighbors:
            new_path = prev_verts + [j]
            # tied for longest path
            if len(new_path) == record_length:
                record_paths.append(new_path)
            # new longer path
            elif len(new_path) > record_length:
                record_paths = [new_path]
                record_length = len(new_path)
            # recurse on neighbor node to find longer paths
            record_paths, record_length = helper_fn(record_paths, record_length, new_path)
        return record_paths, record_length
    return helper_fn([], 0, [])

# I think this also works when long_paths is just an arbitrary list of lists of vertices.
# Given a list of paths through coxeter_matrix, finds the subset of those paths with the earliest connection to a node off the path, and returns a new list of the paths plus the new nodes.
def paths_with_earliest_node_to_next_vertex(coxeter_matrix, long_paths):
    n = len(coxeter_matrix)
    earliest_connection = float('inf') # earliest connection to another vertex that's been found so far, given by its position along the path, not its index in the matrix
    new_partial_orderings = [] # orderings of a subset of the vertices created by taking the paths in long_paths and adding the vertices from the record-breaking earliest vertex connections to them
    for path in long_paths:
        for pathind, i in enumerate(path):
            if pathind > earliest_connection: break
            # check if node i has neighbors not in the path
            i_neighbors = [j for j in range(n) if coxeter_matrix[i][j] != 2 and j not in path]
            if len(i_neighbors) > 0: # found some new neighbors
                if pathind < earliest_connection:
                    earliest_connection = pathind
                    new_partial_orderings = [] # reset the list as new earliest connection position has been found
                for i_neighbor in i_neighbors:
                    new_partial_orderings.append(path + [i_neighbor])
    return new_partial_orderings, earliest_connection

# Finds a canonical ordering of the vertices for any Coxeter-Dynkin diagram, encoded as a Coxeter matrix
# Any two matrices that represent the same Coxeter diagram convert into the same matrix when their columns and rows are reordered in the canonical order.
# Here's the idea:
# We keep a list of lists of vertices (as indices) that are candidate prefixes for the canonical ordering.
# For each candidate we also keep a list of edges in the order they were visited. (Edit: Actually if we store the edges using indices into each vertex list, we just need to store one list.)
# We start with the lists of indices from each of the longest paths through the CD and the edges of the path.
# We look at the lists from that set, that hold the record for earliest node on the path that branches to a node off the path. We only keep those lists and add the branching node to the end of each of them. If there are multiple branching nodes connecting to the same list node, we make a separate list for each of them.
# We repeat this process, looking for the earliest node in each list that connects to a node not in the list, only keeping the lists for which this connection appears the earliest, and adding the latter node to the end of the list.
# We continue this way until we've found all the nodes. If we can't find all the nodes this way, the graph is disconnected and we have a separate way to deal with it.
# If there are still multiple orderings left, we go through all unvisited edges one by one (i,j), where i,j are indices of an ordering list (the actual indices of the matrix are different) like (0,1), (0,2), (1,2), (0,3), (1,3), etc. If any index pair (i,j) is an actual edge in some ordering, we delete the orderings for which it's not an edge and continue.
# If, at the end of this process, there are still multiple orderings, the shape of the graph (excluding labels) is symmetric and each ordering represents a symmetry. Notice that at each step, the partial graphs made from the vertices and edges seen so far in each list were isomorphic.
# Go through the edges of each ordering (in parallel) and at any step, if the edges have different labels, throw out all orders except the ones where the label ranks latest in this list: 3/2, 3, 4/3, 4, 5/4, 5/3, 5/2, 5, ...
# If there are STILL multiple orderings to choose from, then the graph including labels is symmetric and each ordering is a symmetry. Choose one ordering arbitrarily.
def canonical_ordering(coxeter_matrix):
    n_edges = sum([len([p for p in row if p not in {1,2}]) for row in coxeter_matrix])//2 # because we want to check whether we've included all edges
    n = len(coxeter_matrix)
    vertex_orders, order_length = longest_paths(coxeter_matrix)
    edge_order = [(i, i+1) for i in range(order_length - 1)]
    while order_length < n:
        vertex_orders, connect_ind = paths_with_earliest_node_to_next_vertex(coxeter_matrix, vertex_orders)
        if vertex_orders == []:
            # it means graph is disconnected because we failed to find a connection between our subgraph and the rest of the graph
            return None
        order_length += 1
        edge_order.append((connect_ind, order_length - 1))
    # if there's just one vertex permutation left, we can return early (but we don't have to)
    if len(vertex_orders) == 1:
        return vertex_orders[0]
    # now compare the missing edges in each vertex ordering
    i = 0
    j = 1
    while len(edge_order) < n_edges:
        if (i, j) not in edge_order:
            # check whether (i,j) is an edge under each vertex order
            edge_appears = any([coxeter_matrix[order[i]][order[j]] not in {1,2} for order in vertex_orders])
            if edge_appears:
                # delete all the orders where the edge doesn't appear
                vertex_orders = [order for order in vertex_orders if coxeter_matrix[order[i]][order[j]] not in {1,2}]
                edge_order.append((i, j))
            # if there's just one vertex permutation left, we can return early (but we don't have to)
            if len(vertex_orders) == 1:
                return vertex_orders[0]
        # move to the next i, j value
        i += 1
        if i == j:
            i = 0
            j += 1
        if j == n:
            # We shouldn't get here; edge_order should have covered all the edges by now. But in case it miscounts...
            print("You should never see this message.")
            break
    # now go through all the labels in each of the permutations in the edge order given and choose only permutations that have the "largest" label
    for i, j in edge_order:
        labels = [coxeter_matrix[order[i]][order[j]] for order in vertex_orders]
        best_label = F(3,2)
        for label in labels:
            label = F(label) # convert label to Fraction form so we can take numerator and denominator
            if label.numerator > best_label.numerator or label.numerator == best_label.numerator and label.denominator < best_label.denominator:
                best_label = label
        vertex_orders = [order for order in vertex_orders if coxeter_matrix[order[i]][order[j]] == best_label]
        # if there's just one vertex permutation left, we can return early (but we don't have to)
        if len(vertex_orders) == 1:
            return vertex_orders[0]
    return vertex_orders[0]

def check_connectivity(cox_mat):
    def DFS(i, visited):
        neighbors = [j for j, label in enumerate(cox_mat[i]) if label not in {1,2}]
        visited[i] = True
        for j in neighbors:
            if visited[j]: continue
            visited = DFS(j, visited)
        return visited
    n = len(cox_mat)
    return DFS(0, [False]*n) == [True]*n

# uncomment each of these tests to use them
'''# test it on a square cyclic graph
M = \
[[1,3,2,3],
 [3,1,3,2],
 [2,3,1,3],
 [3,2,3,1]]'''
'''# E(6) diagram
M = \
[[1,3,2,2,2,2],
 [3,1,3,2,2,2],
 [2,3,1,3,2,3],
 [2,2,3,1,3,2],
 [2,2,2,3,1,2],
 [2,2,3,2,2,1]]'''
'''# E(6) with an extra node connected to node 2
M = \
[[1,3,2,2,2,2,2],
 [3,1,3,2,2,2,3],
 [2,3,1,3,2,3,2],
 [2,2,3,1,3,2,2],
 [2,2,2,3,1,2,2],
 [2,2,3,2,2,1,2],
 [2,3,2,2,2,2,1]]'''
'''# Q(7)
M = \
[[1,3,2,2,2,2,2],
 [3,1,3,2,2,2,3],
 [2,3,1,3,2,2,2],
 [2,2,3,1,3,3,2],
 [2,2,2,3,1,2,2],
 [2,2,2,3,2,1,2],
 [2,3,2,2,2,2,1]]'''
'''# Q(6) with extra edge, as
# 0|   /3
# | 1-2
# 4/   |5
# (extra edge is between 0 and 4)
# At first, the paths found should be:
# 0,4,1,2,3 and 3,2,1,4,0
# 4,0,1,2,3 and 3,2,1,0,4
# 0,4,1,2,5 and 5,2,1,4,0
# 4,0,1,2,5 and 5,2,1,0,4
# Then the last edge to make a full spanning tree is either (2,3) or (2,5) and so we should be left with the cases where node 2 is at index 1:
# 3,2,1,4,0,5
# 3,2,1,0,4,5
# 5,2,1,4,0,3
# 5,2,1,0,4,3
M = \
[[1,3,2,2,3,2],
 [3,1,3,2,3,2],
 [2,3,1,3,2,3],
 [2,2,3,1,2,2],
 [3,3,2,2,1,2],
 [2,2,3,2,2,1]]'''
'''# 4D cogeo diagram
#  0-3-2-3-3
#4/3| /4
#    1
M = \
[[1,F(4,3),3,2],
 [F(4,3),1,4,2],
 [3,4,1,3],
 [2,2,3,1]]'''
'''print(longest_paths(M))
print(paths_with_earliest_node_to_next_vertex(M, longest_paths(M)[0]))
print(canonical_ordering(M))'''