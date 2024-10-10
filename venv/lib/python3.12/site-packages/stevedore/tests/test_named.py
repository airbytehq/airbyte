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

from unittest import mock

from stevedore import named
from stevedore.tests import utils


class TestNamed(utils.TestCase):
    def test_named(self):
        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            names=['t1'],
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        actual = em.names()
        self.assertEqual(actual, ['t1'])

    def test_enabled_before_load(self):
        # Set up the constructor for the FauxExtension to cause an
        # AssertionError so the test fails if the class is instantiated,
        # which should only happen if it is loaded before the name of the
        # extension is compared against the names that should be loaded by
        # the manager.
        init_name = 'stevedore.tests.test_extension.FauxExtension.__init__'
        with mock.patch(init_name) as m:
            m.side_effect = AssertionError
            em = named.NamedExtensionManager(
                'stevedore.test.extension',
                # Look for an extension that does not exist so the
                # __init__ we mocked should never be invoked.
                names=['no-such-extension'],
                invoke_on_load=True,
                invoke_args=('a',),
                invoke_kwds={'b': 'B'},
            )
            actual = em.names()
            self.assertEqual(actual, [])

    def test_extensions_listed_in_name_order(self):
        # Since we don't know the "natural" order of the extensions, run
        # the test both ways: if the sorting is broken, one of them will
        # fail
        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            names=['t1', 't2'],
            name_order=True
        )
        actual = em.names()
        self.assertEqual(actual, ['t1', 't2'])

        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            names=['t2', 't1'],
            name_order=True
        )
        actual = em.names()
        self.assertEqual(actual, ['t2', 't1'])

    def test_load_fail_ignored_when_sorted(self):
        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            names=['e1', 't2', 'e2', 't1'],
            name_order=True,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        actual = em.names()
        self.assertEqual(['t2', 't1'], actual)

        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            names=['e1', 't1'],
            name_order=False,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        actual = em.names()
        self.assertEqual(['t1'], actual)
