"""
MIT License
Copyright (c) 2020 Airbyte
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from functools import partial

from base_python import BaseClient

from freshdesk.api import API


def paginator(request, params, page=None, per_page=100, **kwargs):
    """ Split requests in multiple batches and return records as generator
    """
    read_all = page is None
    page = page or 1
    while True:
        rows = request(params={**params, 'page': page, 'per_page': per_page})
        yield from rows

        if len(rows) < per_page or not read_all:
            break
        page += 1
    request(params=params)


class Client(BaseClient):
    ENTITIES = [
        'agents',
        'contacts',
        'companies',
        'groups',
        'roles',
        'skills',
        'surveys',
        'tickets',
        'time_entries'
    ]

    def __init__(self, domain='newaccount1603334233301.freshdesk.com',
                 api_key='LulyQWftBkRtJzuPjdt', version=None):
        self._client = API(domain, api_key, version)
        super().__init__()

    def list(self, name, **kwargs):
        # for now exact matching
        url = name
        request = partial(self._client._api._get, url=url)
        yield from paginator(request, params={}, **kwargs)

    def _enumerate_methods(self):
        return {
            entity: partial(self.list, name=entity)
            for entity in self.ENTITIES
        }

