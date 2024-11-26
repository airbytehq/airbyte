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
Code related to processing of import hooks.
"""

import glob
import os.path
import sys
import weakref

from PyInstaller import log as logging
from PyInstaller.building.utils import format_binaries_and_datas
from PyInstaller.compat import expand_path, importlib_load_source
from PyInstaller.depend.imphookapi import PostGraphAPI
from PyInstaller.exceptions import ImportErrorWhenRunningHook

logger = logging.getLogger(__name__)

# Safety check: Hook module names need to be unique. Duplicate names might occur if the cached PyuModuleGraph has an
# issue.
HOOKS_MODULE_NAMES = set()


class ModuleHookCache(dict):
    """
    Cache of lazily loadable hook script objects.

    This cache is implemented as a `dict` subclass mapping from the fully-qualified names of all modules with at
    least one hook script to lists of `ModuleHook` instances encapsulating these scripts. As a `dict` subclass,
    all cached module names and hook scripts are accessible via standard dictionary operations.

    Attributes
    ----------
    module_graph : ModuleGraph
        Current module graph.
    _hook_module_name_prefix : str
        String prefixing the names of all in-memory modules lazily loaded from cached hook scripts. See also the
        `hook_module_name_prefix` parameter passed to the `ModuleHook.__init__()` method.
    """

    _cache_id_next = 0
    """
    0-based identifier unique to the next `ModuleHookCache` to be instantiated.

    This identifier is incremented on each instantiation of a new `ModuleHookCache` to isolate in-memory modules of
    lazily loaded hook scripts in that cache to the same cache-specific namespace, preventing edge-case collisions
    with existing in-memory modules in other caches.

    """
    def __init__(self, module_graph, hook_dirs):
        """
        Cache all hook scripts in the passed directories.

        **Order of caching is significant** with respect to hooks for the same module, as the values of this
        dictionary are lists. Hooks for the same module will be run in the order in which they are cached. Previously
        cached hooks are always preserved rather than overridden.

        By default, official hooks are cached _before_ user-defined hooks. For modules with both official and
        user-defined hooks, this implies that the former take priority over and hence will be loaded _before_ the
        latter.

        Parameters
        ----------
        module_graph : ModuleGraph
            Current module graph.
        hook_dirs : list
            List of the absolute or relative paths of all directories containing **hook scripts** (i.e.,
            Python scripts with filenames matching `hook-{module_name}.py`, where `{module_name}` is the module
            hooked by that script) to be cached.
        """
        super().__init__()

        # To avoid circular references and hence increased memory consumption, a weak rather than strong reference is
        # stored to the passed graph. Since this graph is guaranteed to live longer than this cache,
        # this is guaranteed to be safe.
        self.module_graph = weakref.proxy(module_graph)

        # String unique to this cache prefixing the names of all in-memory modules lazily loaded from cached hook
        # scripts, privatized for safety.
        self._hook_module_name_prefix = '__PyInstaller_hooks_{}_'.format(ModuleHookCache._cache_id_next)
        ModuleHookCache._cache_id_next += 1

        # Cache all hook scripts in the passed directories.
        self._cache_hook_dirs(hook_dirs)

    def _cache_hook_dirs(self, hook_dirs):
        """
        Cache all hook scripts in the passed directories.

        Parameters
        ----------
        hook_dirs : list
            List of the absolute or relative paths of all directories containing hook scripts to be cached.
        """

        for hook_dir in hook_dirs:
            # Canonicalize this directory's path and validate its existence.
            hook_dir = os.path.abspath(expand_path(hook_dir))
            if not os.path.isdir(hook_dir):
                raise FileNotFoundError('Hook directory "{}" not found.'.format(hook_dir))

            # For each hook script in this directory...
            hook_filenames = glob.glob(os.path.join(hook_dir, 'hook-*.py'))
            for hook_filename in hook_filenames:
                # Fully-qualified name of this hook's corresponding module, constructed by removing the "hook-" prefix
                # and ".py" suffix.
                module_name = os.path.basename(hook_filename)[5:-3]

                # Lazily loadable hook object.
                module_hook = ModuleHook(
                    module_graph=self.module_graph,
                    module_name=module_name,
                    hook_filename=hook_filename,
                    hook_module_name_prefix=self._hook_module_name_prefix,
                )

                # Add this hook to this module's list of hooks.
                module_hooks = self.setdefault(module_name, [])
                module_hooks.append(module_hook)

    def remove_modules(self, *module_names):
        """
        Remove the passed modules and all hook scripts cached for these modules from this cache.

        Parameters
        ----------
        module_names : list
            List of all fully-qualified module names to be removed.
        """

        for module_name in module_names:
            # Unload this module's hook script modules from memory. Since these are top-level pure-Python modules cached
            # only in the "sys.modules" dictionary, popping these modules from this dictionary suffices to garbage
            # collect these modules.
            module_hooks = self.get(module_name, [])
            for module_hook in module_hooks:
                sys.modules.pop(module_hook.hook_module_name, None)

            # Remove this module and its hook script objects from this cache.
            self.pop(module_name, None)


def _module_collection_mode_sanitizer(value):
    if isinstance(value, dict):
        # Hook set a dictionary; use it as-is
        return value
    elif isinstance(value, str):
        # Hook set a mode string; convert to a dictionary and assign the string to `None` (= the hooked module).
        return {None: value}

    raise ValueError(f"Invalid module collection mode setting value: {value!r}")


# Dictionary mapping the names of magic attributes required by the "ModuleHook" class to 2-tuples "(default_type,
# sanitizer_func)", where:
#
# * "default_type" is the type to which that attribute will be initialized when that hook is lazily loaded.
# * "sanitizer_func" is the callable sanitizing the original value of that attribute defined by that hook into a
#   safer value consumable by "ModuleHook" callers if any or "None" if the original value requires no sanitization.
#
# To avoid subtleties in the ModuleHook.__getattr__() method, this dictionary is declared as a module rather than a
# class attribute. If declared as a class attribute and then undefined (...for whatever reason), attempting to access
# this attribute from that method would produce infinite recursion.
_MAGIC_MODULE_HOOK_ATTRS = {
    # Collections in which order is insignificant. This includes:
    #
    # * "datas", sanitized from hook-style 2-tuple lists defined by hooks into TOC-style 2-tuple sets consumable by
    #   "ModuleHook" callers.
    # * "binaries", sanitized in the same way.
    'datas': (set, format_binaries_and_datas),
    'binaries': (set, format_binaries_and_datas),
    'excludedimports': (set, None),

    # Collections in which order is significant. This includes:
    #
    # * "hiddenimports", as order of importation is significant. On module importation, hook scripts are loaded and hook
    #   functions declared by these scripts are called. As these scripts and functions can have side effects dependent
    #   on module importation order, module importation itself can have side effects dependent on this order!
    'hiddenimports': (list, None),

    # Flags
    'warn_on_missing_hiddenimports': (lambda: True, bool),

    # Package/module collection mode dictionary.
    'module_collection_mode': (dict, _module_collection_mode_sanitizer),
}


class ModuleHook:
    """
    Cached object encapsulating a lazy loadable hook script.

    This object exposes public attributes (e.g., `datas`) of the underlying hook script as attributes of the same
    name of this object. On the first access of any such attribute, this hook script is lazily loaded into an
    in-memory private module reused on subsequent accesses. These dynamic attributes are referred to as "magic." All
    other static attributes of this object (e.g., `hook_module_name`) are referred to as "non-magic."

    Attributes (Magic)
    ----------
    datas : set
        Set of `TOC`-style 2-tuples `(target_file, source_file)` for all external non-executable files required by
        the module being hooked, converted from the `datas` list of hook-style 2-tuples `(source_dir_or_glob,
        target_dir)` defined by this hook script.
    binaries : set
        Set of `TOC`-style 2-tuples `(target_file, source_file)` for all external executable files required by the
        module being hooked, converted from the `binaries` list of hook-style 2-tuples `(source_dir_or_glob,
        target_dir)` defined by this hook script.
    excludedimports : set
        Set of the fully-qualified names of all modules imported by the module being hooked to be ignored rather than
        imported from that module, converted from the `excludedimports` list defined by this hook script. These
        modules will only be "locally" rather than "globally" ignored. These modules will remain importable from all
        modules other than the module being hooked.
    hiddenimports : set
        Set of the fully-qualified names of all modules imported by the module being hooked that are _not_
        automatically detectable by PyInstaller (usually due to being dynamically imported in that module),
        converted from the `hiddenimports` list defined by this hook script.
    warn_on_missing_hiddenimports : bool
        Boolean flag indicating whether missing hidden imports from the hook should generate warnings or not. This
        behavior is enabled by default, but individual hooks can opt out of it.
    module_collection_mode : dict
        A dictionary of package/module names and their corresponding collection mode strings ('pyz', 'pyc', 'py',
        'pyz+py', 'py+pyz').

    Attributes (Non-magic)
    ----------
    module_graph : ModuleGraph
        Current module graph.
    module_name : str
        Name of the module hooked by this hook script.
    hook_filename : str
        Absolute or relative path of this hook script.
    hook_module_name : str
        Name of the in-memory module of this hook script's interpreted contents.
    _hook_module : module
        In-memory module of this hook script's interpreted contents, lazily loaded on the first call to the
        `_load_hook_module()` method _or_ `None` if this method has yet to be accessed.
    """

    #-- Magic --

    def __init__(self, module_graph, module_name, hook_filename, hook_module_name_prefix):
        """
        Initialize this metadata.

        Parameters
        ----------
        module_graph : ModuleGraph
            Current module graph.
        module_name : str
            Name of the module hooked by this hook script.
        hook_filename : str
            Absolute or relative path of this hook script.
        hook_module_name_prefix : str
            String prefixing the name of the in-memory module for this hook script. To avoid namespace clashes with
            similar modules created by other `ModuleHook` objects in other `ModuleHookCache` containers, this string
            _must_ be unique to the `ModuleHookCache` container containing this `ModuleHook` object. If this string
            is non-unique, an existing in-memory module will be erroneously reused when lazily loading this hook
            script, thus erroneously resanitizing previously sanitized hook script attributes (e.g., `datas`) with
            the `format_binaries_and_datas()` helper.

        """
        # Note that the passed module graph is already a weak reference, avoiding circular reference issues. See
        # ModuleHookCache.__init__(). TODO: Add a failure message
        assert isinstance(module_graph, weakref.ProxyTypes)
        self.module_graph = module_graph
        self.module_name = module_name
        self.hook_filename = hook_filename

        # Name of the in-memory module fabricated to refer to this hook script.
        self.hook_module_name = hook_module_name_prefix + self.module_name.replace('.', '_')

        # Safety check, see above
        global HOOKS_MODULE_NAMES
        if self.hook_module_name in HOOKS_MODULE_NAMES:
            # When self._shallow is true, this class never loads the hook and sets the attributes to empty values
            self._shallow = True
        else:
            self._shallow = False
            HOOKS_MODULE_NAMES.add(self.hook_module_name)

        # Attributes subsequently defined by the _load_hook_module() method.
        self._loaded = False
        self._has_hook_function = False
        self._hook_module = None

    def __getattr__(self, attr_name):
        """
        Get the magic attribute with the passed name (e.g., `datas`) from this lazily loaded hook script if any _or_
        raise `AttributeError` otherwise.

        This special method is called only for attributes _not_ already defined by this object. This includes
        undefined attributes and the first attempt to access magic attributes.

        This special method is _not_ called for subsequent attempts to access magic attributes. The first attempt to
        access magic attributes defines corresponding instance variables accessible via the `self.__dict__` instance
        dictionary (e.g., as `self.datas`) without calling this method. This approach also allows magic attributes to
        be deleted from this object _without_ defining the `__delattr__()` special method.

        See Also
        ----------
        Class docstring for supported magic attributes.
        """

        # If this is a magic attribute, initialize this attribute by lazy loading this hook script and then return
        # this attribute.
        if attr_name in _MAGIC_MODULE_HOOK_ATTRS and not self._loaded:
            self._load_hook_module()
            return getattr(self, attr_name)
        # Else, this is an undefined attribute. Raise an exception.
        else:
            raise AttributeError(attr_name)

    def __setattr__(self, attr_name, attr_value):
        """
        Set the attribute with the passed name to the passed value.

        If this is a magic attribute, this hook script will be lazily loaded before setting this attribute. Unlike
        `__getattr__()`, this special method is called to set _any_ attribute -- including magic, non-magic,
        and undefined attributes.

        See Also
        ----------
        Class docstring for supported magic attributes.
        """

        # If this is a magic attribute, initialize this attribute by lazy loading this hook script before overwriting
        # this attribute.
        if attr_name in _MAGIC_MODULE_HOOK_ATTRS:
            self._load_hook_module()

        # Set this attribute to the passed value. To avoid recursion, the superclass method rather than setattr() is
        # called.
        return super().__setattr__(attr_name, attr_value)

    #-- Loading --

    def _load_hook_module(self, keep_module_ref=False):
        """
        Lazily load this hook script into an in-memory private module.

        This method (and, indeed, this class) preserves all attributes and functions defined by this hook script as
        is, ensuring sane behaviour in hook functions _not_ expecting unplanned external modification. Instead,
        this method copies public attributes defined by this hook script (e.g., `binaries`) into private attributes
        of this object, which the special `__getattr__()` and `__setattr__()` methods safely expose to external
        callers. For public attributes _not_ defined by this hook script, the corresponding private attributes will
        be assigned sane defaults. For some public attributes defined by this hook script, the corresponding private
        attributes will be transformed into objects more readily and safely consumed elsewhere by external callers.

        See Also
        ----------
        Class docstring for supported attributes.
        """

        # If this hook script module has already been loaded, or we are _shallow, noop.
        if (self._loaded and (self._hook_module is not None or not keep_module_ref)) or self._shallow:
            if self._shallow:
                self._loaded = True
                self._hook_module = True  # Not None
                # Inform the user
                logger.debug(
                    'Skipping module hook %r from %r because a hook for %s has already been loaded.',
                    *os.path.split(self.hook_filename)[::-1], self.module_name
                )
                # Set the default attributes to empty instances of the type.
                for attr_name, (attr_type, _) in _MAGIC_MODULE_HOOK_ATTRS.items():
                    super().__setattr__(attr_name, attr_type())
            return

        # Load and execute the hook script. Even if mechanisms from the import machinery are used, this does not import
        # the hook as the module.
        head, tail = os.path.split(self.hook_filename)
        logger.info('Loading module hook %r from %r...', tail, head)
        try:
            self._hook_module = importlib_load_source(self.hook_module_name, self.hook_filename)
        except ImportError:
            logger.debug("Hook failed with:", exc_info=True)
            raise ImportErrorWhenRunningHook(self.hook_module_name, self.hook_filename)

        # Mark as loaded
        self._loaded = True

        # Check if module has hook() function.
        self._has_hook_function = hasattr(self._hook_module, 'hook')

        # Copy hook script attributes into magic attributes exposed as instance variables of the current "ModuleHook"
        # instance.
        for attr_name, (default_type, sanitizer_func) in _MAGIC_MODULE_HOOK_ATTRS.items():
            # Unsanitized value of this attribute.
            attr_value = getattr(self._hook_module, attr_name, None)

            # If this attribute is undefined, expose a sane default instead.
            if attr_value is None:
                attr_value = default_type()
            # Else if this attribute requires sanitization, do so.
            elif sanitizer_func is not None:
                attr_value = sanitizer_func(attr_value)
            # Else, expose the unsanitized value of this attribute.

            # Expose this attribute as an instance variable of the same name.
            setattr(self, attr_name, attr_value)

        # If module_collection_mode has an entry with None key, reassign it to the hooked module's name.
        setattr(
            self, 'module_collection_mode', {
                key if key is not None else self.module_name: value
                for key, value in getattr(self, 'module_collection_mode').items()
            }
        )

        # Release the module if we do not need the reference. This is the case when hook is loaded during the analysis
        # rather as part of the post-graph operations.
        if not keep_module_ref:
            self._hook_module = None

    #-- Hooks --

    def post_graph(self, analysis):
        """
        Call the **post-graph hook** (i.e., `hook()` function) defined by this hook script, if any.

        Parameters
        ----------
        analysis: build_main.Analysis
            Analysis that calls the hook

        This method is intended to be called _after_ the module graph for this application is constructed.
        """

        # Lazily load this hook script into an in-memory module.
        # The script might have been loaded before during modulegraph analysis; in that case, it needs to be reloaded
        # only if it provides a hook() function.
        if not self._loaded or self._has_hook_function:
            # Keep module reference when loading the hook, so we can call its hook function!
            self._load_hook_module(keep_module_ref=True)

            # Call this hook script's hook() function, which modifies attributes accessed by subsequent methods and
            # hence must be called first.
            self._process_hook_func(analysis)

        # Order is insignificant here.
        self._process_hidden_imports()

    def _process_hook_func(self, analysis):
        """
        Call this hook's `hook()` function if defined.

        Parameters
        ----------
        analysis: build_main.Analysis
            Analysis that calls the hook
        """

        # If this hook script defines no hook() function, noop.
        if not hasattr(self._hook_module, 'hook'):
            return

        # Call this hook() function.
        hook_api = PostGraphAPI(module_name=self.module_name, module_graph=self.module_graph, analysis=analysis)
        try:
            self._hook_module.hook(hook_api)
        except ImportError:
            logger.debug("Hook failed with:", exc_info=True)
            raise ImportErrorWhenRunningHook(self.hook_module_name, self.hook_filename)

        # Update all magic attributes modified by the prior call.
        self.datas.update(set(hook_api._added_datas))
        self.binaries.update(set(hook_api._added_binaries))
        self.hiddenimports.extend(hook_api._added_imports)
        self.module_collection_mode.update(hook_api._module_collection_mode)

        # FIXME: `hook_api._deleted_imports` should be appended to `self.excludedimports` and used to suppress module
        # import during the modulegraph construction rather than handled here. However, for that to work, the `hook()`
        # function needs to be ran during modulegraph construction instead of in post-processing (and this in turn
        # requires additional code refactoring in order to be able to pass `analysis` to `PostGraphAPI` object at
        # that point). So once the modulegraph rewrite is complete, remove the code block below.
        for deleted_module_name in hook_api._deleted_imports:
            # Remove the graph link between the hooked module and item. This removes the 'item' node from the graph if
            # no other links go to it (no other modules import it)
            self.module_graph.removeReference(hook_api.node, deleted_module_name)

    def _process_hidden_imports(self):
        """
        Add all imports listed in this hook script's `hiddenimports` attribute to the module graph as if directly
        imported by this hooked module.

        These imports are typically _not_ implicitly detectable by PyInstaller and hence must be explicitly defined
        by hook scripts.
        """

        # For each hidden import required by the module being hooked...
        for import_module_name in self.hiddenimports:
            try:
                # Graph node for this module. Do not implicitly create namespace packages for non-existent packages.
                caller = self.module_graph.find_node(self.module_name, create_nspkg=False)

                # Manually import this hidden import from this module.
                self.module_graph.import_hook(import_module_name, caller)
            # If this hidden import is unimportable, print a non-fatal warning. Hidden imports often become
            # desynchronized from upstream packages and hence are only "soft" recommendations.
            except ImportError:
                if self.warn_on_missing_hiddenimports:
                    logger.warning('Hidden import "%s" not found!', import_module_name)


class AdditionalFilesCache:
    """
    Cache for storing what binaries and datas were pushed by what modules when import hooks were processed.
    """
    def __init__(self):
        self._binaries = {}
        self._datas = {}

    def add(self, modname, binaries, datas):

        self._binaries.setdefault(modname, [])
        self._binaries[modname].extend(binaries or [])
        self._datas.setdefault(modname, [])
        self._datas[modname].extend(datas or [])

    def __contains__(self, name):
        return name in self._binaries or name in self._datas

    def binaries(self, modname):
        """
        Return list of binaries for given module name.
        """
        return self._binaries.get(modname, [])

    def datas(self, modname):
        """
        Return list of datas for given module name.
        """
        return self._datas.get(modname, [])
