"""
altgraph - a python graph library
=================================

altgraph is a fork of `graphlib <http://pygraphlib.sourceforge.net>`_ tailored
to use newer Python 2.3+ features, including additional support used by the
py2app suite (modulegraph and macholib, specifically).

altgraph is a python based graph (network) representation and manipulation
package.  It has started out as an extension to the
`graph_lib module
<http://www.ece.arizona.edu/~denny/python_nest/graph_lib_1.0.1.html>`_
written by Nathan Denny it has been significantly optimized and expanded.

The :class:`altgraph.Graph.Graph` class is loosely modeled after the
`LEDA <http://www.algorithmic-solutions.com/enleda.htm>`_
(Library of Efficient Datatypes) representation. The library
includes methods for constructing graphs, BFS and DFS traversals,
topological sort, finding connected components, shortest paths as well as a
number graph statistics functions. The library can also visualize graphs
via `graphviz <http://www.research.att.com/sw/tools/graphviz/>`_.

The package contains the following modules:

    -  the :py:mod:`altgraph.Graph` module contains the
       :class:`~altgraph.Graph.Graph` class that stores the graph data

    -  the :py:mod:`altgraph.GraphAlgo` module implements graph algorithms
       operating on graphs (:py:class:`~altgraph.Graph.Graph`} instances)

    -  the :py:mod:`altgraph.GraphStat` module contains functions for
       computing statistical measures on graphs

    -  the :py:mod:`altgraph.GraphUtil` module contains functions for
       generating, reading and saving graphs

    -  the :py:mod:`altgraph.Dot` module  contains functions for displaying
       graphs via `graphviz <http://www.research.att.com/sw/tools/graphviz/>`_

    -  the :py:mod:`altgraph.ObjectGraph` module implements a graph of
       objects with a unique identifier

Installation
------------

Download and unpack the archive then type::

    python setup.py install

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of::

    python setup.py --help install

To verify that the code works run the test suite::

    python setup.py test

Example usage
-------------

Lets assume that we want to analyze the graph below (links to the full picture)
GRAPH_IMG.  Our script then might look the following way::

    from altgraph import Graph, GraphAlgo, Dot

    # these are the edges
    edges = [ (1,2), (2,4), (1,3), (2,4), (3,4), (4,5), (6,5),
        (6,14), (14,15), (6, 15),  (5,7), (7, 8), (7,13), (12,8),
        (8,13), (11,12), (11,9), (13,11), (9,13), (13,10) ]

    # creates the graph
    graph = Graph.Graph()
    for head, tail in edges:
        graph.add_edge(head, tail)

    # do a forward bfs from 1 at most to 20
    print(graph.forw_bfs(1))

This will print the nodes in some breadth first order::

    [1, 2, 3, 4, 5, 7, 8, 13, 11, 10, 12, 9]

If we wanted to get the hop-distance from node 1 to node 8
we coud write::

    print(graph.get_hops(1, 8))

This will print the following::

    [(1, 0), (2, 1), (3, 1), (4, 2), (5, 3), (7, 4), (8, 5)]

Node 1 is at 0 hops since it is the starting node, nodes 2,3 are 1 hop away ...
node 8 is 5 hops away. To find the shortest distance between two nodes you
can use::

    print(GraphAlgo.shortest_path(graph, 1, 12))

It will print the nodes on one (if there are more) the shortest paths::

    [1, 2, 4, 5, 7, 13, 11, 12]

To display the graph we can use the GraphViz backend::

    dot = Dot.Dot(graph)

    # display the graph on the monitor
    dot.display()

    # save it in an image file
    dot.save_img(file_name='graph', file_type='gif')



..
  @author: U{Istvan Albert<http://www.personal.psu.edu/staff/i/u/iua1/>}

  @license:  MIT License

  Copyright (c) 2004 Istvan Albert unless otherwise noted.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to
  deal in the Software without restriction, including without limitation the
  rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
  IN THE SOFTWARE.
  @requires: Python 2.3 or higher

  @newfield contributor: Contributors:
  @contributor: U{Reka Albert <http://www.phys.psu.edu/~ralbert/>}

"""
import pkg_resources

__version__ = pkg_resources.require("altgraph")[0].version


class GraphError(ValueError):
    pass
