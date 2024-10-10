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

from .exception import MultipleMatches
from .exception import NoMatches
from .named import NamedExtensionManager


class DriverManager(NamedExtensionManager):
    """Load a single plugin with a given name from the namespace.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param name: The name of the driver to load.
    :type name: str
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
    :param on_load_failure_callback: Callback function that will be called when
        an entrypoint can not be loaded. The arguments that will be provided
        when this is called (when an entrypoint fails to load) are
        (manager, entrypoint, exception)
    :type on_load_failure_callback: function
    :param verify_requirements: Use setuptools to enforce the
        dependencies of the plugin(s) being loaded. Defaults to False.
    :type verify_requirements: bool
    :type warn_on_missing_entrypoint: bool
    """

    def __init__(self, namespace, name,
                 invoke_on_load=False, invoke_args=(), invoke_kwds={},
                 on_load_failure_callback=None,
                 verify_requirements=False,
                 warn_on_missing_entrypoint=True):
        on_load_failure_callback = on_load_failure_callback \
            or self._default_on_load_failure
        super(DriverManager, self).__init__(
            namespace=namespace,
            names=[name],
            invoke_on_load=invoke_on_load,
            invoke_args=invoke_args,
            invoke_kwds=invoke_kwds,
            on_load_failure_callback=on_load_failure_callback,
            verify_requirements=verify_requirements,
            warn_on_missing_entrypoint=warn_on_missing_entrypoint
        )

    @staticmethod
    def _default_on_load_failure(drivermanager, ep, err):
        raise

    @classmethod
    def make_test_instance(cls, extension, namespace='TESTING',
                           propagate_map_exceptions=False,
                           on_load_failure_callback=None,
                           verify_requirements=False):
        """Construct a test DriverManager

        Test instances are passed a list of extensions to work from rather
        than loading them from entry points.

        :param extension: Pre-configured Extension instance
        :type extension: :class:`~stevedore.extension.Extension`
        :param namespace: The namespace for the manager; used only for
            identification since the extensions are passed in.
        :type namespace: str
        :param propagate_map_exceptions: Boolean controlling whether exceptions
            are propagated up through the map call or whether they are logged
            and then ignored
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

        o = super(DriverManager, cls).make_test_instance(
            [extension], namespace=namespace,
            propagate_map_exceptions=propagate_map_exceptions,
            on_load_failure_callback=on_load_failure_callback,
            verify_requirements=verify_requirements)
        return o

    def _init_plugins(self, extensions):
        super(DriverManager, self)._init_plugins(extensions)

        if not self.extensions:
            name = self._names[0]
            raise NoMatches('No %r driver found, looking for %r' %
                            (self.namespace, name))
        if len(self.extensions) > 1:
            discovered_drivers = ','.join(e.entry_point_target
                                          for e in self.extensions)

            raise MultipleMatches('Multiple %r drivers found: %s' %
                                  (self.namespace, discovered_drivers))

    def __call__(self, func, *args, **kwds):
        """Invokes func() for the single loaded extension.

        The signature for func() should be::

            def func(ext, *args, **kwds):
                pass

        The first argument to func(), 'ext', is the
        :class:`~stevedore.extension.Extension` instance.

        Exceptions raised from within func() are logged and ignored.

        :param func: Callable to invoke for each extension.
        :param args: Variable arguments to pass to func()
        :param kwds: Keyword arguments to pass to func()
        :returns: List of values returned from func()
        """
        results = self.map(func, *args, **kwds)
        if results:
            return results[0]

    @property
    def driver(self):
        """Returns the driver being used by this manager."""
        ext = self.extensions[0]
        return ext.obj if ext.obj else ext.plugin
