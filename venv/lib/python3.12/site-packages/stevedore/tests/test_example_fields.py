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

"""Tests for stevedore.example2.fields
"""

from stevedore.example2 import fields
from stevedore.tests import utils


class TestExampleFields(utils.TestCase):
    def test_simple_items(self):
        f = fields.FieldList(100)
        text = ''.join(f.format({'a': 'A', 'b': 'B'}))
        expected = '\n'.join([
            ': a : A',
            ': b : B',
            '',
        ])
        self.assertEqual(text, expected)

    def test_long_item(self):
        f = fields.FieldList(25)
        text = ''.join(f.format({'name':
                       'a value longer than the allowed width'}))
        expected = '\n'.join([
            ': name : a value longer',
            '    than the allowed',
            '    width',
            '',
        ])
        self.assertEqual(text, expected)
