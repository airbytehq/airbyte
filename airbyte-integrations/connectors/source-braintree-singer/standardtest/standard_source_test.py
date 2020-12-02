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

import json
import pkgutil

from airbyte_protocol import AirbyteCatalog, ConnectorSpecification
from base_python_test import StandardSourceTestIface


class BraintreeStandardSourceTest(StandardSourceTestIface):
    def get_spec(self) -> ConnectorSpecification:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    def get_config(self) -> object:
        return json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], "config.json"))

    def get_catalog(self) -> AirbyteCatalog:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], "catalog.json")
        return AirbyteCatalog.parse_obj(json.loads(raw_spec))

    def setup(self) -> None:
        pass

    def teardown(self) -> None:
        pass
