"""
altgraph.GraphAlgo - Graph algorithms
=====================================
"""
from altgraph import GraphError


def dijkstra(graph, start, end=None):
    """
    Dijkstra's algorithm for shortest paths

    `David Eppstein, UC Irvine, 4 April 2002
        <http://www.ics.uci.edu/~eppstein/161/python/>`_

    `Python Cookbook Recipe
        <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466>`_

    Find shortest paths from the  start node to all nodes nearer than or
    equal to the end node.

    Dijkstra's algorithm is only guaranteed to work correctly when all edge
    lengths are positive.  This code does not verify this property for all
    edges (only the edges examined until the end vertex is reached), but will
    correctly compute shortest paths even for some graphs with negative edges,
    and will raise an exception if it discovers that a negative edge has
    caused it to make a mistake.

    Adapted to altgraph by Istvan Albert, Pennsylvania State University -
    June, 9 2004
    """
    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors
    Q = _priorityDictionary()  # estimated distances of non-final vertices
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end:
            break

        for w in graph.out_nbrs(v):
            edge_id = graph.edge_by_node(v, w)
            vwLength = D[v] + graph.edge_data(edge_id)
            if w in D:
                if vwLength < D[w]:
                    raise GraphError(
                        "Dijkstra: found better path to already-final vertex"
                    )
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return (D, P)


def shortest_path(graph, start, end):
    """
    Find a single shortest path from the *start* node to the *end* node.
    The input has the same conventions as dijkstra(). The output is a list of
    the nodes in order along the shortest path.

    **Note that the distances must be stored in the edge data as numeric data**
    """

    D, P = dijkstra(graph, start, end)
    Path = []
    while 1:
        Path.append(end)
        if end == start:
            break
        end = P[end]
    Path.reverse()
    return Path


#
# Utility classes and functions
#
class _priorityDictionary(dict):
    """
    Priority dictionary using binary heaps (internal use only)

    David Eppstein, UC Irvine, 8 Mar 2002

    Implements a data structure that acts almost like a dictionary, with
    two modifications:

        1. D.smallest() returns the value x minimizing D[x].  For this to
           work correctly, all values D[x] stored in the dictionary must be
           comparable.

        2. iterating "for x in D" finds and removes the items from D in sorted
           order. Each item is not removed until the next item is requested,
           so D[x] will still return a useful value until the next iteration
           of the for-loop.  Each operation takes logarithmic amortized time.
    """

    def __init__(self):
        """
        Initialize priorityDictionary by creating binary heap of pairs
        (value,key).  Note that changing or removing a dict entry will not
        remove the old pair from the heap until it is found by smallest()
        or until the heap is rebuilt.
        """
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        """
        Find smallest item after removing deleted items from front of heap.
        """
        if len(self) == 0:
            raise IndexError("smallest of empty priorityDictionary")
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2 * insertionPoint + 1
                if (
                    smallChild + 1 < len(heap)
                    and heap[smallChild] > heap[smallChild + 1]
                ):
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]

    def __iter__(self):
        """
        Create destructive sorted iterator of priorityDictionary.
        """

        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]

        return iterfn()

    def __setitem__(self, key, val):
        """
        Change value stored in dictionary and add corresponding pair to heap.
        Rebuilds the heap if the number of deleted items gets large, to avoid
        memory leakage.
        """
        dict.__setitem__(self, key, val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v, k) for k, v in self.items()]
            self.__heap.sort()
        else:
            newPair = (val, key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and newPair < heap[(insertionPoint - 1) // 2]:
                heap[insertionPoint] = heap[(insertionPoint - 1) // 2]
                insertionPoint = (insertionPoint - 1) // 2
            heap[insertionPoint] = newPair

    def setdefault(self, key, val):
        """
        Reimplement setdefault to pass through our customized __setitem__.
        """
        if key not in self:
            self[key] = val
        return self[key]
