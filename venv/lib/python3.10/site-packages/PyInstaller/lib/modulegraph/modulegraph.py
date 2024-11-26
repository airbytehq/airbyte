"""
Find modules used by a script, using bytecode analysis.

Based on the stdlib modulefinder by Thomas Heller and Just van Rossum,
but uses a graph data structure and 2.3 features

XXX: Verify all calls to _import_hook (and variants) to ensure that
imports are done in the right way.
"""
#FIXME: To decrease the likelihood of ModuleGraph exceeding the recursion limit
#and hence unpredictably raising fatal exceptions, increase the recursion
#limit at PyInstaller startup (i.e., in the
#PyInstaller.building.build_main.build() function). For details, see:
#    https://github.com/pyinstaller/pyinstaller/issues/1919#issuecomment-216016176

import ast
import os
import pkgutil
import sys
import re
from collections import deque, namedtuple, defaultdict
import urllib.request
import warnings
import importlib.util
import importlib.machinery

# The logic in PyInstaller.compat ensures that these are available and
# of correct version.
if sys.version_info >= (3, 10):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

from altgraph.ObjectGraph import ObjectGraph
from altgraph import GraphError

from . import util


class BUILTIN_MODULE:
    def is_package(fqname):
        return False


class NAMESPACE_PACKAGE:
    def __init__(self, namespace_dirs):
        self.namespace_dirs = namespace_dirs

    def is_package(self, fqname):
        return True


#FIXME: Leverage this rather than magic numbers below.
ABSOLUTE_OR_RELATIVE_IMPORT_LEVEL = -1
"""
Constant instructing the builtin `__import__()` function to attempt both
absolute and relative imports.
"""


#FIXME: Leverage this rather than magic numbers below.
ABSOLUTE_IMPORT_LEVEL = 0
"""
Constant instructing the builtin `__import__()` function to attempt only
absolute imports.
"""


#FIXME: Leverage this rather than magic numbers below.
DEFAULT_IMPORT_LEVEL = ABSOLUTE_IMPORT_LEVEL
"""
Constant instructing the builtin `__import__()` function to attempt the default
import style specific to the active Python interpreter.

Specifically, under:

* Python 2, this defaults to attempting both absolute and relative imports.
* Python 3, this defaults to attempting only absolute imports.
"""


class InvalidRelativeImportError (ImportError):
    pass


def _path_from_importerror(exc, default):
    # This is a hack, but sadly enough the necessary information
    # isn't available otherwise.
    m = re.match(r'^No module named (\S+)$', str(exc))
    if m is not None:
        return m.group(1)

    return default


#FIXME: What is this? Do we actually need this? This appears to provide
#significantly more fine-grained metadata than PyInstaller will ever require.
#It consumes a great deal of space (slots or no slots), since we store an
#instance of this class for each edge of the graph.
class DependencyInfo (namedtuple("DependencyInfo",
                      ["conditional", "function", "tryexcept", "fromlist"])):
    __slots__ = ()

    def _merged(self, other):
        if (not self.conditional and not self.function and not self.tryexcept) \
           or (not other.conditional and not other.function and not other.tryexcept):
            return DependencyInfo(
                conditional=False,
                function=False,
                tryexcept=False,
                fromlist=self.fromlist and other.fromlist)

        else:
            return DependencyInfo(
                    conditional=self.conditional or other.conditional,
                    function=self.function or other.function,
                    tryexcept=self.tryexcept or other.tryexcept,
                    fromlist=self.fromlist and other.fromlist)


#FIXME: Shift the following Node class hierarchy into a new
#"PyInstaller.lib.modulegraph.node" module. This module is much too long.
#FIXME: Refactor "_deferred_imports" from a tuple into a proper lightweight
#class leveraging "__slots__". If not for backward compatibility, we'd just
#leverage a named tuple -- but this should do just as well.
#FIXME: Move the "packagepath" attribute into the "Package" class. Only
#packages define the "__path__" special attribute. The codebase currently
#erroneously tests whether "module.packagepath is not None" to determine
#whether a node is a package or not. However, "isinstance(module, Package)" is
#a significantly more reliable test. Refactor the former into the latter.
class Node:
    """
    Abstract base class (ABC) of all objects added to a `ModuleGraph`.

    Attributes
    ----------
    code : codeobject
        Code object of the pure-Python module corresponding to this graph node
        if any _or_ `None` otherwise.
    graphident : str
        Synonym of `identifier` required by the `ObjectGraph` superclass of the
        `ModuleGraph` class. For readability, the `identifier` attribute should
        typically be used instead.
    filename : str
        Absolute path of this graph node's corresponding module, package, or C
        extension if any _or_ `None` otherwise.
    identifier : str
        Fully-qualified name of this graph node's corresponding module,
        package, or C extension.
    packagepath : str
        List of the absolute paths of all directories comprising this graph
        node's corresponding package. If this is a:
        * Non-namespace package, this list contains exactly one path.
        * Namespace package, this list contains one or more paths.
    _deferred_imports : list
        List of all target modules imported by the source module corresponding
        to this graph node whole importations have been deferred for subsequent
        processing in between calls to the `_ModuleGraph._scan_code()` and
        `_ModuleGraph._process_imports()` methods for this source module _or_
        `None` otherwise. Each element of this list is a 3-tuple
        `(have_star, _safe_import_hook_args, _safe_import_hook_kwargs)`
        collecting the importation of a target module from this source module
        for subsequent processing, where:
        * `have_star` is a boolean `True` only if this is a `from`-style star
          import (e.g., resembling `from {target_module_name} import *`).
        * `_safe_import_hook_args` is a (typically non-empty) sequence of all
          positional arguments to be passed to the `_safe_import_hook()` method
          to add this importation to the graph.
        * `_safe_import_hook_kwargs` is a (typically empty) dictionary of all
          keyword arguments to be passed to the `_safe_import_hook()` method
          to add this importation to the graph.
        Unlike functional languages, Python imposes a maximum depth on the
        interpreter stack (and hence recursion). On breaching this depth,
        Python raises a fatal `RuntimeError` exception. Since `ModuleGraph`
        parses imports recursively rather than iteratively, this depth _was_
        commonly breached before the introduction of this list. Python
        environments installing a large number of modules (e.g., Anaconda) were
        particularly susceptible. Why? Because `ModuleGraph` concurrently
        descended through both the abstract syntax trees (ASTs) of all source
        modules being parsed _and_ the graph of all target modules imported by
        these source modules being built. The stack thus consisted of
        alternating layers of AST and graph traversal. To unwind such
        alternation and effectively halve the stack depth, `ModuleGraph` now
        descends through the abstract syntax tree (AST) of each source module
        being parsed and adds all importations originating within this module
        to this list _before_ descending into the graph of these importations.
        See pyinstaller/pyinstaller/#1289 for further details.
    _global_attr_names : set
        Set of the unqualified names of all global attributes (e.g., classes,
        variables) defined in the pure-Python module corresponding to this
        graph node if any _or_ the empty set otherwise. This includes the names
        of all attributes imported via `from`-style star imports from other
        existing modules (e.g., `from {target_module_name} import *`). This
        set is principally used to differentiate the non-ignorable importation
        of non-existent submodules in a package from the ignorable importation
        of existing global attributes defined in that package's pure-Python
        `__init__` submodule in `from`-style imports (e.g., `bar` in
        `from foo import bar`, which may be either a submodule or attribute of
        `foo`), as such imports ambiguously allow both. This set is _not_ used
        to differentiate submodules from attributes in `import`-style imports
        (e.g., `bar` in `import foo.bar`, which _must_ be a submodule of
        `foo`), as such imports unambiguously allow only submodules.
    _starimported_ignored_module_names : set
        Set of the fully-qualified names of all existing unparsable modules
        that the existing parsable module corresponding to this graph node
        attempted to perform one or more "star imports" from. If this module
        either does _not_ exist or does but is unparsable, this is the empty
        set. Equivalently, this set contains each fully-qualified name
        `{trg_module_name}` for which:
        * This module contains an import statement of the form
          `from {trg_module_name} import *`.
        * The module whose name is `{trg_module_name}` exists but is _not_
          parsable by `ModuleGraph` (e.g., due to _not_ being pure-Python).
        **This set is currently defined but otherwise ignored.**
    _submodule_basename_to_node : dict
        Dictionary mapping from the unqualified name of each submodule
        contained by the parent module corresponding to this graph node to that
        submodule's graph node. If this dictionary is non-empty, this parent
        module is typically but _not_ always a package (e.g., the non-package
        `os` module containing the `os.path` submodule).
    """

    __slots__ = [
        'code',
        'filename',
        'graphident',
        'identifier',
        'packagepath',
        '_deferred_imports',
        '_global_attr_names',
        '_starimported_ignored_module_names',
        '_submodule_basename_to_node',
    ]

    def __init__(self, identifier):
        """
        Initialize this graph node.

        Parameters
        ----------
        identifier : str
            Fully-qualified name of this graph node's corresponding module,
            package, or C extension.
        """

        self.code = None
        self.filename = None
        self.graphident = identifier
        self.identifier = identifier
        self.packagepath = None
        self._deferred_imports = None
        self._global_attr_names = set()
        self._starimported_ignored_module_names = set()
        self._submodule_basename_to_node = dict()


    def is_global_attr(self, attr_name):
        """
        `True` only if the pure-Python module corresponding to this graph node
        defines a global attribute (e.g., class, variable) with the passed
        name.

        If this module is actually a package, this method instead returns
        `True` only if this package's pure-Python `__init__` submodule defines
        such a global attribute. In this case, note that this package may still
        contain an importable submodule of the same name. Callers should
        attempt to import this attribute as a submodule of this package
        _before_ assuming this attribute to be an ignorable global. See
        "Examples" below for further details.

        Parameters
        ----------
        attr_name : str
            Unqualified name of the attribute to be tested.

        Returns
        ----------
        bool
            `True` only if this module defines this global attribute.

        Examples
        ----------
        Consider a hypothetical module `foo` containing submodules `bar` and
        `__init__` where the latter assigns `bar` to be a global variable
        (possibly star-exported via the special `__all__` global variable):

        >>> # In "foo.__init__":
        >>> bar = 3.1415

        Python 2 and 3 both permissively permit this. This method returns
        `True` in this case (i.e., when called on the `foo` package's graph
        node, passed the attribute name `bar`) despite the importability of the
        `foo.bar` submodule.
        """

        return attr_name in self._global_attr_names


    def is_submodule(self, submodule_basename):
        """
        `True` only if the parent module corresponding to this graph node
        contains the submodule with the passed name.

        If `True`, this parent module is typically but _not_ always a package
        (e.g., the non-package `os` module containing the `os.path` submodule).

        Parameters
        ----------
        submodule_basename : str
            Unqualified name of the submodule to be tested.

        Returns
        ----------
        bool
            `True` only if this parent module contains this submodule.
        """

        return submodule_basename in self._submodule_basename_to_node


    def add_global_attr(self, attr_name):
        """
        Record the global attribute (e.g., class, variable) with the passed
        name to be defined by the pure-Python module corresponding to this
        graph node.

        If this module is actually a package, this method instead records this
        attribute to be defined by this package's pure-Python `__init__`
        submodule.

        Parameters
        ----------
        attr_name : str
            Unqualified name of the attribute to be added.
        """

        self._global_attr_names.add(attr_name)


    def add_global_attrs_from_module(self, target_module):
        """
        Record all global attributes (e.g., classes, variables) defined by the
        target module corresponding to the passed graph node to also be defined
        by the source module corresponding to this graph node.

        If the source module is actually a package, this method instead records
        these attributes to be defined by this package's pure-Python `__init__`
        submodule.

        Parameters
        ----------
        target_module : Node
            Graph node of the target module to import attributes from.
        """

        self._global_attr_names.update(target_module._global_attr_names)


    def add_submodule(self, submodule_basename, submodule_node):
        """
        Add the submodule with the passed name and previously imported graph
        node to the parent module corresponding to this graph node.

        This parent module is typically but _not_ always a package (e.g., the
        non-package `os` module containing the `os.path` submodule).

        Parameters
        ----------
        submodule_basename : str
            Unqualified name of the submodule to add to this parent module.
        submodule_node : Node
            Graph node of this submodule.
        """

        self._submodule_basename_to_node[submodule_basename] = submodule_node


    def get_submodule(self, submodule_basename):
        """
        Graph node of the submodule with the passed name in the parent module
        corresponding to this graph node.

        If this parent module does _not_ contain this submodule, an exception
        is raised. Else, this parent module is typically but _not_ always a
        package (e.g., the non-package `os` module containing the `os.path`
        submodule).

        Parameters
        ----------
        module_basename : str
            Unqualified name of the submodule to retrieve.

        Returns
        ----------
        Node
            Graph node of this submodule.
        """

        return self._submodule_basename_to_node[submodule_basename]


    def get_submodule_or_none(self, submodule_basename):
        """
        Graph node of the submodule with the passed unqualified name in the
        parent module corresponding to this graph node if this module contains
        this submodule _or_ `None`.

        This parent module is typically but _not_ always a package (e.g., the
        non-package `os` module containing the `os.path` submodule).

        Parameters
        ----------
        submodule_basename : str
            Unqualified name of the submodule to retrieve.

        Returns
        ----------
        Node
            Graph node of this submodule if this parent module contains this
            submodule _or_ `None`.
        """

        return self._submodule_basename_to_node.get(submodule_basename)


    def remove_global_attr_if_found(self, attr_name):
        """
        Record the global attribute (e.g., class, variable) with the passed
        name if previously recorded as defined by the pure-Python module
        corresponding to this graph node to be subsequently undefined by the
        same module.

        If this module is actually a package, this method instead records this
        attribute to be undefined by this package's pure-Python `__init__`
        submodule.

        This method is intended to be called on globals previously defined by
        this module that are subsequently undefined via the `del` built-in by
        this module, thus "forgetting" or "undoing" these globals.

        For safety, there exists no corresponding `remove_global_attr()`
        method. While defining this method is trivial, doing so would invite
        `KeyError` exceptions on scanning valid Python that lexically deletes a
        global in a scope under this module's top level (e.g., in a function)
        _before_ defining this global at this top level. Since `ModuleGraph`
        cannot and should not (re)implement a full-blown Python interpreter,
        ignoring out-of-order deletions is the only sane policy.

        Parameters
        ----------
        attr_name : str
            Unqualified name of the attribute to be removed.
        """

        if self.is_global_attr(attr_name):
            self._global_attr_names.remove(attr_name)

    def __eq__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return False

        return self.graphident == otherIdent

    def __ne__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return True

        return self.graphident != otherIdent

    def __lt__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return NotImplemented

        return self.graphident < otherIdent

    def __le__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return NotImplemented

        return self.graphident <= otherIdent

    def __gt__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return NotImplemented

        return self.graphident > otherIdent

    def __ge__(self, other):
        try:
            otherIdent = getattr(other, 'graphident')
        except AttributeError:
            return NotImplemented

        return self.graphident >= otherIdent

    def __hash__(self):
        return hash(self.graphident)

    def infoTuple(self):
        return (self.identifier,)

    def __repr__(self):
        return '%s%r' % (type(self).__name__, self.infoTuple())


