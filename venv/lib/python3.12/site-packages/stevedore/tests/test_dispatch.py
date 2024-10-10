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

from stevedore import dispatch
from stevedore.tests import utils


def check_dispatch(ep, *args, **kwds):
    return ep.name == 't2'


class TestDispatch(utils.TestCase):
    def check_dispatch(ep, *args, **kwds):
        return ep.name == 't2'

    def test_dispatch(self):

        def invoke(ep, *args, **kwds):
            return (ep.name, args, kwds)

        em = dispatch.DispatchExtensionManager('stevedore.test.extension',
                                               lambda *args, **kwds: True,
                                               invoke_on_load=True,
                                               invoke_args=('a',),
                                               invoke_kwds={'b': 'B'},
                                               )
        self.assertEqual(len(em.extensions), 2)
        self.assertEqual(set(em.names()), set(['t1', 't2']))

        results = em.map(check_dispatch,
                         invoke,
                         'first',
                         named='named value',
                         )
        expected = [('t2', ('first',), {'named': 'named value'})]
        self.assertEqual(results, expected)

    def test_dispatch_map_method(self):
        em = dispatch.DispatchExtensionManager('stevedore.test.extension',
                                               lambda *args, **kwds: True,
                                               invoke_on_load=True,
                                               invoke_args=('a',),
                                               invoke_kwds={'b': 'B'},
                                               )

        results = em.map_method(check_dispatch, 'get_args_and_data', 'first')
        self.assertEqual(results, [(('a',), {'b': 'B'}, 'first')])

    def test_name_dispatch(self):

        def invoke(ep, *args, **kwds):
            return (ep.name, args, kwds)

        em = dispatch.NameDispatchExtensionManager('stevedore.test.extension',
                                                   lambda *args, **kwds: True,
                                                   invoke_on_load=True,
                                                   invoke_args=('a',),
                                                   invoke_kwds={'b': 'B'},
                                                   )
        self.assertEqual(len(em.extensions), 2)
        self.assertEqual(set(em.names()), set(['t1', 't2']))

        results = em.map(['t2'], invoke, 'first', named='named value',)
        expected = [('t2', ('first',), {'named': 'named value'})]
        self.assertEqual(results, expected)

    def test_name_dispatch_ignore_missing(self):

        def invoke(ep, *args, **kwds):
            return (ep.name, args, kwds)

        em = dispatch.NameDispatchExtensionManager(
            'stevedore.test.extension',
            lambda *args, **kwds: True,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )

        results = em.map(['t3', 't1'], invoke, 'first', named='named value',)
        expected = [('t1', ('first',), {'named': 'named value'})]
        self.assertEqual(results, expected)

    def test_name_dispatch_map_method(self):
        em = dispatch.NameDispatchExtensionManager(
            'stevedore.test.extension',
            lambda *args, **kwds: True,
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )

        results = em.map_method(['t3', 't1'], 'get_args_and_data', 'first')
        self.assertEqual(results, [(('a',), {'b': 'B'}, 'first')])
