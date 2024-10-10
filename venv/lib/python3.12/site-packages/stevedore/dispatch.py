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

import logging

from .enabled import EnabledExtensionManager
from .exception import NoMatches

LOG = logging.getLogger(__name__)


class DispatchExtensionManager(EnabledExtensionManager):
    """Loads all plugins and filters on execution.

    This is useful for long-running processes that need to pass
    different inputs to different extensions.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param check_func: Function to determine which extensions to load.
    :type check_func: callable
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
    :type invoke_on_load: bool
    """

    def map(self, filter_func, func, *args, **kwds):
        """Iterate over the extensions invoking func() for any where
        filter_func() returns True.

        The signature of filter_func() should be::

            def filter_func(ext, *args, **kwds):
                pass

        The first argument to filter_func(), 'ext', is the
        :class:`~stevedore.extension.Extension`
        instance. filter_func() should return True if the extension
        should be invoked for the input arguments.

        The signature for func() should be::

            def func(ext, *args, **kwds):
                pass

        The first argument to func(), 'ext', is the
        :class:`~stevedore.extension.Extension` instance.

        Exceptions raised from within func() are propagated up and
        processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        :param filter_func: Callable to test each extension.
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
            if filter_func(e, *args, **kwds):
                self._invoke_one_plugin(response.append, func, e, args, kwds)
        return response

    def map_method(self, filter_func, method_name, *args, **kwds):
        """Iterate over the extensions invoking each one's object method called
        `method_name` for any where filter_func() returns True.

        This is equivalent of using :meth:`map` with func set to
        `lambda x: x.obj.method_name()`
        while being more convenient.

        Exceptions raised from within the called method are propagated up
        and processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        .. versionadded:: 0.12

        :param filter_func: Callable to test each extension.
        :param method_name: The extension method name to call
                            for each extension.
        :param args: Variable arguments to pass to method
        :param kwds: Keyword arguments to pass to method
        :returns: List of values returned from methods
        """
        return self.map(filter_func, self._call_extension_method,
                        method_name, *args, **kwds)


class NameDispatchExtensionManager(DispatchExtensionManager):
    """Loads all plugins and filters on execution.

    This is useful for long-running processes that need to pass
    different inputs to different extensions and can predict the name
    of the extensions before calling them.

    The check_func argument should return a boolean, with ``True``
    indicating that the extension should be loaded and made available
    and ``False`` indicating that the extension should be ignored.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param check_func: Function to determine which extensions to load.
    :type check_func: callable
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
    :type invoke_on_load: bool
    :param on_load_failure_callback: Callback function that will be called when
        an entrypoint can not be loaded. The arguments that will be provided
        when this is called (when an entrypoint fails to load) are
        (manager, entrypoint, exception)
    :type on_load_failure_callback: function
    :param verify_requirements: Use setuptools to enforce the
        dependencies of the plugin(s) being loaded. Defaults to False.
    :type verify_requirements: bool

    """

    def __init__(self, namespace, check_func, invoke_on_load=False,
                 invoke_args=(), invoke_kwds={},
                 propagate_map_exceptions=False,
                 on_load_failure_callback=None,
                 verify_requirements=False):
        super(NameDispatchExtensionManager, self).__init__(
            namespace=namespace,
            check_func=check_func,
            invoke_on_load=invoke_on_load,
            invoke_args=invoke_args,
            invoke_kwds=invoke_kwds,
            propagate_map_exceptions=propagate_map_exceptions,
            on_load_failure_callback=on_load_failure_callback,
            verify_requirements=verify_requirements,
        )

    def _init_plugins(self, extensions):
        super(NameDispatchExtensionManager, self)._init_plugins(extensions)
        self.by_name = dict((e.name, e) for e in self.extensions)

    def map(self, names, func, *args, **kwds):
        """Iterate over the extensions invoking func() for any where
        the name is in the given list of names.

        The signature for func() should be::

            def func(ext, *args, **kwds):
                pass

        The first argument to func(), 'ext', is the
        :class:`~stevedore.extension.Extension` instance.

        Exceptions raised from within func() are propagated up and
        processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        :param names: List or set of name(s) of extension(s) to invoke.
        :param func: Callable to invoke for each extension.
        :param args: Variable arguments to pass to func()
        :param kwds: Keyword arguments to pass to func()
        :returns: List of values returned from func()
        """
        response = []
        for name in names:
            try:
                e = self.by_name[name]
            except KeyError:
                LOG.debug('Missing extension %r being ignored', name)
            else:
                self._invoke_one_plugin(response.append, func, e, args, kwds)
        return response

    def map_method(self, names, method_name, *args, **kwds):
        """Iterate over the extensions invoking each one's object method called
        `method_name` for any where the name is in the given list of names.

        This is equivalent of using :meth:`map` with func set to
        `lambda x: x.obj.method_name()`
        while being more convenient.

        Exceptions raised from within the called method are propagated up
        and processing stopped if self.propagate_map_exceptions is True,
        otherwise they are logged and ignored.

        .. versionadded:: 0.12

        :param names: List or set of name(s) of extension(s) to invoke.
        :param method_name: The extension method name
                            to call for each extension.
        :param args: Variable arguments to pass to method
        :param kwds: Keyword arguments to pass to method
        :returns: List of values returned from methods
        """
        return self.map(names, self._call_extension_method,
                        method_name, *args, **kwds)
