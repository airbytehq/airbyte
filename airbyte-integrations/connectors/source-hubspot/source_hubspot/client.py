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

from typing import Mapping, Tuple

from base_python import BaseClient


class Client(BaseClient):
    _apis = {
        "campaigns": lambda x: x,
        "companies": lambda x: x,
        "contact_lists": lambda x: x,
        "contacts": lambda x: x,
        "contacts_by_company": lambda x: x,
        "deal_pipelines": lambda x: x,
        "deals": lambda x: x,
        "email_events": lambda x: x,
        "engagements": lambda x: x,
        "forms": lambda x: x,
        "line_items": lambda x: x,
        "owners": lambda x: x,
        "products": lambda x: x,
        "quotes": lambda x: x,
        "subscription_changes": lambda x: x,
        "tickets": lambda x: x,
        "workflows": lambda x: x,
    }

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        pass
