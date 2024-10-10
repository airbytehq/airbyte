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

"""Tests for stevedore._cache
"""
import sys

from unittest import mock

from stevedore import _cache
from stevedore.tests import utils


class TestCache(utils.TestCase):

    def test_disable_caching_executable(self):
        """Test caching is disabled if python interpreter is located under /tmp
        directory (Ansible)
        """
        with mock.patch.object(sys, 'executable', '/tmp/fake'):
            sot = _cache.Cache()
            self.assertTrue(sot._disable_caching)

    def test_disable_caching_file(self):
        """Test caching is disabled if .disable file is present in target
        dir
        """
        cache_dir = _cache._get_cache_dir()

        with mock.patch('os.path.isfile') as mock_path:
            mock_path.return_value = True
            sot = _cache.Cache()
            mock_path.assert_called_with('%s/.disable' % cache_dir)
            self.assertTrue(sot._disable_caching)

            mock_path.return_value = False
            sot = _cache.Cache()
            self.assertFalse(sot._disable_caching)

    @mock.patch('os.makedirs')
    @mock.patch('builtins.open')
    def test__get_data_for_path_no_write(self, mock_open, mock_mkdir):
        sot = _cache.Cache()
        sot._disable_caching = True
        mock_open.side_effect = IOError
        sot._get_data_for_path('fake')
        mock_mkdir.assert_not_called()

    def test__build_cacheable_data(self):
        # this is a rubbish test as we don't actually do anything with the
        # data, but it's too hard to script since it's totally environmentally
        # dependent and mocking out the underlying calls would remove the value
        # of this test (we want to test those underlying API calls)
        ret = _cache._build_cacheable_data()
        self.assertIsInstance(ret['groups'], dict)