# TODO: This indirection is, frankly, unnecessary. The
# ModuleGraph.alias_module() should directly add the desired AliasNode instance
# to the graph rather than indirectly adding an Alias instance to the
# "lazynodes" dictionary.
class Alias(str):
    """
    Placeholder aliasing an existing source module to a non-existent target
    module (i.e., the desired alias).

    For obscure reasons, this class subclasses `str`. Each instance of this
    class is the fully-qualified name of the existing source module being
    aliased. Unlike the related `AliasNode` class, instances of this class are
    _not_ actual nodes and hence _not_ added to the graph; they only facilitate
    communication between the `ModuleGraph.alias_module()` and
    `ModuleGraph.find_node()` methods.
    """


class AliasNode(Node):
    """
    Graph node representing the aliasing of an existing source module under a
    non-existent target module name (i.e., the desired alias).
    """

    def __init__(self, name, node):
        """
        Initialize this alias.

        Parameters
        ----------
        name : str
            Fully-qualified name of the non-existent target module to be
            created (as an alias of the existing source module).
        node : Node
            Graph node of the existing source module being aliased.
        """
        super(AliasNode, self).__init__(name)

        #FIXME: Why only some? Why not *EVERYTHING* except "graphident", which
        #must remain equal to "name" for lookup purposes? This is, after all,
        #an alias. The idea is for the two nodes to effectively be the same.

        # Copy some attributes from this source module into this target alias.
        for attr_name in (
            'identifier', 'packagepath',
            '_global_attr_names', '_starimported_ignored_module_names',
            '_submodule_basename_to_node'):
            if hasattr(node, attr_name):
                setattr(self, attr_name, getattr(node, attr_name))


    def infoTuple(self):
        return (self.graphident, self.identifier)


class BadModule(Node):
    pass


class ExcludedModule(BadModule):
    pass


class MissingModule(BadModule):
    pass


class InvalidRelativeImport (BadModule):
    def __init__(self, relative_path, from_name):
        identifier = relative_path
        if relative_path.endswith('.'):
            identifier += from_name
        else:
            identifier += '.' + from_name
        super(InvalidRelativeImport, self).__init__(identifier)
        self.relative_path = relative_path
        self.from_name = from_name

    def infoTuple(self):
        return (self.relative_path, self.from_name)


class Script(Node):
    def __init__(self, filename):
        super(Script, self).__init__(filename)
        self.filename = filename

    def infoTuple(self):
        return (self.filename,)


class BaseModule(Node):
    def __init__(self, name, filename=None, path=None):
        super(BaseModule, self).__init__(name)
        self.filename = filename
        self.packagepath = path

    def infoTuple(self):
        return tuple(filter(None, (self.identifier, self.filename, self.packagepath)))


class BuiltinModule(BaseModule):
    pass


class SourceModule(BaseModule):
    pass


class InvalidSourceModule(SourceModule):
    pass


class CompiledModule(BaseModule):
    pass


class InvalidCompiledModule(BaseModule):
    pass


class Extension(BaseModule):
    pass


class Package(BaseModule):
    """
    Graph node representing a non-namespace package.
    """
    pass


class ExtensionPackage(Extension, Package):
    """
    Graph node representing a package where the __init__ module is an extension
    module.
    """
    pass


class NamespacePackage(Package):
    """
    Graph node representing a namespace package.
    """
    pass


class RuntimeModule(BaseModule):
    """
    Graph node representing a non-package Python module dynamically defined at
    runtime.

    Most modules are statically defined on-disk as standard Python files.
    Some modules, however, are dynamically defined in-memory at runtime
    (e.g., `gi.repository.Gst`, dynamically defined by the statically
    defined `gi.repository.__init__` module).

    This node represents such a runtime module. Since this is _not_ a package,
    all attempts to import submodules from this module in `from`-style import
    statements (e.g., the `queue` submodule in `from six.moves import queue`)
    will be silently ignored.

    To ensure that the parent package of this module if any is also imported
    and added to the graph, this node is typically added to the graph by
    calling the `ModuleGraph.add_module()` method.
    """
    pass


class RuntimePackage(Package):
    """
    Graph node representing a non-namespace Python package dynamically defined
    at runtime.

    Most packages are statically defined on-disk as standard subdirectories
    containing `__init__.py` files. Some packages, however, are dynamically
    defined in-memory at runtime (e.g., `six.moves`, dynamically defined by
    the statically defined `six` module).

    This node represents such a runtime package. All attributes imported from
    this package in `from`-style import statements that are submodules of this
    package (e.g., the `queue` submodule in `from six.moves import queue`) will
    be imported rather than ignored.

    To ensure that the parent package of this package if any is also imported
    and added to the graph, this node is typically added to the graph by
    calling the `ModuleGraph.add_module()` method.
    """
    pass


#FIXME: Safely removable. We don't actually use this anywhere. After removing
#this class, remove the corresponding entry from "compat".
class FlatPackage(BaseModule):
    def __init__(self, *args, **kwds):
        warnings.warn(
            "This class will be removed in a future version of modulegraph",
            DeprecationWarning)
        super(FlatPackage, *args, **kwds)


#FIXME: Safely removable. We don't actually use this anywhere. After removing
#this class, remove the corresponding entry from "compat".
class ArchiveModule(BaseModule):
    def __init__(self, *args, **kwds):
        warnings.warn(
            "This class will be removed in a future version of modulegraph",
            DeprecationWarning)
        super(FlatPackage, *args, **kwds)


# HTML templates for ModuleGraph generator
header = """\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>%(TITLE)s</title>
    <style>
      .node { padding: 0.5em 0 0.5em; border-top: thin grey dotted; }
      .moduletype { font: smaller italic }
      .node a { text-decoration: none; color: #006699; }
      .node a:visited { text-decoration: none; color: #2f0099; }
    </style>
  </head>
  <body>
    <h1>%(TITLE)s</h1>"""
entry = """
<div class="node">
  <a name="%(NAME)s"></a>
  %(CONTENT)s
</div>"""
contpl = """<tt>%(NAME)s</tt> <span class="moduletype">%(TYPE)s</span>"""
contpl_linked = """\
<a target="code" href="%(URL)s" type="text/plain"><tt>%(NAME)s</tt></a>
<span class="moduletype">%(TYPE)s</span>"""
imports = """\
  <div class="import">
%(HEAD)s:
  %(LINKS)s
  </div>
"""
footer = """
  </body>
</html>"""


def _ast_names(names):
    result = []
    for nm in names:
        if isinstance(nm, ast.alias):
            result.append(nm.name)
        else:
            result.append(nm)

    result = [r for r in result if r != '__main__']
    return result


def uniq(seq):
    """Remove duplicates from a list, preserving order"""
    # Taken from https://stackoverflow.com/questions/480214
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


DEFAULT_IMPORT_LEVEL = 0


class _Visitor(ast.NodeVisitor):
    def __init__(self, graph, module):
        self._graph = graph
        self._module = module
        self._level = DEFAULT_IMPORT_LEVEL
        self._in_if = [False]
        self._in_def = [False]
        self._in_tryexcept = [False]

    @property
    def in_if(self):
        return self._in_if[-1]

    @property
    def in_def(self):
        return self._in_def[-1]

    @property
    def in_tryexcept(self):
        return self._in_tryexcept[-1]


    def _collect_import(self, name, fromlist, level):
        have_star = False
        if fromlist is not None:
            fromlist = uniq(fromlist)
            if '*' in fromlist:
                fromlist.remove('*')
                have_star = True

        # Record this import as originating from this module for subsequent
        # handling by the _process_imports() method.
        self._module._deferred_imports.append(
            (have_star,
             (name, self._module, fromlist, level),
             {'edge_attr': DependencyInfo(
                 conditional=self.in_if,
                 tryexcept=self.in_tryexcept,
                 function=self.in_def,
                 fromlist=False)}))


    def visit_Import(self, node):
        for nm in _ast_names(node.names):
            self._collect_import(nm, None, self._level)

    def visit_ImportFrom(self, node):
        level = node.level if node.level != 0 else self._level
        self._collect_import(node.module or '', _ast_names(node.names), level)

    def visit_If(self, node):
        self._in_if.append(True)
        self.generic_visit(node)
        self._in_if.pop()

    def visit_FunctionDef(self, node):
        self._in_def.append(True)
        self.generic_visit(node)
        self._in_def.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Try(self, node):
        self._in_tryexcept.append(True)
        self.generic_visit(node)
        self._in_tryexcept.pop()

    def visit_TryExcept(self, node):
        self._in_tryexcept.append(True)
        self.generic_visit(node)
        self._in_tryexcept.pop()

    def visit_Expression(self, node):
        # Expression node's cannot contain import statements or
        # other nodes that are relevant for us.
        pass

    # Expression isn't actually used as such in AST trees,
    # therefore define visitors for all kinds of expression nodes.
    visit_BoolOp = visit_Expression
    visit_BinOp = visit_Expression
    visit_UnaryOp = visit_Expression
    visit_Lambda = visit_Expression
    visit_IfExp = visit_Expression
    visit_Dict = visit_Expression
    visit_Set = visit_Expression
    visit_ListComp = visit_Expression
    visit_SetComp = visit_Expression
    visit_ListComp = visit_Expression
    visit_GeneratorExp = visit_Expression
    visit_Compare = visit_Expression
    visit_Yield = visit_Expression
    visit_YieldFrom = visit_Expression
    visit_Await = visit_Expression
    visit_Call = visit_Expression
    visit_Await = visit_Expression


