#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""ExtensionManager
"""

import logging
import operator

from . import _cache
from .exception import NoMatches

LOG = logging.getLogger(__name__)


class Extension(object):
    """Book-keeping object for tracking extensions.

    The arguments passed to the constructor are saved as attributes of
    the instance using the same names, and can be accessed by the
    callables passed to :meth:`map` or when iterating over an
    :class:`ExtensionManager` directly.

    :param name: The entry point name.
    :type name: str
    :param entry_point: The EntryPoint instance returned by
        :mod:`entrypoints`.
    :type entry_point: EntryPoint
    :param plugin: The value returned by entry_point.load()
    :param obj: The object returned by ``plugin(*args, **kwds)`` if the
                manager invoked the extension on load.

    """

    def __init__(self, name, entry_point, plugin, obj):
        self.name = name
        self.entry_point = entry_point
        self.plugin = plugin
        self.obj = obj

    @property
    def module_name(self):
        """The name of the module from which the entry point is loaded.

        :return: A string in 'dotted.module' format.
        """
        # NOTE: importlib_metadata from PyPI includes this but the
        # Python 3.8 standard library does not.
        match = self.entry_point.pattern.match(self.entry_point.value)
        return match.group('module')

    @property
    def attr(self):
        """The attribute of the module to be loaded."""
        match = self.entry_point.pattern.match(self.entry_point.value)
        return match.group('attr')

    @property
    def entry_point_target(self):
        """The module and attribute referenced by this extension's entry_point.

        :return: A string representation of the target of the entry point in
            'dotted.module:object' format.
        """
        return self.entry_point.value


class ExtensionManager(object):
    """Base class for all of the other managers.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param invoke_on_load: Boolean controlling whether to invoke the
        object returned by the entry point after the driver is loaded.
    :type invoke_on_load: bool
    :param invoke_args: Positional arguments to pass when invoking
        the object returned by the entry point. Only used if invoke_on_load
        is True.
    :type invoke_args: tuple
    :param invoke_kwds: Named arguments to pass when invoking
        the object returned by the entry point. Only used if invoke_on_load
        is True.
    :type invoke_kwds: dict
    :param propagate_map_exceptions: Boolean controlling whether exceptions
        are propagated up through the map call or whether they are logged and
        then ignored
    :type propagate_map_exceptions: bool
    :param on_load_failure_callback: Callback function that will be called when
        an entrypoint can not be loaded. The arguments that will be provided
        when this is called (when an entrypoint fails to load) are
        (manager, entrypoint, exception)
    :type on_load_failure_callback: function
    :param verify_requirements: Use setuptools to enforce the
        dependencies of the plugin(s) being loaded. Defaults to False.
    :type verify_requirements: bool
    """

    def __init__(self, namespace,
                 invoke_on_load=False,
                 invoke_args=(),
                 invoke_kwds={},
                 propagate_map_exceptions=False,
                 on_load_failure_callback=None,
                 verify_requirements=False):
        self._init_attributes(
            namespace,
            propagate_map_exceptions=propagate_map_exceptions,
            on_load_failure_callback=on_load_failure_callback)
        extensions = self._load_plugins(invoke_on_load,
                                        invoke_args,
                                        invoke_kwds,
                                        verify_requirements)
        self._init_plugins(extensions)

    @classmethod
    def make_test_instance(cls, extensions, namespace='TESTING',
                           propagate_map_exceptions=False,
                           on_load_failure_callback=None,
                           verify_requirements=False):
        """Construct a test ExtensionManager

        Test instances are passed a list of extensions to work from rather
        than loading them from entry points.

        :param extensions: Pre-configured Extension instances to use
        :type extensions: list of :class:`~stevedore.extension.Extension`
        :param namespace: The namespace for the manager; used only for
            identification since the extensions are passed in.
        :type namespace: str
        :param propagate_map_exceptions: When calling map, controls whether
            exceptions are propagated up through the map call or whether they
            are logged and then ignored
        :type propagate_map_exceptions: bool
        :param on_load_failure_callback: Callback function that will
            be called when an entrypoint can not be loaded. The
            arguments that will be provided when this is called (when
            an entrypoint fails to load) are (manager, entrypoint,
            exception)
        :type on_load_failure_callback: function
        :param verify_requirements: Use setuptools to enforce the
            dependencies of the plugin(s) being loaded. Defaults to False.
        :type verify_requirements: bool
        :return: The manager instance, initialized for testing

        """

        o = cls.__new__(cls)
        o._init_attributes(namespace,
                           propagate_map_exceptions=propagate_map_exceptions,
                           on_load_failure_callback=on_load_failure_callback)
        o._init_plugins(extensions)
        return o

    def _init_attributes(self, namespace, propagate_map_exceptions=False,
                         on_load_failure_callback=None):
        self.namespace = namespace
        self.propagate_map_exceptions = propagate_map_exceptions
        self._on_load_failure_callback = on_load_failure_callback

    def _init_plugins(self, extensions):
        self.extensions = extensions
        self._extensions_by_name_cache = None

    @property
    def _extensions_by_name(self):
        if self._extensions_by_name_cache is None:
            d = {}
            for e in self.extensions:
                d[e.name] = e
            self._extensions_by_name_cache = d
        return self._extensions_by_name_cache

    ENTRY_POINT_CACHE = {}

    def list_entry_points(self):
        """Return the list of entry points for this namespace.

        The entry points are not actually loaded, their list is just read and
        returned.

        """
        if self.namespace not in self.ENTRY_POINT_CACHE:
            eps = list(_cache.get_group_all(self.namespace))
            self.ENTRY_POINT_CACHE[self.namespace] = eps
        return self.ENTRY_POINT_CACHE[self.namespace]

    def entry_points_names(self):
        """Return the list of entry points names for this namespace."""
        return list(map(operator.attrgetter("name"), self.list_entry_points()))

    def _load_plugins(self, invoke_on_load, invoke_args, invoke_kwds,
                      verify_requirements):
        extensions = []
        for ep in self.list_entry_points():
            LOG.debug('found extension %r', ep)
            try:
                ext = self._load_one_plugin(ep,
                                            invoke_on_load,
                                            invoke_args,
                                            invoke_kwds,
                                            verify_requirements,
                                            )
                if ext:
                    extensions.append(ext)
            except (KeyboardInterrupt, AssertionError):
                raise
            except Exception as err:
                if self._on_load_failure_callback is not None:
                    self._on_load_failure_callback(self, ep, err)
                else:
                    # Log the reason we couldn't import the module,
                    # usually without a traceback. The most common
                    # reason is an ImportError due to a missing
                    # dependency, and the error message should be
                    # enough to debug that.  If debug logging is
                    # enabled for our logger, provide the full
                    # traceback.
                    LOG.error('Could not load %r: %s', ep.name, err,
                              exc_info=LOG.isEnabledFor(logging.DEBUG))
        return extensions

    def _load_one_plugin(self, ep, invoke_on_load, invoke_args, invoke_kwds,
                         verify_requirements):
        # NOTE(dhellmann): Using require=False is deprecated in
        # setuptools 11.3.
        if hasattr(ep, 'resolve') and hasattr(ep, 'require'):
            if verify_requirements:
                ep.require()
            plugin = ep.resolve()
        else:
            plugin = ep.load()
        if invoke_on_load:
            obj = plugin(*invoke_args, **invoke_kwds)
        else:
            obj = None
        return Extension(ep.name, ep, plugin, obj)

    def names(self):
        "Returns the names of the discovered extensions"
        # We want to return the names of the extensions in the order
        # they would be used by map(), since some subclasses change
        # that order.
        return [e.name for e in self.extensions]

    def map(self, func, *args, **kwds):
        """Iterate over the extensions invoking func() for each.

        The signature for func() should be::

            def func(ext, *args, **kwds):
                pass

        The first argument to func(), 'ext', is the
        :class:`~stevedore.extension.Extension` instance.

        Exceptions raised from within func() are propagated up and
        processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        :param func: Callable to invoke for each extension.
        :param args: Variable arguments to pass to func()
        :param kwds: Keyword arguments to pass to func()
        :returns: List of values returned from func()
        """
        if not self.extensions:
            # FIXME: Use a more specific exception class here.
            raise NoMatches('No %s extensions found' % self.namespace)
        response = []
        for e in self.extensions:
            self._invoke_one_plugin(response.append, func, e, args, kwds)
        return response

    @staticmethod
    def _call_extension_method(extension, method_name, *args, **kwds):
        return getattr(extension.obj, method_name)(*args, **kwds)

    def map_method(self, method_name, *args, **kwds):
        """Iterate over the extensions invoking a method by name.

        This is equivalent of using :meth:`map` with func set to
        `lambda x: x.obj.method_name()`
        while being more convenient.

        Exceptions raised from within the called method are propagated up
        and processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        .. versionadded:: 0.12

        :param method_name: The extension method name
                            to call for each extension.
        :param args: Variable arguments to pass to method
        :param kwds: Keyword arguments to pass to method
        :returns: List of values returned from methods
        """
        return self.map(self._call_extension_method,
                        method_name, *args, **kwds)

    def _invoke_one_plugin(self, response_callback, func, e, args, kwds):
        try:
            response_callback(func(e, *args, **kwds))
        except Exception as err:
            if self.propagate_map_exceptions:
                raise
            else:
                LOG.error('error calling %r: %s', e.name, err)
                LOG.exception(err)

    def items(self):
        """Return an iterator of tuples of the form (name, extension).

        This is analogous to the Mapping.items() method.
        """
        return self._extensions_by_name.items()

    def __iter__(self):
        """Produce iterator for the manager.

        Iterating over an ExtensionManager produces the :class:`Extension`
        instances in the order they would be invoked.
        """
        return iter(self.extensions)

    def __getitem__(self, name):
        """Return the named extension.

        Accessing an ExtensionManager as a dictionary (``em['name']``)
        produces the :class:`Extension` instance with the
        specified name.
        """
        return self._extensions_by_name[name]

    def __contains__(self, name):
        """Return true if name is in list of enabled extensions."""
        return any(extension.name == name for extension in self.extensions)
