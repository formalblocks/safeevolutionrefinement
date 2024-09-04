from itertools import chain, combinations

def powerset(iterable):
    """
    Adapted from https://high-python-ext-3-algorithms.readthedocs.io/ko/latest/chapter18.html#set-covering

    Calculate the powerset of any iterable.

    For a range of integers up to the length of the given list,
    make all possible combinations and chain them together as one object.
    From https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    "list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def optimal_set_cover(universe, subsets, costs=None):
    """ 
    Adapted from https://high-python-ext-3-algorithms.readthedocs.io/ko/latest/chapter18.html#set-covering

    Optimal algorithm - DONT USE ON BIG INPUTS - O(2^n) complexity!
    Finds the minimum cost subcollection os S that covers all elements of U

    Args:
        universe (list): Universe of elements
        subsets (dict): Subsets of U {S1:elements,S2:elements}
        costs (dict): Costs of each subset in S - {S1:cost, S2:cost...}
    """
    if not costs:
        costs = {x: 1 for x in subsets.keys()}

    pset = powerset(subsets.keys())
    best_set = None
    best_cost = float("inf")
    for subset in pset:
        covered = set()
        cost = 0
        for s in subset:
            covered.update(subsets[s])
            cost += costs[s]
        if len(covered) == len(universe) and cost < best_cost:
            best_set = subset
            best_cost = cost
    return best_set

universe = {1, 2, 3, 4, 5}
subsets = {'S1': {4, 1, 3}, 'S2': {2, 5}, 'S3': {1, 4, 3, 2}}

optimal_cover = optimal_set_cover(universe, subsets)
print(optimal_cover)