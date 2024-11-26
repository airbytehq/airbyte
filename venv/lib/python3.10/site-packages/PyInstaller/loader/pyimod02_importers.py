#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
PEP-302 and PEP-451 importers for frozen applications.
"""

# **NOTE** This module is used during bootstrap.
# Import *ONLY* builtin modules or modules that are collected into the base_library.zip archive.
# List of built-in modules: sys.builtin_module_names
# List of modules collected into base_library.zip: PyInstaller.compat.PY3_BASE_MODULES

import sys
import os
import io

import _frozen_importlib
import _thread

from pyimod01_archive import ArchiveReadError, ZlibArchiveReader

SYS_PREFIX = sys._MEIPASS + os.sep
SYS_PREFIXLEN = len(SYS_PREFIX)

# In Python 3, it is recommended to use class 'types.ModuleType' to create a new module. However, 'types' module is
# not a built-in module. The 'types' module uses this trick with using type() function:
imp_new_module = type(sys)

if sys.flags.verbose and sys.stderr:

    def trace(msg, *a):
        sys.stderr.write(msg % a)
        sys.stderr.write("\n")
else:

    def trace(msg, *a):
        pass


def _decode_source(source_bytes):
    """
    Decode bytes representing source code and return the string. Universal newline support is used in the decoding.
    Based on CPython's implementation of the same functionality:
    https://github.com/python/cpython/blob/3.9/Lib/importlib/_bootstrap_external.py#L679-L688
    """
    # Local import to avoid including `tokenize` and its dependencies in `base_library.zip`
    from tokenize import detect_encoding
    source_bytes_readline = io.BytesIO(source_bytes).readline
    encoding = detect_encoding(source_bytes_readline)
    newline_decoder = io.IncrementalNewlineDecoder(decoder=None, translate=True)
    return newline_decoder.decode(source_bytes.decode(encoding[0]))


class PyiFrozenImporterState:
    """
    An object encapsulating extra information for PyiFrozenImporter, to be stored in `ModuleSpec.loader_state`. Having
    a custom type allows us to verify that module spec indeed contains the original loader state data, as set by
    `PyiFrozenImporter.find_spec`.
    """
    def __init__(self, entry_name):
        # Module name, as recorded in the PYZ archive.
        self.pyz_entry_name = entry_name


class PyiFrozenImporter:
    """
    Load bytecode of Python modules from the executable created by PyInstaller.

    Python bytecode is zipped and appended to the executable.

    NOTE: PYZ format cannot be replaced by zipimport module.

    The problem is that we have no control over zipimport; for instance, it does not work if the zip file is embedded
    into a PKG that is appended to an executable, like we create in one-file mode.

    This used to be PEP-302 finder and loader class for the ``sys.meta_path`` hook. A PEP-302 finder requires method
    find_module() to return loader class with method load_module(). However, both of these methods were deprecated in
    python 3.4 by PEP-451 (see below). Therefore, this class now provides only optional extensions to the PEP-302
    importer protocol.

    This is also a PEP-451 finder and loader class for the ModuleSpec type import system. A PEP-451 finder requires
    method find_spec(), a PEP-451 loader requires methods exec_module(), load_module() and (optionally) create_module().
    All these methods are implemented in this one class.
    """
    def __init__(self):
        """
        Load, unzip and initialize the Zip archive bundled with the executable.
        """
        # Examine all items in sys.path and the one like /path/executable_name?117568 is the correct executable with
        # the bundled zip archive. Use this value for the ZlibArchiveReader class, and remove this item from sys.path.
        # It was needed only for PyiFrozenImporter class. Wrong path from sys.path raises an ArchiveReadError exception.
        for pyz_filepath in sys.path:
            try:
                # Unzip zip archive bundled with the executable.
                self._pyz_archive = ZlibArchiveReader(pyz_filepath, check_pymagic=True)

                # As no exception was raised, we can assume that ZlibArchiveReader was successfully loaded.
                # Let's remove 'pyz_filepath' from sys.path.
                trace("# PyInstaller: PyiFrozenImporter(%s)", pyz_filepath)
                sys.path.remove(pyz_filepath)
                break
            except IOError:
                # Item from sys.path is not ZlibArchiveReader; let's try next one.
                continue
            except ArchiveReadError:
                # Item from sys.path is not ZlibArchiveReader; let's try next one.
                continue
        else:
            # sys.path does not contain the filename of the executable with the bundled zip archive. Raise import error.
            raise ImportError("Cannot load frozen modules.")

        # Some runtime hooks might need access to the list of available frozen modules. Make them accessible as a set().
        self.toc = set(self._pyz_archive.toc.keys())

        # Some runtime hooks might need to traverse available frozen package/module hierarchy to simulate filesystem.
        # Such traversals can be efficiently implemented using a prefix tree (trie), whose computation we defer
        # until first access.
        self._lock = _thread.RLock()
        self._toc_tree = None

    @property
    def toc_tree(self):
        with self._lock:
            if self._toc_tree is None:
                self._toc_tree = self._build_pyz_prefix_tree()
            return self._toc_tree

    # Helper for computing PYZ prefix tree
    def _build_pyz_prefix_tree(self):
        tree = dict()
        for entry_name in self.toc:
            name_components = entry_name.split('.')
            current = tree
            if self._pyz_archive.is_package(entry_name):  # self.is_package() without unnecessary checks
                # Package; create new dictionary node for its modules
                for name_component in name_components:
                    current = current.setdefault(name_component, {})
            else:
                # Module; create the leaf node (empty string)
                for name_component in name_components[:-1]:
                    current = current.setdefault(name_component, {})
                current[name_components[-1]] = ''
        return tree

    # Private helper
    def _is_pep420_namespace_package(self, fullname):
        if fullname in self.toc:
            try:
                return self._pyz_archive.is_pep420_namespace_package(fullname)
            except Exception as e:
                raise ImportError(f'PyiFrozenImporter cannot handle module {fullname!r}') from e
        else:
            raise ImportError(f'PyiFrozenImporter cannot handle module {fullname!r}')

    #-- Optional Extensions to the PEP-302 Importer Protocol --

    def is_package(self, fullname):
        if fullname in self.toc:
            try:
                return self._pyz_archive.is_package(fullname)
            except Exception as e:
                raise ImportError(f'PyiFrozenImporter cannot handle module {fullname!r}') from e
        else:
            raise ImportError(f'PyiFrozenImporter cannot handle module {fullname!r}')

    def get_code(self, fullname):
        """
        Get the code object associated with the module.

        ImportError should be raised if module not found.
        """
        try:
            if fullname == '__main__':
                # Special handling for __main__ module; the bootloader should store code object to _pyi_main_co
                # attribute of the module.
                return sys.modules['__main__']._pyi_main_co

            # extract() returns None if fullname is not in the archive, and the subsequent subscription attempt raises
            # exception, which is turned into ImportError.
            return self._pyz_archive.extract(fullname)
        except Exception as e:
            raise ImportError(f'PyiFrozenImporter cannot handle module {fullname!r}') from e

    def get_source(self, fullname):
        """
        Method should return the source code for the module as a string.
        But frozen modules does not contain source code.

        Return None, unless the corresponding source file was explicitly collected to the filesystem.
        """
        if fullname in self.toc:
            # Try loading the .py file from the filesystem (only for collected modules)
            if self.is_package(fullname):
                fullname += '.__init__'
            filename = os.path.join(SYS_PREFIX, fullname.replace('.', os.sep) + '.py')
            try:
                # Read in binary mode, then decode
                with open(filename, 'rb') as fp:
                    source_bytes = fp.read()
                return _decode_source(source_bytes)
            except FileNotFoundError:
                pass
            return None
        else:
            # ImportError should be raised if module not found.
            raise ImportError('No module named ' + fullname)

    def get_data(self, path):
        """
        Returns the data as a string, or raises IOError if the file was not found. The data is always returned as if
        "binary" mode was used.

        The 'path' argument is a path that can be constructed by munging module.__file__ (or pkg.__path__ items).

        This assumes that the file in question was collected into frozen application bundle as a file, and is available
        on the filesystem. Older versions of PyInstaller also supported data embedded in the PYZ archive, but that has
        been deprecated in v6.
        """
        # Try to fetch the data from the filesystem. Since __file__ attribute works properly, just try to open the file
        # and read it.
        with open(path, 'rb') as fp:
            return fp.read()

    def get_filename(self, fullname):
        """
        This method should return the value that __file__ would be set to if the named module was loaded. If the module
        is not found, an ImportError should be raised.
        """
        # The absolute absolute path to the executable is taken from sys.prefix. In onefile mode it points to the temp
        # directory where files are unpacked by PyInstaller. Then, append the appropriate suffix (__init__.pyc for a
        # package, or just .pyc for a module).
        # Method is_package() will raise ImportError if module not found.
        if self.is_package(fullname):
            filename = os.path.join(SYS_PREFIX, fullname.replace('.', os.path.sep), '__init__.pyc')
        else:
            filename = os.path.join(SYS_PREFIX, fullname.replace('.', os.path.sep) + '.pyc')
        return filename

    def find_spec(self, fullname, path=None, target=None):
        """
        PEP-451 finder.find_spec() method for the ``sys.meta_path`` hook.

        fullname     fully qualified name of the module
        path         None for a top-level module, or package.__path__ for
                     submodules or subpackages.
        target       unused by this Finder

        Finders are still responsible for identifying, and typically creating, the loader that should be used to load a
        module. That loader will now be stored in the module spec returned by find_spec() rather than returned directly.
        As is currently the case without the PEP-452, if a loader would be costly to create, that loader can be designed
        to defer the cost until later.

        Finders must return ModuleSpec objects when find_spec() is called. This new method replaces find_module() and
        find_loader() (in the PathEntryFinder case). If a loader does not have find_spec(), find_module() and
        find_loader() are used instead, for backward-compatibility.
        """
        entry_name = None  # None means - no module found in this importer.

        # Try to handle module.__path__ modifications by the modules themselves. This needs to be done first in
        # order to support module overrides in alternative locations while we also have the original module
        # available at non-override location.
        if path is not None:
            # Reverse the fake __path__ we added to the package module into a dotted module name, and add the tail
            # module from fullname onto that to synthesize a new fullname.
            modname = fullname.rsplit('.')[-1]

            for p in path:
                if not p.startswith(SYS_PREFIX):
                    continue
                p = p[SYS_PREFIXLEN:]
                parts = p.split(os.sep)
                if not parts:
                    continue
                if not parts[0]:
                    parts = parts[1:]
                parts.append(modname)
                entry_name = ".".join(parts)
                if entry_name in self.toc:
                    trace("import %s as %s # PyInstaller PYZ (__path__ override: %s)", entry_name, fullname, p)
                    break
            else:
                entry_name = None

        if entry_name is None:
            # Either there was no path override, or the module was not available there. Check the fully qualified name
            # of the module directly.
            if fullname in self.toc:
                entry_name = fullname
                trace("import %s # PyInstaller PYZ", fullname)

        if entry_name is None:
            trace("# %s not found in PYZ", fullname)
            return None

        if self._is_pep420_namespace_package(entry_name):
            from importlib._bootstrap_external import _NamespacePath
            # PEP-420 namespace package; as per PEP 451, we need to return a spec with "loader" set to None
            # (a.k.a. not set)
            spec = _frozen_importlib.ModuleSpec(fullname, None, is_package=True)
            # Set submodule_search_locations, which seems to fill the __path__ attribute.
            # This needs to be an instance of `importlib._bootstrap_external._NamespacePath` for `importlib.resources`
            # to work correctly with the namespace package; otherwise `importlib.resources.files()` throws an
            # `ValueError('Invalid path')` due to this check:
            # https://github.com/python/cpython/blob/v3.11.5/Lib/importlib/resources/readers.py#L109-L110
            spec.submodule_search_locations = _NamespacePath(
                entry_name,
                [os.path.dirname(self.get_filename(entry_name))],
                # The `path_finder` argument must be a callable with two arguments (`name` and `path`) that
                # returns the spec - so we need to bind our `find_spec` via lambda.
                lambda name, path: self.find_spec(name, path),
            )
            return spec

        # origin has to be the filename
        origin = self.get_filename(entry_name)
        is_pkg = self.is_package(entry_name)

        spec = _frozen_importlib.ModuleSpec(
            fullname,
            self,
            is_package=is_pkg,
            origin=origin,
            # Provide the entry_name (name of module entry in the PYZ) for the loader to use during loading.
            loader_state=PyiFrozenImporterState(entry_name)
        )

        # Make the import machinery set __file__.
        # PEP 451 says: "has_location" is true if the module is locatable. In that case the spec's origin is used
        # as the location and __file__ is set to spec.origin. If additional location information is required
        # (e.g., zipimport), that information may be stored in spec.loader_state.
        spec.has_location = True

        # Set submodule_search_locations for packages. Seems to be required for importlib_resources from 3.2.0;
        # see issue #5395.
        if is_pkg:
            spec.submodule_search_locations = [os.path.dirname(self.get_filename(entry_name))]

        return spec

    def create_module(self, spec):
        """
        PEP-451 loader.create_module() method for the ``sys.meta_path`` hook.

        Loaders may also implement create_module() that will return a new module to exec. It may return None to indicate
        that the default module creation code should be used. One use case, though atypical, for create_module() is to
        provide a module that is a subclass of the builtin module type. Most loaders will not need to implement
        create_module().

        create_module() should properly handle the case where it is called more than once for the same spec/module. This
        may include returning None or raising ImportError.
        """
        # Contrary to what is defined in PEP-451, this method is not optional. We want the default results, so we simply
        # return None (which is handled for su my the import machinery).
        # See https://bugs.python.org/issue23014 for more information.
        return None

    def exec_module(self, module):
        """
        PEP-451 loader.exec_module() method for the ``sys.meta_path`` hook.

        Loaders will have a new method, exec_module(). Its only job is to "exec" the module and consequently populate
        the module's namespace. It is not responsible for creating or preparing the module object, nor for any cleanup
        afterward. It has no return value. exec_module() will be used during both loading and reloading.

        exec_module() should properly handle the case where it is called more than once. For some kinds of modules this
        may mean raising ImportError every time after the first time the method is called. This is particularly relevant
        for reloading, where some kinds of modules do not support in-place reloading.
        """
        spec = module.__spec__

        if isinstance(spec.loader_state, PyiFrozenImporterState):
            # Use the module name stored in the `loader_state`, which was set by our `find_spec()` implementation.
            # This is necessary to properly resolve aliased modules; for example, `module.__spec__.name` contains
            # `pkg_resources.extern.jaraco.text`, but the original name stored in `loader_state`, which we need
            # to use for code look-up, is `pkg_resources._vendor.jaraco.text`.
            module_name = spec.loader_state.pyz_entry_name
        elif isinstance(spec.loader_state, dict):
            # This seems to happen when `importlib.util.LazyLoader` is used, and our original `loader_state` is lost.
            # We could use `spec.name` and hope for the best, but that will likely fail with aliased modules (see
            # the comment in the branch above for an example).
            #
            # So try to reconstruct the original module name from the `origin` - which is essentially the reverse of
            # our `get_filename()` implementation.
            assert spec.origin.startswith(SYS_PREFIX)
            module_name = spec.origin[SYS_PREFIXLEN:].replace(os.sep, '.')
            if module_name.endswith('.pyc'):
                module_name = module_name[:-4]
            if module_name.endswith('.__init__'):
                module_name = module_name[:-9]
        else:
            raise RuntimeError(f"Module's spec contains loader_state of incompatible type: {type(spec.loader_state)}")

        bytecode = self.get_code(module_name)
        if bytecode is None:
            raise RuntimeError(f"Failed to retrieve bytecode for {spec.name!r}!")

        # Set by the import machinery
        assert hasattr(module, '__file__')

        # If `submodule_search_locations` is not None, this is a package; set __path__.
        if spec.submodule_search_locations is not None:
            # Since PYTHONHOME is set in bootloader, 'sys.prefix' points to the correct path where PyInstaller should
            # find bundled dynamic libraries. In one-file mode it points to the tmp directory where bundled files are
            # extracted at execution time.
            #
            # __path__ cannot be empty list because 'wx' module prepends something to it. It cannot contain value
            # 'sys.prefix' because 'xml.etree.cElementTree' fails otherwise.
            #
            # Set __path__ to point to 'sys.prefix/package/subpackage'.
            module.__path__ = [os.path.dirname(module.__file__)]

        exec(bytecode, module.__dict__)

    def get_resource_reader(self, fullname):
        """
        Return importlib.resource-compatible resource reader.
        """
        return PyiFrozenResourceReader(self, fullname)


class PyiFrozenResourceReader:
    """
    Resource reader for importlib.resources / importlib_resources support.

    Supports only on-disk resources, which should cover the typical use cases, i.e., the access to data files;
    PyInstaller collects data files onto filesystem, and as of v6.0.0, the embedded PYZ archive is guaranteed
    to contain only .pyc modules.

    When listing resources, source .py files will not be listed as they are not collected by default. Similarly,
    sub-directories that contained only .py files are not reconstructed on filesystem, so they will not be listed,
    either. If access to .py files is required for whatever reason, they need to be explicitly collected as data files
    anyway, which will place them on filesystem and make them appear as resources.

    For on-disk resources, we *must* return path compatible with pathlib.Path() in order to avoid copy to a temporary
    file, which might break under some circumstances, e.g., metpy with importlib_resources back-port, due to:
    https://github.com/Unidata/MetPy/blob/a3424de66a44bf3a92b0dcacf4dff82ad7b86712/src/metpy/plots/wx_symbols.py#L24-L25
    (importlib_resources tries to use 'fonts/wx_symbols.ttf' as a temporary filename suffix, which fails as it contains
    a separator).

    Furthermore, some packages expect files() to return either pathlib.Path or zipfile.Path, e.g.,
    https://github.com/tensorflow/datasets/blob/master/tensorflow_datasets/core/utils/resource_utils.py#L81-L97
    This makes implementation of mixed support for on-disk and embedded resources using importlib.abc.Traversable
    protocol rather difficult.

    So in order to maximize compatibility with unfrozen behavior, the below implementation is basically equivalent of
    importlib.readers.FileReader from python 3.10:
      https://github.com/python/cpython/blob/839d7893943782ee803536a47f1d4de160314f85/Lib/importlib/readers.py#L11
    and its underlying classes, importlib.abc.TraversableResources and importlib.abc.ResourceReader:
      https://github.com/python/cpython/blob/839d7893943782ee803536a47f1d4de160314f85/Lib/importlib/abc.py#L422
      https://github.com/python/cpython/blob/839d7893943782ee803536a47f1d4de160314f85/Lib/importlib/abc.py#L312
    """
    def __init__(self, importer, name):
        # Local import to avoid including `pathlib` and its dependencies in `base_library.zip`
        from pathlib import Path
        self.importer = importer
        self.path = Path(sys._MEIPASS).joinpath(*name.split('.'))

    def open_resource(self, resource):
        return self.files().joinpath(resource).open('rb')

    def resource_path(self, resource):
        return str(self.path.joinpath(resource))

    def is_resource(self, path):
        return self.files().joinpath(path).is_file()

    def contents(self):
        return (item.name for item in self.files().iterdir())

    def files(self):
        return self.path


def install():
    """
    Install PyiFrozenImporter class into the import machinery.

    This function installs the PyiFrozenImporter class into the import machinery of the running process. The importer
    is added to sys.meta_path. It could be added to sys.path_hooks, but sys.meta_path is processed by Python before
    looking at sys.path!

    The order of processing import hooks in sys.meta_path:

    1. built-in modules
    2. modules from the bundled ZIP archive
    3. C extension modules
    4. Modules from sys.path
    """
    # Ensure Python looks in the bundled zip archive for modules before any other places.
    importer = PyiFrozenImporter()
    sys.meta_path.append(importer)

    # On Windows there is importer _frozen_importlib.WindowsRegistryFinder that looks for Python modules in Windows
    # registry. The frozen executable should not look for anything in the Windows registry. Remove this importer
    # from sys.meta_path.
    for item in sys.meta_path:
        if hasattr(item, '__name__') and item.__name__ == 'WindowsRegistryFinder':
            sys.meta_path.remove(item)
            break
    # _frozen_importlib.PathFinder is also able to handle Python C extensions. However, PyInstaller needs its own
    # importer as it uses extension names like 'module.submodle.so' (instead of paths). As of Python 3.7.0b2, there
    # are several PathFinder instances (and duplicate ones) on sys.meta_path. This propobly is a bug, see
    # https://bugs.python.org/issue33128. Thus we need to move all of them to the end, and eliminate the duplicates.
    path_finders = []
    for item in reversed(sys.meta_path):
        if getattr(item, '__name__', None) == 'PathFinder':
            sys.meta_path.remove(item)
            if item not in path_finders:
                path_finders.append(item)
    sys.meta_path.extend(reversed(path_finders))
    # TODO: do we need _frozen_importlib.FrozenImporter in Python 3? Could it be also removed?

    # Set the FrozenImporter as loader for __main__, in order for python to treat __main__ as a module instead of
    # a built-in.
    try:
        sys.modules['__main__'].__loader__ = importer
    except Exception:
        pass

    # Apply hack for python >= 3.11 and its frozen stdlib modules.
    if sys.version_info >= (3, 11):
        _fixup_frozen_stdlib()


# A hack for python >= 3.11 and its frozen stdlib modules. Unless `sys._stdlib_dir` is set, these modules end up
# missing __file__ attribute, which causes problems with 3rd party code. At the time of writing, python interpreter
# configuration API does not allow us to influence `sys._stdlib_dir` - it always resets it to `None`. Therefore,
# we manually set the path, and fix __file__ attribute on modules.
def _fixup_frozen_stdlib():
    import _imp  # built-in

    # If sys._stdlib_dir is None or empty, override it with sys._MEIPASS
    if not sys._stdlib_dir:
        try:
            sys._stdlib_dir = sys._MEIPASS
        except AttributeError:
            pass

    # The sys._stdlib_dir set above should affect newly-imported python-frozen modules. However, most of them have
    # been already imported during python initialization and our bootstrap, so we need to retroactively fix their
    # __file__ attribute.
    for module_name, module in sys.modules.items():
        if not _imp.is_frozen(module_name):
            continue

        is_pkg = _imp.is_frozen_package(module_name)

        # Determine "real" name from __spec__.loader_state.
        loader_state = module.__spec__.loader_state

        orig_name = loader_state.origname
        if is_pkg:
            orig_name += '.__init__'

        # We set suffix to .pyc to be consistent with out PyiFrozenImporter.
        filename = os.path.join(sys._MEIPASS, *orig_name.split('.')) + '.pyc'

        # Fixup the __file__ attribute
        if not hasattr(module, '__file__'):
            try:
                module.__file__ = filename
            except AttributeError:
                pass

        # Fixup the loader_state.filename
        # Except for _frozen_importlib (importlib._bootstrap), whose loader_state.filename appears to be left at
        # None in python.
        if loader_state.filename is None and orig_name != 'importlib._bootstrap':
            loader_state.filename = filename
