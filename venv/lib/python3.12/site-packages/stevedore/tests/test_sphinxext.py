#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Tests for the sphinx extension
"""

import importlib.metadata as importlib_metadata

from stevedore import extension
from stevedore import sphinxext
from stevedore.tests import utils


def _make_ext(name, docstring):
    def inner():
        pass

    inner.__doc__ = docstring
    m1 = importlib_metadata.EntryPoint(
        name, '{}_module:{}'.format(name, name), 'group',
    )
    return extension.Extension(name, m1, inner, None)


class TestSphinxExt(utils.TestCase):

    def setUp(self):
        super(TestSphinxExt, self).setUp()
        self.exts = [
            _make_ext('test1', 'One-line docstring'),
            _make_ext('test2', 'Multi-line docstring\n\nAnother para'),
        ]
        self.em = extension.ExtensionManager.make_test_instance(self.exts)

    def test_simple_list(self):
        results = list(sphinxext._simple_list(self.em))
        self.assertEqual(
            [
                ('* test1 -- One-line docstring', 'test1_module'),
                ('* test2 -- Multi-line docstring', 'test2_module'),
            ],
            results,
        )

    def test_simple_list_no_docstring(self):
        ext = [_make_ext('nodoc', None)]
        em = extension.ExtensionManager.make_test_instance(ext)
        results = list(sphinxext._simple_list(em))
        self.assertEqual(
            [
                ('* nodoc -- ', 'nodoc_module'),
            ],
            results,
        )

    def test_detailed_list(self):
        results = list(sphinxext._detailed_list(self.em))
        self.assertEqual(
            [
                ('test1', 'test1_module'),
                ('-----', 'test1_module'),
                ('\n', 'test1_module'),
                ('One-line docstring', 'test1_module'),
                ('\n', 'test1_module'),
                ('test2', 'test2_module'),
                ('-----', 'test2_module'),
                ('\n', 'test2_module'),
                ('Multi-line docstring\n\nAnother para', 'test2_module'),
                ('\n', 'test2_module'),
            ],
            results,
        )

    def test_detailed_list_format(self):
        results = list(sphinxext._detailed_list(self.em, over='+', under='+'))
        self.assertEqual(
            [
                ('+++++', 'test1_module'),
                ('test1', 'test1_module'),
                ('+++++', 'test1_module'),
                ('\n', 'test1_module'),
                ('One-line docstring', 'test1_module'),
                ('\n', 'test1_module'),
                ('+++++', 'test2_module'),
                ('test2', 'test2_module'),
                ('+++++', 'test2_module'),
                ('\n', 'test2_module'),
                ('Multi-line docstring\n\nAnother para', 'test2_module'),
                ('\n', 'test2_module'),
            ],
            results,
        )

    def test_detailed_list_no_docstring(self):
        ext = [_make_ext('nodoc', None)]
        em = extension.ExtensionManager.make_test_instance(ext)
        results = list(sphinxext._detailed_list(em))
        self.assertEqual(
            [
                ('nodoc', 'nodoc_module'),
                ('-----', 'nodoc_module'),
                ('\n', 'nodoc_module'),
                (('.. warning:: No documentation found for '
                 'nodoc in nodoc_module:nodoc'),
                 'nodoc_module'),
                ('\n', 'nodoc_module'),
            ],
            results,
        )
