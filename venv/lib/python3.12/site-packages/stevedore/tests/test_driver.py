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

"""Tests for stevedore.extension
"""

import importlib.metadata as importlib_metadata

from stevedore import driver
from stevedore import exception
from stevedore import extension
from stevedore.tests import test_extension
from stevedore.tests import utils


class TestCallback(utils.TestCase):
    def test_detect_plugins(self):
        em = driver.DriverManager('stevedore.test.extension', 't1')
        names = sorted(em.names())
        self.assertEqual(names, ['t1'])

    def test_call(self):
        def invoke(ext, *args, **kwds):
            return (ext.name, args, kwds)
        em = driver.DriverManager('stevedore.test.extension', 't1')
        result = em(invoke, 'a', b='C')
        self.assertEqual(result, ('t1', ('a',), {'b': 'C'}))

    def test_driver_property_not_invoked_on_load(self):
        em = driver.DriverManager('stevedore.test.extension', 't1',
                                  invoke_on_load=False)
        d = em.driver
        self.assertIs(d, test_extension.FauxExtension)

    def test_driver_property_invoked_on_load(self):
        em = driver.DriverManager('stevedore.test.extension', 't1',
                                  invoke_on_load=True)
        d = em.driver
        self.assertIsInstance(d, test_extension.FauxExtension)

    def test_no_drivers(self):
        try:
            driver.DriverManager('stevedore.test.extension.none', 't1')
        except exception.NoMatches as err:
            self.assertIn("No 'stevedore.test.extension.none' driver found",
                          str(err))

    def test_bad_driver(self):
        try:
            driver.DriverManager('stevedore.test.extension', 'e2')
        except ImportError:
            pass
        else:
            self.assertEqual(False, "No error raised")

    def test_multiple_drivers(self):
        # The idea for this test was contributed by clayg:
        # https://gist.github.com/clayg/6311348
        extensions = [
            extension.Extension(
                'backend',
                importlib_metadata.EntryPoint(
                    'backend', 'pkg1:driver', 'backend'),
                'pkg backend',
                None,
            ),
            extension.Extension(
                'backend',
                importlib_metadata.EntryPoint(
                    'backend', 'pkg2:driver', 'backend'),
                'pkg backend',
                None,
            ),
        ]
        try:
            dm = driver.DriverManager.make_test_instance(extensions[0])
            # Call the initialization code that verifies the extension
            dm._init_plugins(extensions)
        except exception.MultipleMatches as err:
            self.assertIn("Multiple", str(err))
        else:
            self.fail('Should have had an error')
