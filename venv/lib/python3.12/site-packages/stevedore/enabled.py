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

from .extension import ExtensionManager


LOG = logging.getLogger(__name__)


class EnabledExtensionManager(ExtensionManager):
    """Loads only plugins that pass a check function.

    The check_func argument should return a boolean, with ``True``
    indicating that the extension should be loaded and made available
    and ``False`` indicating that the extension should be ignored.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param check_func: Function to determine which extensions to load.
    :type check_func: callable, taking an :class:`Extension`
        instance as argument
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

    def __init__(self, namespace, check_func, invoke_on_load=False,
                 invoke_args=(), invoke_kwds={},
                 propagate_map_exceptions=False,
                 on_load_failure_callback=None,
                 verify_requirements=False,):
        self.check_func = check_func
        super(EnabledExtensionManager, self).__init__(
            namespace,
            invoke_on_load=invoke_on_load,
            invoke_args=invoke_args,
            invoke_kwds=invoke_kwds,
            propagate_map_exceptions=propagate_map_exceptions,
            on_load_failure_callback=on_load_failure_callback,
            verify_requirements=verify_requirements,
        )

    def _load_one_plugin(self, ep, invoke_on_load, invoke_args, invoke_kwds,
                         verify_requirements):
        ext = super(EnabledExtensionManager, self)._load_one_plugin(
            ep, invoke_on_load, invoke_args, invoke_kwds,
            verify_requirements,
        )
        if ext and not self.check_func(ext):
            LOG.debug('ignoring extension %r', ep.name)
            return None
        return ext
