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

from unittest.mock import Mock
from unittest.mock import sentinel

from stevedore.dispatch import DispatchExtensionManager
from stevedore.dispatch import NameDispatchExtensionManager
from stevedore.extension import Extension
from stevedore.tests import utils

from stevedore import DriverManager
from stevedore import EnabledExtensionManager
from stevedore import ExtensionManager
from stevedore import HookManager
from stevedore import NamedExtensionManager


test_extension = Extension('test_extension', None, None, None)
test_extension2 = Extension('another_one', None, None, None)

mock_entry_point = Mock(module_name='test.extension', attrs=['obj'])
a_driver = Extension('test_driver', mock_entry_point, sentinel.driver_plugin,
                     sentinel.driver_obj)


# base ExtensionManager
class TestTestManager(utils.TestCase):
    def test_instance_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = ExtensionManager.make_test_instance(extensions)
        self.assertEqual(extensions, em.extensions)

    def test_instance_should_have_default_namespace(self):
        em = ExtensionManager.make_test_instance([])
        self.assertEqual(em.namespace, 'TESTING')

    def test_instance_should_use_supplied_namespace(self):
        namespace = 'testing.1.2.3'
        em = ExtensionManager.make_test_instance([], namespace=namespace)
        self.assertEqual(namespace, em.namespace)

    def test_extension_name_should_be_listed(self):
        em = ExtensionManager.make_test_instance([test_extension])
        self.assertIn(test_extension.name, em.names())

    def test_iterator_should_yield_extension(self):
        em = ExtensionManager.make_test_instance([test_extension])
        self.assertEqual(test_extension, next(iter(em)))

    def test_manager_should_allow_name_access(self):
        em = ExtensionManager.make_test_instance([test_extension])
        self.assertEqual(test_extension, em[test_extension.name])

    def test_manager_should_call(self):
        em = ExtensionManager.make_test_instance([test_extension])
        func = Mock()
        em.map(func)
        func.assert_called_once_with(test_extension)

    def test_manager_should_call_all(self):
        em = ExtensionManager.make_test_instance([test_extension2,
                                                  test_extension])
        func = Mock()
        em.map(func)
        func.assert_any_call(test_extension2)
        func.assert_any_call(test_extension)

    def test_manager_return_values(self):
        def mapped(ext, *args, **kwds):
            return ext.name

        em = ExtensionManager.make_test_instance([test_extension2,
                                                  test_extension])
        results = em.map(mapped)
        self.assertEqual(sorted(results), ['another_one', 'test_extension'])

    def test_manager_should_eat_exceptions(self):
        em = ExtensionManager.make_test_instance([test_extension])

        func = Mock(side_effect=RuntimeError('hard coded error'))

        results = em.map(func, 1, 2, a='A', b='B')
        self.assertEqual(results, [])

    def test_manager_should_propagate_exceptions(self):
        em = ExtensionManager.make_test_instance([test_extension],
                                                 propagate_map_exceptions=True)
        self.skipTest('Skipping temporarily')
        func = Mock(side_effect=RuntimeError('hard coded error'))
        em.map(func, 1, 2, a='A', b='B')

    # NamedExtensionManager
    def test_named_manager_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = NamedExtensionManager.make_test_instance(extensions)
        self.assertEqual(extensions, em.extensions)

    def test_named_manager_should_have_default_namespace(self):
        em = NamedExtensionManager.make_test_instance([])
        self.assertEqual(em.namespace, 'TESTING')

    def test_named_manager_should_use_supplied_namespace(self):
        namespace = 'testing.1.2.3'
        em = NamedExtensionManager.make_test_instance([], namespace=namespace)
        self.assertEqual(namespace, em.namespace)

    def test_named_manager_should_populate_names(self):
        extensions = [test_extension, test_extension2]
        em = NamedExtensionManager.make_test_instance(extensions)
        self.assertEqual(em.names(), ['test_extension', 'another_one'])

    # HookManager
    def test_hook_manager_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = HookManager.make_test_instance(extensions)
        self.assertEqual(extensions, em.extensions)

    def test_hook_manager_should_be_first_extension_name(self):
        extensions = [test_extension, test_extension2]
        em = HookManager.make_test_instance(extensions)
        # This will raise KeyError if the names don't match
        assert (em[test_extension.name])

    def test_hook_manager_should_have_default_namespace(self):
        em = HookManager.make_test_instance([test_extension])
        self.assertEqual(em.namespace, 'TESTING')

    def test_hook_manager_should_use_supplied_namespace(self):
        namespace = 'testing.1.2.3'
        em = HookManager.make_test_instance([test_extension],
                                            namespace=namespace)
        self.assertEqual(namespace, em.namespace)

    def test_hook_manager_should_return_named_extensions(self):
        hook1 = Extension('captain', None, None, None)
        hook2 = Extension('captain', None, None, None)
        em = HookManager.make_test_instance([hook1, hook2])
        self.assertEqual([hook1, hook2], em['captain'])

    # DriverManager
    def test_driver_manager_should_use_supplied_extension(self):
        em = DriverManager.make_test_instance(a_driver)
        self.assertEqual([a_driver], em.extensions)

    def test_driver_manager_should_have_default_namespace(self):
        em = DriverManager.make_test_instance(a_driver)
        self.assertEqual(em.namespace, 'TESTING')

    def test_driver_manager_should_use_supplied_namespace(self):
        namespace = 'testing.1.2.3'
        em = DriverManager.make_test_instance(a_driver, namespace=namespace)
        self.assertEqual(namespace, em.namespace)

    def test_instance_should_use_driver_name(self):
        em = DriverManager.make_test_instance(a_driver)
        self.assertEqual(['test_driver'], em.names())

    def test_instance_call(self):
        def invoke(ext, *args, **kwds):
            return ext.name, args, kwds

        em = DriverManager.make_test_instance(a_driver)
        result = em(invoke, 'a', b='C')
        self.assertEqual(result, ('test_driver', ('a',), {'b': 'C'}))

    def test_instance_driver_property(self):
        em = DriverManager.make_test_instance(a_driver)
        self.assertEqual(sentinel.driver_obj, em.driver)

    # EnabledExtensionManager
    def test_enabled_instance_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = EnabledExtensionManager.make_test_instance(extensions)
        self.assertEqual(extensions, em.extensions)

    # DispatchExtensionManager
    def test_dispatch_instance_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = DispatchExtensionManager.make_test_instance(extensions)
        self.assertEqual(extensions, em.extensions)

    def test_dispatch_map_should_invoke_filter_for_extensions(self):
        em = DispatchExtensionManager.make_test_instance([test_extension,
                                                          test_extension2])
        filter_func = Mock(return_value=False)
        args = ('A',)
        kw = {'big': 'Cheese'}
        em.map(filter_func, None, *args, **kw)
        filter_func.assert_any_call(test_extension, *args, **kw)
        filter_func.assert_any_call(test_extension2, *args, **kw)

    # NameDispatchExtensionManager
    def test_name_dispatch_instance_should_use_supplied_extensions(self):
        extensions = [test_extension, test_extension2]
        em = NameDispatchExtensionManager.make_test_instance(extensions)

        self.assertEqual(extensions, em.extensions)

    def test_name_dispatch_instance_should_build_extension_name_map(self):
        extensions = [test_extension, test_extension2]
        em = NameDispatchExtensionManager.make_test_instance(extensions)
        self.assertEqual(test_extension, em.by_name[test_extension.name])
        self.assertEqual(test_extension2, em.by_name[test_extension2.name])

    def test_named_dispatch_map_should_invoke_filter_for_extensions(self):
        em = NameDispatchExtensionManager.make_test_instance([test_extension,
                                                              test_extension2])
        func = Mock()
        args = ('A',)
        kw = {'BIGGER': 'Cheese'}
        em.map(['test_extension'], func, *args, **kw)
        func.assert_called_once_with(test_extension, *args, **kw)