class ModuleGraph(ObjectGraph):
    """
    Directed graph whose nodes represent modules and edges represent
    dependencies between these modules.
    """


    def createNode(self, cls, name, *args, **kw):
        m = self.find_node(name)

        if m is None:
            #assert m is None, m
            m = super(ModuleGraph, self).createNode(cls, name, *args, **kw)

        return m


    def __init__(self, path=None, excludes=(), replace_paths=(), implies=(), graph=None, debug=0):
        super(ModuleGraph, self).__init__(graph=graph, debug=debug)
        if path is None:
            path = sys.path
        self.path = path
        self.lazynodes = {}
        # excludes is stronger than implies
        self.lazynodes.update(dict(implies))
        for m in excludes:
            self.lazynodes[m] = None
        self.replace_paths = replace_paths

        # Maintain own list of package path mappings in the scope of Modulegraph
        # object.
        self._package_path_map = {}

        # Legacy namespace-package paths. Initialized by scan_legacy_namespace_packages.
        self._legacy_ns_packages = {}

    def scan_legacy_namespace_packages(self):
        """
        Resolve extra package `__path__` entries for legacy setuptools-based
        namespace packages, by reading `namespace_packages.txt` from dist
        metadata.
        """
        legacy_ns_packages = defaultdict(lambda: set())

        for dist in importlib_metadata.distributions():
            ns_packages = dist.read_text("namespace_packages.txt")
            if ns_packages is None:
                continue
            ns_packages = ns_packages.splitlines()
            # Obtain path to dist metadata directory
            dist_path = getattr(dist, '_path')
            if dist_path is None:
                continue
            for package_name in ns_packages:
                path = os.path.join(
                    str(dist_path.parent),  # might be zipfile.Path if in zipped .egg
                    *package_name.split('.'),
                )
                legacy_ns_packages[package_name].add(path)

        # Convert into dictionary of lists
        self._legacy_ns_packages = {
            package_name: list(paths)
            for package_name, paths in legacy_ns_packages.items()
        }

    def implyNodeReference(self, node, other, edge_data=None):
        """
        Create a reference from the passed source node to the passed other node,
        implying the former to depend upon the latter.

        While the source node _must_ be an existing graph node, the target node
        may be either an existing graph node _or_ a fully-qualified module name.
        In the latter case, the module with that name and all parent packages of
        that module will be imported _without_ raising exceptions and for each
        newly imported module or package:

        * A new graph node will be created for that module or package.
        * A reference from the passed source node to that module or package will
          be created.

        This method allows dependencies between Python objects _not_ importable
        with standard techniques (e.g., module aliases, C extensions).

        Parameters
        ----------
        node : str
            Graph node for this reference's source module or package.
        other : {Node, str}
            Either a graph node _or_ fully-qualified name for this reference's
            target module or package.
        """

        if isinstance(other, Node):
            self._updateReference(node, other, edge_data)
        else:
            if isinstance(other, tuple):
                raise ValueError(other)
            others = self._safe_import_hook(other, node, None)
            for other in others:
                self._updateReference(node, other, edge_data)

    def outgoing(self, fromnode):
        """
        Yield all nodes that `fromnode` dependes on (that is,
        all modules that `fromnode` imports.
        """

        node = self.find_node(fromnode)
        out_edges, _ = self.get_edges(node)
        return out_edges

    getReferences = outgoing

    def incoming(self, tonode, collapse_missing_modules=True):
        node = self.find_node(tonode)
        _, in_edges = self.get_edges(node)

        if collapse_missing_modules:
            for n in in_edges:
                if isinstance(n, MissingModule):
                    for n in self.incoming(n, False):
                        yield n

                else:
                    yield n

        else:
            for n in in_edges:
                yield n

    getReferers = incoming

    def hasEdge(self, fromnode, tonode):
        """ Return True iff there is an edge from 'fromnode' to 'tonode' """
        fromnode = self.find_node(fromnode)
        tonode = self.find_node(tonode)

        return self.graph.edge_by_node(fromnode, tonode) is not None

    def foldReferences(self, packagenode):
        """
        Create edges to/from `packagenode` based on the edges to/from all
        submodules of that package _and_ then hide the graph nodes
        corresponding to those submodules.
        """

        pkg = self.find_node(packagenode)

        for n in self.nodes():
            if not n.identifier.startswith(pkg.identifier + '.'):
                continue

            iter_out, iter_inc = self.get_edges(n)
            for other in iter_out:
                if other.identifier.startswith(pkg.identifier + '.'):
                    continue

                if not self.hasEdge(pkg, other):
                    # Ignore circular dependencies
                    self._updateReference(pkg, other, 'pkg-internal-import')

            for other in iter_inc:
                if other.identifier.startswith(pkg.identifier + '.'):
                    # Ignore circular dependencies
                    continue

                if not self.hasEdge(other, pkg):
                    self._updateReference(other, pkg, 'pkg-import')

            self.graph.hide_node(n)

    # TODO: unfoldReferences(pkg) that restore the submodule nodes and
    #       removes 'pkg-import' and 'pkg-internal-import' edges. Care should
    #       be taken to ensure that references are correct if multiple packages
    #       are folded and then one of them in unfolded

    def _updateReference(self, fromnode, tonode, edge_data):
        try:
            ed = self.edgeData(fromnode, tonode)
        except (KeyError, GraphError):  # XXX: Why 'GraphError'
            return self.add_edge(fromnode, tonode, edge_data)

        if not (isinstance(ed, DependencyInfo) and isinstance(edge_data, DependencyInfo)):
            self.updateEdgeData(fromnode, tonode, edge_data)
        else:
            self.updateEdgeData(fromnode, tonode, ed._merged(edge_data))

    def add_edge(self, fromnode, tonode, edge_data='direct'):
        """
        Create a reference from fromnode to tonode
        """
        return super(ModuleGraph, self).createReference(fromnode, tonode, edge_data=edge_data)

    createReference = add_edge

    def find_node(self, name, create_nspkg=True):
        """
        Graph node uniquely identified by the passed fully-qualified module
        name if this module has been added to the graph _or_ `None` otherwise.

        If (in order):

        . A namespace package with this identifier exists _and_ the passed
          `create_nspkg` parameter is `True`, this package will be
          instantiated and returned.
        . A lazy node with this identifier and:
          * No dependencies exists, this node will be instantiated and
            returned.
          * Dependencies exists, this node and all transitive dependencies of
            this node be instantiated and this node returned.
        . A non-lazy node with this identifier exists, this node will be
          returned as is.

        Parameters
        ----------
        name : str
            Fully-qualified name of the module whose graph node is to be found.
        create_nspkg : bool
            Ignored.

        Returns
        ----------
        Node
            Graph node of this module if added to the graph _or_ `None`
            otherwise.
        """

        data = super(ModuleGraph, self).findNode(name)

        if data is not None:
            return data

        if name in self.lazynodes:
            deps = self.lazynodes.pop(name)

            if deps is None:
                # excluded module
                m = self.createNode(ExcludedModule, name)
            elif isinstance(deps, Alias):
                other = self._safe_import_hook(deps, None, None).pop()
                m = self.createNode(AliasNode, name, other)
                self.implyNodeReference(m, other)
            else:
                m = self._safe_import_hook(name, None, None).pop()
                for dep in deps:
                    self.implyNodeReference(m, dep)

            return m

        return None

    findNode = find_node
    iter_graph = ObjectGraph.flatten

    def add_script(self, pathname, caller=None):
        """
        Create a node by path (not module name).  It is expected to be a Python
        source file, and will be scanned for dependencies.
        """
        self.msg(2, "run_script", pathname)

        pathname = os.path.realpath(pathname)
        m = self.find_node(pathname)
        if m is not None:
            return m

        with open(pathname, 'rb') as fp:
            contents = fp.read()
        contents = importlib.util.decode_source(contents)

        co_ast = compile(contents, pathname, 'exec', ast.PyCF_ONLY_AST, True)
        co = compile(co_ast, pathname, 'exec', 0, True)
        m = self.createNode(Script, pathname)
        self._updateReference(caller, m, None)
        n = self._scan_code(m, co, co_ast)
        self._process_imports(n)
        m.code = co
        if self.replace_paths:
            m.code = self._replace_paths_in_code(m.code)
        return m


    #FIXME: For safety, the "source_module" parameter should default to the
    #root node of the current graph if unpassed. This parameter currently
    #defaults to None, thus disconnected modules imported in this manner (e.g.,
    #hidden imports imported by depend.analysis.initialize_modgraph()).
    def import_hook(
        self,
        target_module_partname,
        source_module=None,
        target_attr_names=None,
        level=DEFAULT_IMPORT_LEVEL,
        edge_attr=None,
    ):
        """
        Import the module with the passed name, all parent packages of this
        module, _and_ all submodules and attributes in this module with the
        passed names from the previously imported caller module signified by
        the passed graph node.

        Unlike most import methods (e.g., `_safe_import_hook()`), this method
        is designed to be publicly called by both external and internal
        callers and hence is public.

        Parameters
        ----------
        target_module_partname : str
            Partially-qualified name of the target module to be imported. See
            `_safe_import_hook()` for further details.
        source_module : Node
            Graph node for the previously imported **source module** (i.e.,
            module containing the `import` statement triggering the call to
            this method) _or_ `None` if this module is to be imported in a
            "disconnected" manner. **Passing `None` is _not_ recommended.**
            Doing so produces a disconnected graph in which the graph node
            created for the module to be imported will be disconnected and
            hence unreachable from all other nodes -- which frequently causes
            subtle issues in external callers (namely PyInstaller, which
            silently ignores unreachable nodes).
        target_attr_names : list
            List of the unqualified names of all submodules and attributes to
            be imported from the module to be imported if this is a "from"-
            style import (e.g., `[encode_base64, encode_noop]` for the import
            `from email.encoders import encode_base64, encode_noop`) _or_
            `None` otherwise.
        level : int
            Whether to perform an absolute or relative import. See
            `_safe_import_hook()` for further details.

        Returns
        ----------
        list
            List of the graph nodes created for all modules explicitly imported
            by this call, including the passed module and all submodules listed
            in `target_attr_names` _but_ excluding all parent packages
            implicitly imported by this call. If `target_attr_names` is `None`
            or the empty list, this is guaranteed to be a list of one element:
            the graph node created for the passed module.

        Raises
        ----------
        ImportError
            If the target module to be imported is unimportable.
        """
        self.msg(3, "_import_hook", target_module_partname, source_module, source_module, level)

        source_package = self._determine_parent(source_module)
        target_package, target_module_partname = self._find_head_package(
            source_package, target_module_partname, level)

        self.msgin(4, "load_tail", target_package, target_module_partname)

        submodule = target_package
        while target_module_partname:
            i = target_module_partname.find('.')
            if i < 0:
                i = len(target_module_partname)
            head, target_module_partname = target_module_partname[
                :i], target_module_partname[i+1:]
            mname = "%s.%s" % (submodule.identifier, head)
            submodule = self._safe_import_module(head, mname, submodule)

            if submodule is None:
                # FIXME: Why do we no longer return a MissingModule instance?
                # result = self.createNode(MissingModule, mname)
                self.msgout(4, "raise ImportError: No module named", mname)
                raise ImportError("No module named " + repr(mname))

        self.msgout(4, "load_tail ->", submodule)

        target_module = submodule
        target_modules = [target_module]

        # If this is a "from"-style import *AND* this target module is
        # actually a package, import all submodules of this package specified
        # by the "import" half of this import (e.g., the submodules "bar" and
        # "car" of the target package "foo" in "from foo import bar, car").
        #
        # If this target module is a non-package, it could still contain
        # importable submodules (e.g., the non-package `os` module containing
        # the `os.path` submodule). In this case, these submodules are already
        # imported by this target module's pure-Python code. Since our import
        # scanner already detects such imports, these submodules need *NOT* be
        # reimported here.
        if target_attr_names and isinstance(target_module,
                                            (Package, AliasNode)):
            for target_submodule in self._import_importable_package_submodules(
                target_module, target_attr_names):
                if target_submodule not in target_modules:
                    target_modules.append(target_submodule)

        # Add an edge from this source module to each target module.
        for target_module in target_modules:
            self._updateReference(
                source_module, target_module, edge_data=edge_attr)

        return target_modules


    def _determine_parent(self, caller):
        """
        Determine the package containing a node.
        """
        self.msgin(4, "determine_parent", caller)

        parent = None
        if caller:
            pname = caller.identifier

            if isinstance(caller, Package):
                parent = caller

            elif '.' in pname:
                pname = pname[:pname.rfind('.')]
                parent = self.find_node(pname)

            elif caller.packagepath:
                # XXX: I have no idea why this line
                # is necessary.
                parent = self.find_node(pname)

        self.msgout(4, "determine_parent ->", parent)
        return parent


    def _find_head_package(
        self,
        source_package,
        target_module_partname,
        level=DEFAULT_IMPORT_LEVEL):
        """
        Import the target package providing the target module with the passed
        name to be subsequently imported from the previously imported source
        package corresponding to the passed graph node.

        Parameters
        ----------
        source_package : Package
            Graph node for the previously imported **source package** (i.e.,
            package containing the module containing the `import` statement
            triggering the call to this method) _or_ `None` if this module is
            to be imported in a "disconnected" manner. **Passing `None` is
            _not_ recommended.** See the `_import_hook()` method for further
            details.
        target_module_partname : str
            Partially-qualified name of the target module to be imported. See
            `_safe_import_hook()` for further details.
        level : int
            Whether to perform absolute or relative imports. See the
            `_safe_import_hook()` method for further details.

        Returns
        ----------
        (target_package, target_module_tailname)
            2-tuple describing the imported target package, where:
            * `target_package` is the graph node created for this package.
            * `target_module_tailname` is the unqualified name of the target
              module to be subsequently imported (e.g., `text` when passed a
              `target_module_partname` of `email.mime.text`).

        Raises
        ----------
        ImportError
            If the package to be imported is unimportable.
        """
        self.msgin(4, "find_head_package", source_package, target_module_partname, level)

        #FIXME: Rename all local variable names to something sensible. No,
        #"p_fqdn" is not a sensible name.

        # If this target module is a submodule...
        if '.' in target_module_partname:
            target_module_headname, target_module_tailname = (
                target_module_partname.split('.', 1))
        # Else, this target module is a top-level module.
        else:
            target_module_headname = target_module_partname
            target_module_tailname = ''

        # If attempting both absolute and relative imports...
        if level == ABSOLUTE_OR_RELATIVE_IMPORT_LEVEL:
            if source_package:
                target_package_name = source_package.identifier + '.' + target_module_headname
            else:
                target_package_name = target_module_headname
        # Else if attempting only absolute imports...
        elif level == ABSOLUTE_IMPORT_LEVEL:
            target_package_name = target_module_headname

            # Absolute import, ignore the parent
            source_package = None
        # Else if attempting only relative imports...
        else:
            if source_package is None:
                self.msg(2, "Relative import outside of package")
                raise InvalidRelativeImportError(
                    "Relative import outside of package (name=%r, parent=%r, level=%r)" % (
                        target_module_partname, source_package, level))

            for i in range(level - 1):
                if '.' not in source_package.identifier:
                    self.msg(2, "Relative import outside of package")
                    raise InvalidRelativeImportError(
                        "Relative import outside of package (name=%r, parent=%r, level=%r)" % (
                            target_module_partname, source_package, level))

                p_fqdn = source_package.identifier.rsplit('.', 1)[0]
                new_parent = self.find_node(p_fqdn)
                if new_parent is None:
                    #FIXME: Repetition detected. Exterminate. Exterminate.
                    self.msg(2, "Relative import outside of package")
                    raise InvalidRelativeImportError(
                        "Relative import outside of package (name=%r, parent=%r, level=%r)" % (
                            target_module_partname, source_package, level))

                assert new_parent is not source_package, (
                    new_parent, source_package)
                source_package = new_parent

            if target_module_headname:
                target_package_name = (
                    source_package.identifier + '.' + target_module_headname)
            else:
                target_package_name = source_package.identifier

        # Graph node of this target package.
        target_package = self._safe_import_module(
            target_module_headname, target_package_name, source_package)

        # If this target package is *NOT* importable and a source package was
        # passed, attempt to import this target package as an absolute import.
        #
        # ADDENDUM: but do this only if the passed "level" is either
        # ABSOLUTE_IMPORT_LEVEL (0) or ABSOLUTE_OR_RELATIVE_IMPORT_LEVEL (-1).
        # Otherwise, an attempt at relative import of a missing sub-module
        # (from .module import something) might pull in an unrelated
        # but eponymous top-level module, which should not happen.
        if target_package is None and source_package is not None and level <= ABSOLUTE_IMPORT_LEVEL:
            target_package_name = target_module_headname
            source_package = None

            # Graph node for the target package, again.
            target_package = self._safe_import_module(
                target_module_headname, target_package_name, source_package)

        # If this target package is importable, return this package.
        if target_package is not None:
            self.msgout(4, "find_head_package ->", (target_package, target_module_tailname))
            return target_package, target_module_tailname

        # Else, raise an exception.
        self.msgout(4, "raise ImportError: No module named", target_package_name)
        raise ImportError("No module named " + target_package_name)




    #FIXME: Refactor from a generator yielding graph nodes into a non-generator
    #returning a list or tuple of all yielded graph nodes. This method is only
    #called once above and the return value of that call is only iterated over
    #as a list or tuple. There's no demonstrable reason for this to be a
    #generator. Generators are great for their intended purposes (e.g., as
    #continuations). This isn't one of those purposes.
    def _import_importable_package_submodules(self, package, attr_names):
        """
        Generator importing and yielding each importable submodule (of the
        previously imported package corresponding to the passed graph node)
        whose unqualified name is in the passed list.

        Elements of this list that are _not_ importable submodules of this
        package are either:

        * Ignorable attributes (e.g., classes, globals) defined at the top
          level of this package's `__init__` submodule, which will be ignored.
        * Else, unignorable unimportable submodules, in which case an
          exception is raised.

        Parameters
        ----------
        package : Package
            Graph node of the previously imported package containing the
            modules to be imported and yielded.

        attr_names : list
            List of the unqualified names of all attributes of this package to
            attempt to import as submodules. This list will be internally
            converted into a set, safely ignoring any duplicates in this list
            (e.g., reducing the "from"-style import
            `from foo import bar, car, far, bar, car, far` to merely
            `from foo import bar, car, far`).

        Yields
        ----------
        Node
            Graph node created for the currently imported submodule.

        Raises
        ----------
        ImportError
            If any attribute whose name is in `attr_names` is neither:
            * An importable submodule of this package.
            * An ignorable global attribute (e.g., class, variable) defined at
              the top level of this package's `__init__` submodule.
            In this case, this attribute _must_ be an unimportable submodule of
            this package.
        """

        # Ignore duplicate submodule names in the passed list.
        attr_names = set(attr_names)
        self.msgin(4, "_import_importable_package_submodules", package, attr_names)

        #FIXME: This test *SHOULD* be superfluous and hence safely removable.
        #The higher-level _scan_bytecode() and _collect_import() methods
        #already guarantee "*" characters to be removed from fromlists.
        if '*' in attr_names:
            attr_names.update(self._find_all_submodules(package))
            attr_names.remove('*')

        # self.msg(4, '_import_importable_package_submodules (global attrs)', package.identifier, package._global_attr_names)

        # For the name of each attribute to be imported from this package...
        for attr_name in attr_names:
            # self.msg(4, '_import_importable_package_submodules (fromlist attr)', package.identifier, attr_name)

            # Graph node of this attribute if this attribute is a previously
            # imported module or None otherwise.
            submodule = package.get_submodule_or_none(attr_name)

            # If this attribute is *NOT* a previously imported module, attempt
            # to import this attribute as a submodule of this package.
            if submodule is None:
                # Fully-qualified name of this submodule.
                submodule_name = package.identifier + '.' + attr_name

                # Graph node of this submodule if importable or None otherwise.
                submodule = self._safe_import_module(
                    attr_name, submodule_name, package)

                # If this submodule is unimportable...
                if submodule is None:
                    # If this attribute is a global (e.g., class, variable)
                    # defined at the top level of this package's "__init__"
                    # submodule, this importation is safely ignorable. Do so
                    # and skip to the next attribute.
                    #
                    # This behaviour is non-conformant with Python behaviour,
                    # which is bad, but is required to sanely handle all
                    # possible edge cases, which is good. In Python, a global
                    # attribute defined at the top level of a package's
                    # "__init__" submodule shadows a submodule of the same name
                    # in that package. Attempting to import that submodule
                    # instead imports that attribute; thus, that submodule is
                    # effectively unimportable. In this method and elsewhere,
                    # that submodule is tested for first and hence shadows that
                    # attribute -- the opposite logic. Attempts to import that
                    # attribute are mistakenly seen as attempts to import that
                    # submodule! Why?
                    #
                    # Edge cases. PyInstaller (and by extension ModuleGraph)
                    # only cares about module imports. Global attribute imports
                    # are parsed only as the means to this ends and are
                    # otherwise ignorable. The cost of erroneously shadowing:
                    #
                    # * Submodules by attributes is significant. Doing so
                    #   prevents such submodules from being frozen and hence
                    #   imported at application runtime.
                    # * Attributes by submodules is insignificant. Doing so
                    #   could erroneously freeze such submodules despite their
                    #   never being imported at application runtime. However,
                    #   ModuleGraph is incapable of determining with certainty
                    #   that Python logic in another module other than the
                    #   "__init__" submodule containing these attributes does
                    #   *NOT* delete these attributes and hence unshadow these
                    #   submodules, which would then become importable at
                    #   runtime and require freezing. Hence, ModuleGraph *MUST*
                    #   permissively assume submodules of the same name as
                    #   attributes to be unshadowed elsewhere and require
                    #   freezing -- even if they do not.
                    #
                    # It is practically difficult (albeit technically feasible)
                    # for ModuleGraph to determine whether or not the target
                    # attribute names of "from"-style import statements (e.g.,
                    # "bar" and "car" in "from foo import bar, car") refer to
                    # non-ignorable submodules or ignorable non-module globals
                    # during opcode scanning. Distinguishing these two cases
                    # during opcode scanning would require a costly call to the
                    # _find_module() method, which would subsequently be
                    # repeated during import-graph construction. This could be
                    # ameliorated with caching, which itself would require
                    # costly space consumption and developer time.
                    #
                    # Since opcode scanning fails to distinguish these two
                    # cases, this and other methods subsequently called at
                    # import-graph construction time (e.g.,
                    # _safe_import_hook()) must do so. Since submodules of the
                    # same name as attributes must assume to be unshadowed
                    # elsewhere and require freezing, the only solution is to
                    # attempt to import an attribute as a non-ignorable module
                    # *BEFORE* assuming an attribute to be an ignorable
                    # non-module. Which is what this and other methods do.
                    #
                    # See Package.is_global_attr() for similar discussion.
                    if package.is_global_attr(attr_name):
                        self.msg(4, '_import_importable_package_submodules: ignoring from-imported global', package.identifier, attr_name)
                        continue
                    # Else, this attribute is an unimportable submodule. Since
                    # this is *NOT* safely ignorable, raise an exception.
                    else:
                        raise ImportError("No module named " + submodule_name)

            # Yield this submodule's graph node to the caller.
            yield submodule

        self.msgin(4, "_import_importable_package_submodules ->")


    def _find_all_submodules(self, m):
        if not m.packagepath:
            return
        # 'suffixes' used to be a list hardcoded to [".py", ".pyc", ".pyo"].
        # But we must also collect Python extension modules - although
        # we cannot separate normal dlls from Python extensions.
        for path in m.packagepath:
            try:
                names = os.listdir(path)
            except (os.error, IOError):
                self.msg(2, "can't list directory", path)
                continue
            for name in names:
                for suffix in importlib.machinery.all_suffixes():
                    if path.endswith(suffix):
                        name = os.path.basename(path)[:-len(suffix)]
                        break
                else:
                    continue
                if name != '__init__':
                    yield name


    def alias_module(self, src_module_name, trg_module_name):
        """
        Alias the source module to the target module with the passed names.

        This method ensures that the next call to findNode() given the target
        module name will resolve this alias. This includes importing and adding
        a graph node for the source module if needed as well as adding a
        reference from the target to source module.

        Parameters
        ----------
        src_module_name : str
            Fully-qualified name of the existing **source module** (i.e., the
            module being aliased).
        trg_module_name : str
            Fully-qualified name of the non-existent **target module** (i.e.,
            the alias to be created).
        """
        self.msg(3, 'alias_module "%s" -> "%s"' % (src_module_name, trg_module_name))
        # print('alias_module "%s" -> "%s"' % (src_module_name, trg_module_name))
        assert isinstance(src_module_name, str), '"%s" not a module name.' % str(src_module_name)
        assert isinstance(trg_module_name, str), '"%s" not a module name.' % str(trg_module_name)

        # If the target module has already been added to the graph as either a
        # non-alias or as a different alias, raise an exception.
        trg_module = self.find_node(trg_module_name)
        if trg_module is not None and not (
           isinstance(trg_module, AliasNode) and
           trg_module.identifier == src_module_name):
            raise ValueError(
                'Target module "%s" already imported as "%s".' % (
                    trg_module_name, trg_module))

        # See findNode() for details.
        self.lazynodes[trg_module_name] = Alias(src_module_name)


    def add_module(self, module):
        """
        Add the passed module node to the graph if not already added.

        If that module has a parent module or package with a previously added
        node, this method also adds a reference from this module node to its
        parent node and adds this module node to its parent node's namespace.

        This high-level method wraps the low-level `addNode()` method, but is
        typically _only_ called by graph hooks adding runtime module nodes. For
        all other node types, the `import_module()` method should be called.

        Parameters
        ----------
        module : BaseModule
            Graph node of the module to be added.
        """
        self.msg(3, 'add_module', module)

        # If no node exists for this module, add such a node.
        module_added = self.find_node(module.identifier)
        if module_added is None:
            self.addNode(module)
        else:
            assert module == module_added, 'New module %r != previous %r.' % (module, module_added)

        # If this module has a previously added parent, reference this module to
        # its parent and add this module to its parent's namespace.
        parent_name, _, module_basename = module.identifier.rpartition('.')
        if parent_name:
            parent = self.find_node(parent_name)
            if parent is None:
                self.msg(4, 'add_module parent not found:', parent_name)
            else:
                self.add_edge(module, parent)
                parent.add_submodule(module_basename, module)


    def append_package_path(self, package_name, directory):
        """
        Modulegraph does a good job at simulating Python's, but it can not
        handle packagepath '__path__' modifications packages make at runtime.

        Therefore there is a mechanism whereby you can register extra paths
        in this map for a package, and it will be honored.

        NOTE: This method has to be called before a package is resolved by
              modulegraph.

        Parameters
        ----------
        module : str
            Fully-qualified module name.
        directory : str
            Absolute or relative path of the directory to append to the
            '__path__' attribute.
        """

        paths = self._package_path_map.setdefault(package_name, [])
        paths.append(directory)


    def _safe_import_module(
        self, module_partname, module_name, parent_module):
        """
        Create a new graph node for the module with the passed name under the
        parent package signified by the passed graph node _without_ raising
        `ImportError` exceptions.

        If this module has already been imported, this module's existing graph
        node will be returned; else if this module is importable, a new graph
        node will be added for this module and returned; else this module is
        unimportable, in which case `None` will be returned. Like the
        `_safe_import_hook()` method, this method does _not_ raise
        `ImportError` exceptions when this module is unimportable.

        Parameters
        ----------
        module_partname : str
            Unqualified name of the module to be imported (e.g., `text`).
        module_name : str
            Fully-qualified name of this module (e.g., `email.mime.text`).
        parent_module : Package
            Graph node of the previously imported parent module containing this
            submodule _or_ `None` if this is a top-level module (i.e.,
            `module_name` contains no `.` delimiters). This parent module is
            typically but _not_ always a package (e.g., the `os.path` submodule
            contained by the `os` module).

        Returns
        ----------
        Node
            Graph node created for this module _or_ `None` if this module is
            unimportable.
        """
        self.msgin(3, "safe_import_module", module_partname, module_name, parent_module)

        # If this module has *NOT* already been imported, do so.
        module = self.find_node(module_name)
        if module is None:
            # List of the absolute paths of all directories to be searched for
            # this module. This effectively defaults to "sys.path".
            search_dirs = None

            # If this module has a parent package...
            if parent_module is not None:
                # ...with a list of the absolute paths of all directories
                # comprising this package, prefer that to "sys.path".
                if parent_module.packagepath is not None:
                    search_dirs = parent_module.packagepath
                # Else, something is horribly wrong. Return emptiness.
                else:
                    self.msgout(3, "safe_import_module -> None (parent_parent.packagepath is None)")
                    return None

            try:
                pathname, loader = self._find_module(
                    module_partname, search_dirs, parent_module)
            except ImportError as exc:
                self.msgout(3, "safe_import_module -> None (%r)" % exc)
                return None

            (module, co) = self._load_module(module_name, pathname, loader)
            if co is not None:
                try:
                    if isinstance(co, ast.AST):
                        co_ast = co
                        co = compile(co_ast, pathname, 'exec', 0, True)
                    else:
                        co_ast = None
                    n = self._scan_code(module, co, co_ast)
                    self._process_imports(n)

                    if self.replace_paths:
                        co = self._replace_paths_in_code(co)
                    module.code = co
                except SyntaxError:
                    self.msg(
                        1, "safe_import_module: SyntaxError in ", pathname,
                    )
                    cls = InvalidSourceModule
                    module = self.createNode(cls, module_name)

        # If this is a submodule rather than top-level module...
        if parent_module is not None:
            self.msg(4, "safe_import_module create reference", module, "->", parent_module)

            # Add an edge from this submodule to its parent module.
            self._updateReference(
                module, parent_module, edge_data=DependencyInfo(
                    conditional=False,
                    fromlist=False,
                    function=False,
                    tryexcept=False,
            ))

            # Add this submodule to its parent module.
            parent_module.add_submodule(module_partname, module)

        # Return this module.
        self.msgout(3, "safe_import_module ->", module)
        return module

    def _load_module(self, fqname, pathname, loader):
        from importlib._bootstrap_external import ExtensionFileLoader
        self.msgin(2, "load_module", fqname, pathname,
                   loader.__class__.__name__)
        partname = fqname.rpartition(".")[-1]

        if loader.is_package(partname):
            if isinstance(loader, NAMESPACE_PACKAGE):
                # This is a PEP-420 namespace package.
                m = self.createNode(NamespacePackage, fqname)
                m.filename = '-'
                m.packagepath = loader.namespace_dirs[:]  # copy for safety
            else:
                # Regular package.
                #
                # NOTE: this might be a legacy setuptools (pkg_resources)
                # based namespace package (with __init__.py, but calling
                # `pkg_resources.declare_namespace(__name__)`). To properly
                # handle the case when such a package is split across
                # multiple locations, we need to resolve the package
                # paths via metadata.
                ns_pkgpaths = self._legacy_ns_packages.get(fqname, [])

                if isinstance(loader, ExtensionFileLoader):
                    m = self.createNode(ExtensionPackage, fqname)
                else:
                    m = self.createNode(Package, fqname)
                m.filename = pathname
                # PEP-302-compliant loaders return the pathname of the
                # `__init__`-file, not the package directory.
                assert os.path.basename(pathname).startswith('__init__.')
                m.packagepath = [os.path.dirname(pathname)] + ns_pkgpaths

            # As per comment at top of file, simulate runtime packagepath
            # additions
            m.packagepath = m.packagepath + self._package_path_map.get(
                fqname, [])

            if isinstance(m, NamespacePackage):
                return (m, None)

        co = None
        if loader is BUILTIN_MODULE:
            cls = BuiltinModule
        elif isinstance(loader, ExtensionFileLoader):
            cls = Extension
        else:
            try:
                src = loader.get_source(partname)
            except (UnicodeDecodeError, SyntaxError) as e:
                # The `UnicodeDecodeError` is typically raised here when the
                # source file contains non-ASCII characters in some local
                # encoding that is different from UTF-8, but fails to
                # declare it via PEP361 encoding header. Python seems to
                # be able to load and run such module, but we cannot retrieve
                # the source for it via the `loader.get_source()`.
                #
                # The `UnicodeDecoreError` in turn triggers a `SyntaxError`
                # when such invalid character appears on the first line of
                # the source file (and interrupts the scan for PEP361
                # encoding header).
                #
                # In such cases, we try to fall back to reading the source
                # as raw data file.

                # If `SyntaxError` was not raised during handling of
                # a `UnicodeDecodeError`, it was likely a genuine syntax
                # error, so re-raise it.
                if isinstance(e, SyntaxError):
                    if not isinstance(e.__context__, UnicodeDecodeError):
                        raise

                self.msg(2, "load_module: failed to obtain source for "
                         f"{partname}: {e}! Falling back to reading as "
                         "raw data!")

                path = loader.get_filename(partname)
                src = loader.get_data(path)

            if src is not None:
                try:
                    co = compile(src, pathname, 'exec', ast.PyCF_ONLY_AST, True)
                    cls = SourceModule
                except SyntaxError:
                    co = None
                    cls = InvalidSourceModule
                except Exception as exc:  # FIXME: more specific?
                    cls = InvalidSourceModule
                    self.msg(2, "load_module: InvalidSourceModule", pathname,
                             exc)
            else:
                # no src available
                try:
                    co = loader.get_code(partname)
                    cls = (CompiledModule if co is not None
                           else InvalidCompiledModule)
                except Exception as exc:  # FIXME: more specific?
                    self.msg(2, "load_module: InvalidCompiledModule, "
                             "Cannot load code", pathname, exc)
                    cls = InvalidCompiledModule

        m = self.createNode(cls, fqname)
        m.filename = pathname

        self.msgout(2, "load_module ->", m)
        return (m, co)

    def _safe_import_hook(
        self, target_module_partname, source_module, target_attr_names,
        level=DEFAULT_IMPORT_LEVEL, edge_attr=None):
        """
        Import the module with the passed name and all parent packages of this
        module from the previously imported caller module signified by the
        passed graph node _without_ raising `ImportError` exceptions.

        This method wraps the lowel-level `_import_hook()` method. On catching
        an `ImportError` exception raised by that method, this method creates
        and adds a `MissingNode` instance describing the unimportable module to
        the graph instead.

        Parameters
        ----------
        target_module_partname : str
            Partially-qualified name of the module to be imported. If `level`
            is:
            * `ABSOLUTE_OR_RELATIVE_IMPORT_LEVEL` (e.g., the Python 2 default)
              or a positive integer (e.g., an explicit relative import), the
              fully-qualified name of this module is the concatenation of the
              fully-qualified name of the caller module's package and this
              parameter.
            * `ABSOLUTE_IMPORT_LEVEL` (e.g., the Python 3 default), this name
              is already fully-qualified.
            * A non-negative integer (e.g., `1`), this name is typically the
              empty string. In this case, this is a "from"-style relative
              import (e.g., "from . import bar") and the fully-qualified name
              of this module is dynamically resolved by import machinery.
        source_module : Node
            Graph node for the previously imported **caller module** (i.e.,
            module containing the `import` statement triggering the call to
            this method) _or_ `None` if this module is to be imported in a
            "disconnected" manner. **Passing `None` is _not_ recommended.**
            Doing so produces a disconnected graph in which the graph node
            created for the module to be imported will be disconnected and
            hence unreachable from all other nodes -- which frequently causes
            subtle issues in external callers (e.g., PyInstaller, which
            silently ignores unreachable nodes).
        target_attr_names : list
            List of the unqualified names of all submodules and attributes to
            be imported via a `from`-style import statement from this target
            module if any (e.g., the list `[encode_base64, encode_noop]` for
            the import `from email.encoders import encode_base64, encode_noop`)
            _or_ `None` otherwise. Ignored unless `source_module` is the graph
            node of a package (i.e., is an instance of the `Package` class).
            Why? Because:
            * Consistency. The `_import_importable_package_submodules()`
              method accepts a similar list applicable only to packages.
            * Efficiency. Unlike packages, modules cannot physically contain
              submodules. Hence, any target module imported via a `from`-style
              import statement as an attribute from another target parent
              module must itself have been imported in that target parent
              module. The import statement responsible for that import must
              already have been previously parsed by `ModuleGraph`, in which
              case that target module will already be frozen by PyInstaller.
              These imports are safely ignorable here.
        level : int
            Whether to perform an absolute or relative import. This parameter
            corresponds exactly to the parameter of the same name accepted by
            the `__import__()` built-in: "The default is -1 which indicates
            both absolute and relative imports will be attempted. 0 means only
            perform absolute imports. Positive values for level indicate the
            number of parent directories to search relative to the directory of
            the module calling `__import__()`." Defaults to -1 under Python 2
            and 0 under Python 3. Since this default depends on the major
            version of the current Python interpreter, depending on this
            default can result in unpredictable and non-portable behaviour.
            Callers are strongly recommended to explicitly pass this parameter
            rather than implicitly accept this default.

        Returns
        ----------
        list
            List of the graph nodes created for all modules explicitly imported
            by this call, including the passed module and all submodules listed
            in `target_attr_names` _but_ excluding all parent packages
            implicitly imported by this call. If `target_attr_names` is either
            `None` or the empty list, this is guaranteed to be a list of one
            element: the graph node created for the passed module. As above,
            `MissingNode` instances are created for all unimportable modules.
        """
        self.msg(3, "_safe_import_hook", target_module_partname, source_module, target_attr_names, level)

        def is_swig_candidate():
            return (source_module is not None and
                    target_attr_names is None and
                    level == ABSOLUTE_IMPORT_LEVEL and
                    type(source_module) is SourceModule and
                    target_module_partname ==
                      '_' + source_module.identifier.rpartition('.')[2])

        def is_swig_wrapper(source_module):
            with open(source_module.filename, 'rb') as fp:
                contents = fp.read()
            contents = importlib.util.decode_source(contents)
            first_line = contents.splitlines()[0] if contents else ''
            self.msg(5, 'SWIG wrapper candidate first line: %r' % (first_line))
            return "automatically generated by SWIG" in first_line


        # List of the graph nodes created for all target modules both
        # imported by and returned from this call, whose:
        #
        # * First element is the graph node for the core target module
        #   specified by the "target_module_partname" parameter.
        # * Remaining elements are the graph nodes for all target submodules
        #   specified by the "target_attr_names" parameter.
        target_modules = None

        # True if this is a Python 2-style implicit relative import of a
        # SWIG-generated C extension. False if we checked and it is not SWIG.
        # None if we haven't checked yet.
        is_swig_import = None

        # Attempt to import this target module in the customary way.
        try:
            target_modules = self.import_hook(
                target_module_partname, source_module,
                target_attr_names=None, level=level, edge_attr=edge_attr)
        # Failing that, defer to custom module importers handling non-standard
        # import schemes (namely, SWIG).
        except InvalidRelativeImportError:
            self.msgout(2, "Invalid relative import", level,
                        target_module_partname, target_attr_names)
            result = []
            for sub in target_attr_names or '*':
                m = self.createNode(InvalidRelativeImport,
                                    '.' * level + target_module_partname, sub)
                self._updateReference(source_module, m, edge_data=edge_attr)
                result.append(m)
            return result
        except ImportError as msg:
            # If this is an absolute top-level import under Python 3 and if the
            # name to be imported is the caller's name prefixed by "_", this
            # could be a SWIG-generated Python 2-style implicit relative import.
            # SWIG-generated files contain functions named swig_import_helper()
            # importing dynamic libraries residing in the same directory. For
            # example, a SWIG-generated caller module "csr.py" might resemble:
            #
            #     # This file was automatically generated by SWIG (http://www.swig.org).
            #     ...
            #     def swig_import_helper():
            #         ...
            #         try:
            #             fp, pathname, description = imp.find_module('_csr',
            #                   [dirname(__file__)])
            #         except ImportError:
            #             import _csr
            #             return _csr
            #
            # While there exists no reasonable means for modulegraph to parse
            # the call to imp.find_module(), the subsequent implicit relative
            # import is trivially parsable. This import is prohibited under
            # Python 3, however, and thus parsed only if the caller's file is
            # parsable plaintext (as indicated by a filetype of ".py") and the
            # first line of this file is the above SWIG header comment.
            #
            # The constraint that this library's name be the caller's name
            # prefixed by '_' is explicitly mandated by SWIG and thus a
            # reliable indicator of "SWIG-ness". The SWIG documentation states:
            # "When linking the module, the name of the output file has to match
            #  the name of the module prefixed by an underscore."
            #
            # Only source modules (e.g., ".py"-suffixed files) are SWIG import
            # candidates. All other node types are safely ignorable.
            if is_swig_candidate():
                self.msg(
                    4,
                    'SWIG import candidate (name=%r, caller=%r, level=%r)' % (
                        target_module_partname, source_module, level))
                is_swig_import = is_swig_wrapper(source_module)
                if is_swig_import:
                    # Convert this Python 2-compliant implicit relative
                    # import prohibited by Python 3 into a Python
                    # 3-compliant explicit relative "from"-style import for
                    # the duration of this function call by overwriting the
                    # original parameters passed to this call.
                    target_attr_names = [target_module_partname]
                    target_module_partname = ''
                    level = 1
                    self.msg(2,
                             'SWIG import (caller=%r, fromlist=%r, level=%r)'
                             % (source_module, target_attr_names, level))
                    # Import this target SWIG C extension's package.
                    try:
                        target_modules = self.import_hook(
                            target_module_partname, source_module,
                            target_attr_names=None,
                            level=level,
                            edge_attr=edge_attr)
                    except ImportError as msg:
                        self.msg(2, "SWIG ImportError:", str(msg))

            # If this module remains unimportable...
            if target_modules is None:
                self.msg(2, "ImportError:", str(msg))

                # Add this module as a MissingModule node.
                target_module = self.createNode(
                    MissingModule,
                    _path_from_importerror(msg, target_module_partname))
                self._updateReference(
                    source_module, target_module, edge_data=edge_attr)

                # Initialize this list to this node.
                target_modules = [target_module]

        # Ensure that the above logic imported exactly one target module.
        assert len(target_modules) == 1, (
            'Expected import_hook() to'
            'return only one module but received: {}'.format(target_modules))

        # Target module imported above.
        target_module = target_modules[0]

        if isinstance(target_module, MissingModule) \
           and is_swig_import is None and is_swig_candidate() \
           and is_swig_wrapper(source_module):
            # if this possible swig C module was previously imported from
            # a python module other than its corresponding swig python
            # module, then it may have been considered a MissingModule.
            # Try to reimport it now. For details see pull-request #2578
            # and issue #1522.
            #
            # If this module was takes as a SWIG candidate above, but failed
            # to import, this would be a MissingModule, too. Thus check if
            # this was the case (is_swig_import would be not None) to avoid
            # recursion error. If `is_swig_import` is None and we are still a
            # swig candidate then that means we haven't properly imported this
            # swig module yet so do that below.
            #
            # Remove the MissingModule node from the graph so that we can
            # attempt a reimport and avoid collisions. This node should be
            # fine to remove because the proper module will be imported and
            # added to the graph in the next line (call to _safe_import_hook).
            self.removeNode(target_module)
            # Reimport the SWIG C module relative to the wrapper
            target_modules = self._safe_import_hook(
                target_module_partname, source_module,
                target_attr_names=None, level=1, edge_attr=edge_attr)
            # return the output regardless because it would just be
            # duplicating the processing below
            return target_modules

        if isinstance(edge_attr, DependencyInfo):
            edge_attr = edge_attr._replace(fromlist=True)

        # If this is a "from"-style import *AND* this target module is a
        # package, import all attributes listed by the "import" clause of this
        # import that are submodules of this package. If this target module is
        # *NOT* a package, these attributes are always ignorable globals (e.g.,
        # classes, variables) defined at the top level of this module.
        #
        # If this target module is a non-package, it could still contain
        # importable submodules (e.g., the non-package `os` module containing
        # the `os.path` submodule). In this case, these submodules are already
        # imported by this target module's pure-Python code. Since our import
        # scanner already detects these imports, these submodules need *NOT* be
        # reimported here. (Doing so would be harmless but inefficient.)
        if target_attr_names and isinstance(target_module,
                                            (Package, AliasNode)):
            # For the name of each attribute imported from this target package
            # into this source module...
            for target_submodule_partname in target_attr_names:
                #FIXME: Is this optimization *REALLY* an optimization or at all
                #necessary? The findNode() method called below should already
                #be heavily optimized, in which case this optimization here is
                #premature, senseless, and should be eliminated.

                # If this attribute is a previously imported submodule of this
                # target module, optimize this edge case.
                if target_module.is_submodule(target_submodule_partname):
                    # Graph node for this submodule.
                    target_submodule = target_module.get_submodule(
                        target_submodule_partname)

                    #FIXME: What? Shouldn't "target_submodule" *ALWAYS* be
                    #non-None here? Assert this to be non-None instead.
                    if target_submodule is not None:
                        #FIXME: Why does duplication matter? List searches are
                        #mildly expensive.

                        # If this submodule has not already been added to the
                        # list of submodules to be returned, do so.
                        if target_submodule not in target_modules:
                            self._updateReference(
                                source_module,
                                target_submodule,
                                edge_data=edge_attr)
                            target_modules.append(target_submodule)
                        continue

                # Fully-qualified name of this submodule.
                target_submodule_name = (
                    target_module.identifier + '.' + target_submodule_partname)

                # Graph node of this submodule if previously imported or None.
                target_submodule = self.find_node(target_submodule_name)

                # If this submodule has not been imported, do so as if this
                # submodule were the only attribute listed by the "import"
                # clause of this import (e.g., as "from foo import bar" rather
                # than "from foo import car, far, bar").
                if target_submodule is None:
                    # Attempt to import this submodule.
                    try:
                        # Ignore the list of graph nodes returned by this
                        # method. If both this submodule's package and this
                        # submodule are importable, this method returns a
                        # 2-element list whose second element is this
                        # submodule's graph node. However, if this submodule's
                        # package is importable but this submodule is not,
                        # this submodule is either:
                        #
                        # * An ignorable global attribute defined at the top
                        #   level of this package's "__init__" submodule. In
                        #   this case, this method returns a 1-element list
                        #   without raising an exception.
                        # * A non-ignorable unimportable submodule. In this
                        #   case, this method raises an "ImportError".
                        #
                        # While the first two cases are disambiguatable by the
                        # length of this list, doing so would render this code
                        # dependent on import_hook() details subject to change.
                        # Instead, call findNode() to decide the truthiness.
                        self.import_hook(
                            target_module_partname, source_module,
                            target_attr_names=[target_submodule_partname],
                            level=level,
                            edge_attr=edge_attr)

                        # Graph node of this submodule imported by the prior
                        # call if importable or None otherwise.
                        target_submodule = self.find_node(target_submodule_name)

                        # If this submodule does not exist, this *MUST* be an
                        # ignorable global attribute defined at the top level
                        # of this package's "__init__" submodule.
                        if target_submodule is None:
                            # Assert this to actually be the case.
                            assert target_module.is_global_attr(
                                target_submodule_partname), (
                                'No global named {} in {}.__init__'.format(
                                    target_submodule_partname,
                                    target_module.identifier))

                            # Skip this safely ignorable importation to the
                            # next attribute. See similar logic in the body of
                            # _import_importable_package_submodules().
                            self.msg(4, '_safe_import_hook', 'ignoring imported non-module global', target_module.identifier, target_submodule_partname)
                            continue

                        # If this is a SWIG C extension, instruct PyInstaller
                        # to freeze this extension under its unqualified rather
                        # than qualified name (e.g., as "_csr" rather than
                        # "scipy.sparse.sparsetools._csr"), permitting the
                        # implicit relative import in its parent SWIG module to
                        # successfully find this extension.
                        if is_swig_import:
                            # If a graph node with this name already exists,
                            # avoid collisions by emitting an error instead.
                            if self.find_node(target_submodule_partname):
                                self.msg(
                                    2,
                                    'SWIG import error: %r basename %r '
                                    'already exists' % (
                                        target_submodule_name,
                                        target_submodule_partname))
                            else:
                                self.msg(
                                    4,
                                    'SWIG import renamed from %r to %r' % (
                                        target_submodule_name,
                                        target_submodule_partname))
                                target_submodule.identifier = (
                                    target_submodule_partname)
                    # If this submodule is unimportable, add a MissingModule.
                    except ImportError as msg:
                        self.msg(2, "ImportError:", str(msg))
                        target_submodule = self.createNode(
                            MissingModule, target_submodule_name)

                # Add this submodule to its package.
                target_module.add_submodule(
                    target_submodule_partname, target_submodule)
                if target_submodule is not None:
                    self._updateReference(
                        target_module, target_submodule, edge_data=edge_attr)
                    self._updateReference(
                        source_module, target_submodule, edge_data=edge_attr)

                    if target_submodule not in target_modules:
                        target_modules.append(target_submodule)

        # Return the list of all target modules imported by this call.
        return target_modules


    def _scan_code(
        self,
        module,
        module_code_object,
        module_code_object_ast=None):
        """
        Parse and add all import statements from the passed code object of the
        passed source module to this graph, recursively.

        **This method is at the root of all `ModuleGraph` recursion.**
        Recursion begins here and ends when all import statements in all code
        objects of all modules transitively imported by the source module
        passed to the first call to this method have been added to the graph.
        Specifically, this method:

        1. If the passed `module_code_object_ast` parameter is non-`None`,
           parses all import statements from this object.
        2. Else, parses all import statements from the passed
           `module_code_object` parameter.
        1. For each such import statement:
           1. Adds to this `ModuleGraph` instance:
              1. Nodes for all target modules of these imports.
              1. Directed edges from this source module to these target
                 modules.
           2. Recursively calls this method with these target modules.

        Parameters
        ----------
        module : Node
            Graph node of the module to be parsed.
        module_code_object : PyCodeObject
            Code object providing this module's disassembled Python bytecode.
            Ignored unless `module_code_object_ast` is `None`.
        module_code_object_ast : optional[ast.AST]
            Optional abstract syntax tree (AST) of this module if any or `None`
            otherwise. Defaults to `None`, in which case the passed
            `module_code_object` is parsed instead.
        Returns
        ----------
        module : Node
            Graph node of the module to be parsed.
        """

        # For safety, guard against multiple scans of the same module by
        # resetting this module's list of deferred target imports.
        module._deferred_imports = []

        # Parse all imports from this module *BEFORE* adding these imports to
        # the graph. If an AST is provided, parse that rather than this
        # module's code object.
        if module_code_object_ast is not None:
            # Parse this module's AST for imports.
            self._scan_ast(module, module_code_object_ast)

            # Parse this module's code object for all relevant non-imports
            # (e.g., global variable declarations and undeclarations).
            self._scan_bytecode(
                module, module_code_object, is_scanning_imports=False)
        # Else, parse this module's code object for imports.
        else:
            self._scan_bytecode(
                module, module_code_object, is_scanning_imports=True)

        return module

    def _scan_ast(self, module, module_code_object_ast):
        """
        Parse and add all import statements from the passed abstract syntax
        tree (AST) of the passed source module to this graph, non-recursively.

        Parameters
        ----------
        module : Node
            Graph node of the module to be parsed.
        module_code_object_ast : ast.AST
            Abstract syntax tree (AST) of this module to be parsed.
        """

        visitor = _Visitor(self, module)
        visitor.visit(module_code_object_ast)

    #FIXME: Optimize. Global attributes added by this method are tested by
    #other methods *ONLY* for packages, implying this method should scan and
    #handle opcodes pertaining to global attributes (e.g.,
    #"STORE_NAME", "DELETE_GLOBAL") only if the passed "module"
    #object is an instance of the "Package" class. For all other module types,
    #these opcodes should simply be ignored.
    #
    #After doing so, the "Node._global_attr_names" attribute and all methods
    #using this attribute (e.g., Node.is_global()) should be moved from the
    #"Node" superclass to the "Package" subclass.
    def _scan_bytecode(
        self, module, module_code_object, is_scanning_imports):
        """
        Parse and add all import statements from the passed code object of the
        passed source module to this graph, non-recursively.

        This method parses all reasonably parsable operations (i.e., operations
        that are both syntactically and semantically parsable _without_
        requiring Turing-complete interpretation) directly or indirectly
        involving module importation from this code object. This includes:

        * `IMPORT_NAME`, denoting an import statement. Ignored unless
          the passed `is_scanning_imports` parameter is `True`.
        * `STORE_NAME` and `STORE_GLOBAL`, denoting the
          declaration of a global attribute (e.g., class, variable) in this
          module. This method stores each such declaration for subsequent
          lookup. While global attributes are usually irrelevant to import
          parsing, they remain the only means of distinguishing erroneous
          non-ignorable attempts to import non-existent submodules of a package
          from successful ignorable attempts to import existing global
          attributes of a package's `__init__` submodule (e.g., the `bar` in
          `from foo import bar`, which is either a non-ignorable submodule of
          `foo` or an ignorable global attribute of `foo.__init__`).
        * `DELETE_NAME` and `DELETE_GLOBAL`, denoting the
          undeclaration of a previously declared global attribute in this
          module.

        Since `ModuleGraph` is _not_ intended to replicate the behaviour of a
        full-featured Turing-complete Python interpreter, this method ignores
        operations that are _not_ reasonably parsable from this code object --
        even those directly or indirectly involving module importation. This
        includes:

        * `STORE_ATTR(namei)`, implementing `TOS.name = TOS1`. If `TOS` is the
          name of a target module currently imported into the namespace of the
          passed source module, this opcode would ideally be parsed to add that
          global attribute to that target module. Since this addition only
          conditionally occurs on the importation of this source module and
          execution of the code branch in this module performing this addition,
          however, that global _cannot_ be unconditionally added to that target
          module. In short, only Turing-complete behaviour suffices.
        * `DELETE_ATTR(namei)`, implementing `del TOS.name`. If `TOS` is the
          name of a target module currently imported into the namespace of the
          passed source module, this opcode would ideally be parsed to remove
          that global attribute from that target module. Again, however, only
          Turing-complete behaviour suffices.

        Parameters
        ----------
        module : Node
            Graph node of the module to be parsed.
        module_code_object : PyCodeObject
            Code object of the module to be parsed.
        is_scanning_imports : bool
            `True` only if this method is parsing import statements from
            `IMPORT_NAME` opcodes. If `False`, no import statements will be
            parsed. This parameter is typically:
            * `True` when parsing this module's code object for such imports.
            * `False` when parsing this module's abstract syntax tree (AST)
              (rather than code object) for such imports. In this case, that
              parsing will have already parsed import statements, which this
              parsing must avoid repeating.
        """
        level = None
        fromlist = None

        # 'deque' is a list-like container with fast appends, pops on
        # either end, and automatically discarding elements too much.
        prev_insts = deque(maxlen=2)
        for inst in util.iterate_instructions(module_code_object):
            if not inst:
                continue
            # If this is an import statement originating from this module,
            # parse this import.
            #
            # Note that the related "IMPORT_FROM" opcode need *NOT* be parsed.
            # "IMPORT_NAME" suffices. For further details, see
            #     http://probablyprogramming.com/2008/04/14/python-import_name
            if inst.opname == 'IMPORT_NAME':
                # If this method is ignoring import statements, skip to the
                # next opcode.
                if not is_scanning_imports:
                    continue

                assert prev_insts[-2].opname == 'LOAD_CONST'
                assert prev_insts[-1].opname == 'LOAD_CONST'

                # Python >=2.5: LOAD_CONST flags, LOAD_CONST names, IMPORT_NAME name
                level = prev_insts[-2].argval
                fromlist = prev_insts[-1].argval

                assert fromlist is None or type(fromlist) is tuple
                target_module_partname = inst.argval

                #FIXME: The exact same logic appears in _collect_import(),
                #which isn't particularly helpful. Instead, defer this logic
                #until later by:
                #
                #* Refactor the "_deferred_imports" list to contain 2-tuples
                #  "(_safe_import_hook_args, _safe_import_hook_kwargs)" rather
                #  than 3-tuples "(have_star, _safe_import_hook_args,
                #  _safe_import_hook_kwargs)".
                #* Stop prepending these tuples by a "have_star" boolean both
                #  here, in _collect_import(), and in _process_imports().
                #* Shift the logic below to _process_imports().
                #* Remove the same logic from _collect_import().
                have_star = False
                if fromlist is not None:
                    fromlist = uniq(fromlist)
                    if '*' in fromlist:
                        fromlist.remove('*')
                        have_star = True

                # Record this import as originating from this module for
                # subsequent handling by the _process_imports() method.
                module._deferred_imports.append((
                    have_star,
                    (target_module_partname, module, fromlist, level),
                    {}
                ))

            elif inst.opname in ('STORE_NAME', 'STORE_GLOBAL'):
                # If this is the declaration of a global attribute (e.g.,
                # class, variable) in this module, store this declaration for
                # subsequent lookup. See method docstring for further details.
                #
                # Global attributes are usually irrelevant to import parsing, but
                # remain the only means of distinguishing erroneous non-ignorable
                # attempts to import non-existent submodules of a package from
                # successful ignorable attempts to import existing global
                # attributes of a package's "__init__" submodule (e.g., the "bar"
                # in "from foo import bar", which is either a non-ignorable
                # submodule of "foo" or an ignorable global attribute of
                # "foo.__init__").
                name = inst.argval
                module.add_global_attr(name)

            elif inst.opname in ('DELETE_NAME', 'DELETE_GLOBAL'):
                # If this is the undeclaration of a previously declared global
                # attribute (e.g., class, variable) in this module, remove that
                # declaration to prevent subsequent lookup. See method docstring
                # for further details.
                name = inst.argval
                module.remove_global_attr_if_found(name)

            prev_insts.append(inst)


    def _process_imports(self, source_module):
        """
        Graph all target modules whose importations were previously parsed from
        the passed source module by a prior call to the `_scan_code()` method
        and methods call by that method (e.g., `_scan_ast()`,
        `_scan_bytecode()`, `_scan_bytecode_stores()`).

        Parameters
        ----------
        source_module : Node
            Graph node of the source module to graph target imports for.
        """

        # If this source module imported no target modules, noop.
        if not source_module._deferred_imports:
            return

        # For each target module imported by this source module...
        for have_star, import_info, kwargs in source_module._deferred_imports:
            # Graph node of the target module specified by the "from" portion
            # of this "from"-style star import (e.g., an import resembling
            # "from {target_module_name} import *") or ignored otherwise.
            target_modules = self._safe_import_hook(*import_info, **kwargs)
            if not target_modules:
                # If _safe_import_hook suppressed the module, quietly drop it.
                # Do not create an ExcludedModule instance, because that might
                # completely suppress the module whereas it might need to be
                # included due to reference from another module (that does
                # not exclude it via hook).
                continue
            target_module = target_modules[0]

            # If this is a "from"-style star import, process this import.
            if have_star:
                #FIXME: Sadly, the current approach to importing attributes
                #from "from"-style star imports is... simplistic. This should
                #be revised as follows. If this target module is:
                #
                #* A package:
                #  * Whose "__init__" submodule defines the "__all__" global
                #    attribute, only attributes listed by this attribute should
                #    be imported.
                #  * Else, *NO* attributes should be imported.
                #* A non-package:
                #  * Defining the "__all__" global attribute, only attributes
                #    listed by this attribute should be imported.
                #  * Else, only public attributes whose names are *NOT*
                #    prefixed by "_" should be imported.
                source_module.add_global_attrs_from_module(target_module)

                source_module._starimported_ignored_module_names.update(
                    target_module._starimported_ignored_module_names)

                # If this target module has no code object and hence is
                # unparsable, record its name for posterity.
                if target_module.code is None:
                    target_module_name = import_info[0]
                    source_module._starimported_ignored_module_names.add(
                        target_module_name)

        # For safety, prevent these imports from being reprocessed.
        source_module._deferred_imports = None


    def _find_module(self, name, path, parent=None):
        """
        3-tuple describing the physical location of the module with the passed
        name if this module is physically findable _or_ raise `ImportError`.

        This high-level method wraps the low-level `modulegraph.find_module()`
        function with additional support for graph-based module caching.

        Parameters
        ----------
        name : str
            Fully-qualified name of the Python module to be found.
        path : list
            List of the absolute paths of all directories to search for this
            module _or_ `None` if the default path list `self.path` is to be
            searched.
        parent : Node
            Package containing this module if this module is a submodule of a
            package _or_ `None` if this is a top-level module.

        Returns
        ----------
        (filename, loader)
            See `modulegraph._find_module()` for details.

        Raises
        ----------
        ImportError
            If this module is _not_ found.
        """

        if parent is not None:
            # assert path is not None
            fullname = parent.identifier + '.' + name
        else:
            fullname = name

        node = self.find_node(fullname)
        if node is not None:
            self.msg(3, "find_module: already included?", node)
            raise ImportError(name)

        if path is None:
            if name in sys.builtin_module_names:
                return (None, BUILTIN_MODULE)

            path = self.path

        return self._find_module_path(fullname, name, path)


    def _find_module_path(self, fullname, module_name, search_dirs):
        """
        3-tuple describing the physical location of the module with the passed
        name if this module is physically findable _or_ raise `ImportError`.

        This low-level function is a variant on the standard `imp.find_module()`
        function with additional support for:

        * Multiple search paths. The passed list of absolute paths will be
          iteratively searched for the first directory containing a file
          corresponding to this module.
        * Compressed (e.g., zipped) packages.

        For efficiency, the higher level `ModuleGraph._find_module()` method
        wraps this function with support for module caching.

        Parameters
        ----------
        module_name : str
            Fully-qualified name of the module to be found.
        search_dirs : list
            List of the absolute paths of all directories to search for this
            module (in order). Searching will halt at the first directory
            containing this module.

        Returns
        ----------
        (filename, loader)
            2-tuple describing the physical location of this module, where:
            * `filename` is the absolute path of this file.
            * `loader` is the import loader.
              In case of a namespace package, this is a NAMESPACE_PACKAGE
              instance

        Raises
        ----------
        ImportError
            If this module is _not_ found.
        """
        self.msgin(4, "_find_module_path <-", fullname, search_dirs)

        # Top-level 2-tuple to be returned.
        path_data = None

        # List of the absolute paths of all directories comprising the
        # namespace package to which this module belongs if any.
        namespace_dirs = []

        try:
            for search_dir in search_dirs:
                # PEP 302-compliant importer making loaders for this directory.
                importer = pkgutil.get_importer(search_dir)

                # If this directory is not importable, continue.
                if importer is None:
                    # self.msg(4, "_find_module_path importer not found", search_dir)
                    continue

                # Get the PEP 302-compliant loader object loading this module.
                #
                # If this importer defines the PEP 451-compliant find_spec()
                # method, use that, and obtain loader from spec. This should
                # be available on python >= 3.4.
                if hasattr(importer, 'find_spec'):
                    loader = None
                    spec = importer.find_spec(module_name)
                    if spec is not None:
                        loader = spec.loader
                        namespace_dirs.extend(spec.submodule_search_locations or [])
                # Else if this importer defines the PEP 302-compliant find_loader()
                # method, use that.
                elif hasattr(importer, 'find_loader'):
                    loader, loader_namespace_dirs = importer.find_loader(
                        module_name)
                    namespace_dirs.extend(loader_namespace_dirs)
                # Else if this importer defines the Python 2-specific
                # find_module() method, fall back to that. Despite the method
                # name, this method returns a loader rather than a module.
                elif hasattr(importer, 'find_module'):
                    loader = importer.find_module(module_name)
                # Else, raise an exception.
                else:
                    raise ImportError(
                        "Module %r importer %r loader unobtainable" % (module_name, importer))

                # If this module is not loadable from this directory, continue.
                if loader is None:
                    # self.msg(4, "_find_module_path loader not found", search_dir)
                    continue

                # Absolute path of this module. If this module resides in a
                # compressed archive, this is the absolute path of this module
                # after extracting this module from that archive and hence
                # should not exist; else, this path should typically exist.
                pathname = None

                # If this loader defines the PEP 302-compliant get_filename()
                # method, preferably call that method first. Most if not all
                # loaders (including zipimporter objects) define this method.
                if hasattr(loader, 'get_filename'):
                    pathname = loader.get_filename(module_name)
                # Else if this loader provides a "path" attribute, defer to that.
                elif hasattr(loader, 'path'):
                    pathname = loader.path
                # Else, raise an exception.
                else:
                    raise ImportError(
                        "Module %r loader %r path unobtainable" % (module_name, loader))

                # If no path was found, this is probably a namespace package. In
                # such case, continue collecting namespace directories.
                if pathname is None:
                    self.msg(4, "_find_module_path path not found", pathname)
                    continue

                # Return such metadata.
                path_data = (pathname, loader)
                break
            # Else if this is a namespace package, return such metadata.
            else:
                if namespace_dirs:
                    path_data = (namespace_dirs[0],
                                 NAMESPACE_PACKAGE(namespace_dirs))
        except UnicodeDecodeError as exc:
            self.msgout(1, "_find_module_path -> unicode error", exc)
        # Ensure that exceptions are logged, as this function is typically
        # called by the import_module() method which squelches ImportErrors.
        except Exception as exc:
            self.msgout(4, "_find_module_path -> exception", exc)
            raise

        # If this module was not found, raise an exception.
        self.msgout(4, "_find_module_path ->", path_data)
        if path_data is None:
            raise ImportError("No module named " + repr(module_name))

        return path_data


    def create_xref(self, out=None):
        global header, footer, entry, contpl, contpl_linked, imports
        if out is None:
            out = sys.stdout
        scripts = []
        mods = []
        for mod in self.iter_graph():
            name = os.path.basename(mod.identifier)
            if isinstance(mod, Script):
                scripts.append((name, mod))
            else:
                mods.append((name, mod))
        scripts.sort()
        mods.sort()
        scriptnames = [sn for sn, m in scripts]
        scripts.extend(mods)
        mods = scripts

        title = "modulegraph cross reference for " + ', '.join(scriptnames)
        print(header % {"TITLE": title}, file=out)

        def sorted_namelist(mods):
            lst = [os.path.basename(mod.identifier) for mod in mods if mod]
            lst.sort()
            return lst
        for name, m in mods:
            content = ""
            if isinstance(m, BuiltinModule):
                content = contpl % {"NAME": name,
                                    "TYPE": "<i>(builtin module)</i>"}
            elif isinstance(m, Extension):
                content = contpl % {"NAME": name,
                                    "TYPE": "<tt>%s</tt>" % m.filename}
            else:
                url = urllib.request.pathname2url(m.filename or "")
                content = contpl_linked % {"NAME": name, "URL": url,
                                           'TYPE': m.__class__.__name__}
            oute, ince = map(sorted_namelist, self.get_edges(m))
            if oute:
                links = []
                for n in oute:
                    links.append("""  <a href="#%s">%s</a>\n""" % (n, n))
                # #8226 = bullet-point; can't use html-entities since the
                # test-suite uses xml.etree.ElementTree.XMLParser, which
                # does't supprot them.
                links = " &#8226; ".join(links)
                content += imports % {"HEAD": "imports", "LINKS": links}
            if ince:
                links = []
                for n in ince:
                    links.append("""  <a href="#%s">%s</a>\n""" % (n, n))
                # #8226 = bullet-point; can't use html-entities since the
                # test-suite uses xml.etree.ElementTree.XMLParser, which
                # does't supprot them.
                links = " &#8226; ".join(links)
                content += imports % {"HEAD": "imported by", "LINKS": links}
            print(entry % {"NAME": name, "CONTENT": content}, file=out)
        print(footer, file=out)

    def itergraphreport(self, name='G', flatpackages=()):
        # XXX: Can this be implemented using Dot()?
        nodes = list(map(self.graph.describe_node, self.graph.iterdfs(self)))
        describe_edge = self.graph.describe_edge
        edges = deque()
        packagenodes = set()
        packageidents = {}
        nodetoident = {}
        inpackages = {}
        mainedges = set()

        # XXX - implement
        flatpackages = dict(flatpackages)

        def nodevisitor(node, data, outgoing, incoming):
            if not isinstance(data, Node):
                return {'label': str(node)}
            #if isinstance(d, (ExcludedModule, MissingModule, BadModule)):
            #    return None
            s = '<f0> ' + type(data).__name__
            for i, v in enumerate(data.infoTuple()[:1], 1):
                s += '| <f%d> %s' % (i, v)
            return {'label': s, 'shape': 'record'}


        def edgevisitor(edge, data, head, tail):
            # XXX: This method nonsense, the edge
            # data is never initialized.
            if data == 'orphan':
                return {'style': 'dashed'}
            elif data == 'pkgref':
                return {'style': 'dotted'}
            return {}

        yield 'digraph %s {\ncharset="UTF-8";\n' % (name,)
        attr = dict(rankdir='LR', concentrate='true')
        cpatt = '%s="%s"'
        for item in attr.items():
            yield '\t%s;\n' % (cpatt % item,)

        # find all packages (subgraphs)
        for (node, data, outgoing, incoming) in nodes:
            nodetoident[node] = getattr(data, 'identifier', None)
            if isinstance(data, Package):
                packageidents[data.identifier] = node
                inpackages[node] = set([node])
                packagenodes.add(node)

        # create sets for subgraph, write out descriptions
        for (node, data, outgoing, incoming) in nodes:
            # update edges
            for edge in (describe_edge(e) for e in outgoing):
                edges.append(edge)

            # describe node
            yield '\t"%s" [%s];\n' % (
                node,
                ','.join([
                    (cpatt % item) for item in
                    nodevisitor(node, data, outgoing, incoming).items()
                ]),
            )

            inside = inpackages.get(node)
            if inside is None:
                inside = inpackages[node] = set()
            ident = nodetoident[node]
            if ident is None:
                continue
            pkgnode = packageidents.get(ident[:ident.rfind('.')])
            if pkgnode is not None:
                inside.add(pkgnode)

        graph = []
        subgraphs = {}
        for key in packagenodes:
            subgraphs[key] = []

        while edges:
            edge, data, head, tail = edges.popleft()
            if ((head, tail)) in mainedges:
                continue
            mainedges.add((head, tail))
            tailpkgs = inpackages[tail]
            common = inpackages[head] & tailpkgs
            if not common and tailpkgs:
                usepkgs = sorted(tailpkgs)
                if len(usepkgs) != 1 or usepkgs[0] != tail:
                    edges.append((edge, data, head, usepkgs[0]))
                    edges.append((edge, 'pkgref', usepkgs[-1], tail))
                    continue
            if common:
                common = common.pop()
                if tail == common:
                    edges.append((edge, data, tail, head))
                elif head == common:
                    subgraphs[common].append((edge, 'pkgref', head, tail))
                else:
                    edges.append((edge, data, common, head))
                    edges.append((edge, data, common, tail))

            else:
                graph.append((edge, data, head, tail))

        def do_graph(edges, tabs):
            edgestr = tabs + '"%s" -> "%s" [%s];\n'
            # describe edge
            for (edge, data, head, tail) in edges:
                attribs = edgevisitor(edge, data, head, tail)
                yield edgestr % (
                    head,
                    tail,
                    ','.join([(cpatt % item) for item in attribs.items()]),
                )

        for g, edges in subgraphs.items():
            yield '\tsubgraph "cluster_%s" {\n' % (g,)
            yield '\t\tlabel="%s";\n' % (nodetoident[g],)
            for s in do_graph(edges, '\t\t'):
                yield s
            yield '\t}\n'

        for s in do_graph(graph, '\t'):
            yield s

        yield '}\n'

    def graphreport(self, fileobj=None, flatpackages=()):
        if fileobj is None:
            fileobj = sys.stdout
        fileobj.writelines(self.itergraphreport(flatpackages=flatpackages))

    def report(self):
        """Print a report to stdout, listing the found modules with their
        paths, as well as modules that are missing, or seem to be missing.
        """
        print()
        print("%-15s %-25s %s" % ("Class", "Name", "File"))
        print("%-15s %-25s %s" % ("-----", "----", "----"))
        for m in sorted(self.iter_graph(), key=lambda n: n.identifier):
            print("%-15s %-25s %s" % (type(m).__name__, m.identifier, m.filename or ""))

    def _replace_paths_in_code(self, co):
        new_filename = original_filename = os.path.normpath(co.co_filename)
        for f, r in self.replace_paths:
            f = os.path.join(f, '')
            r = os.path.join(r, '')
            if original_filename.startswith(f):
                new_filename = r + original_filename[len(f):]
                break

        else:
            return co

        consts = list(co.co_consts)
        for i in range(len(consts)):
            if isinstance(consts[i], type(co)):
                consts[i] = self._replace_paths_in_code(consts[i])

        return co.replace(co_consts=tuple(consts), co_filename=new_filename)
