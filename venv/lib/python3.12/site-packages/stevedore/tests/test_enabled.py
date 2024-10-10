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

from stevedore import enabled
from stevedore.tests import utils


class TestEnabled(utils.TestCase):
    def test_enabled(self):
        def check_enabled(ep):
            return ep.name == 't2'
        em = enabled.EnabledExtensionManager(
            'stevedore.test.extension',
            check_enabled,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        self.assertEqual(len(em.extensions), 1)
        self.assertEqual(em.names(), ['t2'])

    def test_enabled_after_load(self):
        def check_enabled(ext):
            return ext.obj and ext.name == 't2'
        em = enabled.EnabledExtensionManager(
            'stevedore.test.extension',
            check_enabled,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        self.assertEqual(len(em.extensions), 1)
        self.assertEqual(em.names(), ['t2'])
