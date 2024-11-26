Custom modifications of 3rd party libraries
===========================================

NOTE: PyInstaller does not extend PYTHONPATH (sys.path) with this directory
that contains bundled 3rd party libraries.

Some users complained that PyInstaller failed because their apps were using
too old versions of some libraries that PyInstaller uses too and that's why
extending sys.path was dropped.

All libraries are tweaked to be importable as::

    from PyInstaller.lib.LIB_NAME import xyz

In libraries replace imports like::

    from altgraph import y
    from modulegraph import z

with relative prefix::

    from ..altgraph import y
    from ..modulegraph import z


altgraph
----------

- add fixed version string to ./altgraph/__init__.py::

    # For PyInstaller/lib/ define the version here, since there is no
    # package-resource.
    __version__ = '0.13'


modulegraph
-----------

https://bitbucket.org/ronaldoussoren/modulegraph/downloads

- TODO Use official modulegraph version when following issue is resolved and pull request merged
  https://bitbucket.org/ronaldoussoren/modulegraph/issues/28/__main__-module-being-analyzed-for-wheel

- add fixed version string to ./modulegraph/__init__.py::

    # For PyInstaller/lib/ define the version here, since there is no
    # package-resource.
    __version__ = '0.13'

