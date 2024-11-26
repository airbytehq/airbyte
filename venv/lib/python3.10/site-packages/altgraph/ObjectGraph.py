"""
altgraph.ObjectGraph - Graph of objects with an identifier
==========================================================

A graph of objects that have a "graphident" attribute.
graphident is the key for the object in the graph
"""

from altgraph import GraphError
from altgraph.Graph import Graph
from altgraph.GraphUtil import filter_stack


class ObjectGraph(object):
    """
    A graph of objects that have a "graphident" attribute.
    graphident is the key for the object in the graph
    """

    def __init__(self, graph=None, debug=0):
        if graph is None:
            graph = Graph()
        self.graphident = self
        self.graph = graph
        self.debug = debug
        self.indent = 0
        graph.add_node(self, None)

    def __repr__(self):
        return "<%s>" % (type(self).__name__,)

    def flatten(self, condition=None, start=None):
        """
        Iterate over the subgraph that is entirely reachable by condition
        starting from the given start node or the ObjectGraph root
        """
        if start is None:
            start = self
        start = self.getRawIdent(start)
        return self.graph.iterdata(start=start, condition=condition)

    def nodes(self):
        for ident in self.graph:
            node = self.graph.node_data(ident)
            if node is not None:
                yield self.graph.node_data(ident)

    def get_edges(self, node):
        if node is None:
            node = self
        start = self.getRawIdent(node)
        _, _, outraw, incraw = self.graph.describe_node(start)

        def iter_edges(lst, n):
            seen = set()
            for tpl in (self.graph.describe_edge(e) for e in lst):
                ident = tpl[n]
                if ident not in seen:
                    yield self.findNode(ident)
                    seen.add(ident)

        return iter_edges(outraw, 3), iter_edges(incraw, 2)

    def edgeData(self, fromNode, toNode):
        if fromNode is None:
            fromNode = self
        start = self.getRawIdent(fromNode)
        stop = self.getRawIdent(toNode)
        edge = self.graph.edge_by_node(start, stop)
        return self.graph.edge_data(edge)

    def updateEdgeData(self, fromNode, toNode, edgeData):
        if fromNode is None:
            fromNode = self
        start = self.getRawIdent(fromNode)
        stop = self.getRawIdent(toNode)
        edge = self.graph.edge_by_node(start, stop)
        self.graph.update_edge_data(edge, edgeData)

    def filterStack(self, filters):
        """
        Filter the ObjectGraph in-place by removing all edges to nodes that
        do not match every filter in the given filter list

        Returns a tuple containing the number of:
            (nodes_visited, nodes_removed, nodes_orphaned)
        """
        visited, removes, orphans = filter_stack(self.graph, self, filters)

        for last_good, tail in orphans:
            self.graph.add_edge(last_good, tail, edge_data="orphan")

        for node in removes:
            self.graph.hide_node(node)

        return len(visited) - 1, len(removes), len(orphans)

    def removeNode(self, node):
        """
        Remove the given node from the graph if it exists
        """
        ident = self.getIdent(node)
        if ident is not None:
            self.graph.hide_node(ident)

    def removeReference(self, fromnode, tonode):
        """
        Remove all edges from fromnode to tonode
        """
        if fromnode is None:
            fromnode = self
        fromident = self.getIdent(fromnode)
        toident = self.getIdent(tonode)
        if fromident is not None and toident is not None:
            while True:
                edge = self.graph.edge_by_node(fromident, toident)
                if edge is None:
                    break
                self.graph.hide_edge(edge)

    def getIdent(self, node):
        """
        Get the graph identifier for a node
        """
        ident = self.getRawIdent(node)
        if ident is not None:
            return ident
        node = self.findNode(node)
        if node is None:
            return None
        return node.graphident

    def getRawIdent(self, node):
        """
        Get the identifier for a node object
        """
        if node is self:
            return node
        ident = getattr(node, "graphident", None)
        return ident

    def __contains__(self, node):
        return self.findNode(node) is not None

    def findNode(self, node):
        """
        Find the node on the graph
        """
        ident = self.getRawIdent(node)
        if ident is None:
            ident = node
        try:
            return self.graph.node_data(ident)
        except KeyError:
            return None

    def addNode(self, node):
        """
        Add a node to the graph referenced by the root
        """
        self.msg(4, "addNode", node)

        try:
            self.graph.restore_node(node.graphident)
        except GraphError:
            self.graph.add_node(node.graphident, node)

    def createReference(self, fromnode, tonode, edge_data=None):
        """
        Create a reference from fromnode to tonode
        """
        if fromnode is None:
            fromnode = self
        fromident, toident = self.getIdent(fromnode), self.getIdent(tonode)
        if fromident is None or toident is None:
            return
        self.msg(4, "createReference", fromnode, tonode, edge_data)
        self.graph.add_edge(fromident, toident, edge_data=edge_data)

    def createNode(self, cls, name, *args, **kw):
        """
        Add a node of type cls to the graph if it does not already exist
        by the given name
        """
        m = self.findNode(name)
        if m is None:
            m = cls(name, *args, **kw)
            self.addNode(m)
        return m

    def msg(self, level, s, *args):
        """
        Print a debug message with the given level
        """
        if s and level <= self.debug:
            print("%s%s %s" % ("  " * self.indent, s, " ".join(map(repr, args))))

    def msgin(self, level, s, *args):
        """
        Print a debug message and indent
        """
        if level <= self.debug:
            self.msg(level, s, *args)
            self.indent = self.indent + 1

    def msgout(self, level, s, *args):
        """
        Dedent and print a debug message
        """
        if level <= self.debug:
            self.indent = self.indent - 1
            self.msg(level, s, *args)
