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

from base_python import AirbyteLogger
from source_marketo_singer import SourceMarketoSinger

logger = AirbyteLogger()
source = SourceMarketoSinger()
catalog = "/tmp/catalog.json"
config = "/tmp/config.json"
state = "/tmp/state.json"


def test_discover_cmd():
    assert f"tap-marketo --config {config} --discover" == source.discover_cmd(logger, config).strip()


def test_read_cmd_no_state():
    assert f"tap-marketo --config {config} --properties {catalog}" == source.read_cmd(logger, config, catalog).strip()


def test_read_cmd_with_state():
    assert (
        f"tap-marketo --config {config} --properties {catalog} --state {state}" == source.read_cmd(logger, config, catalog, state).strip()
    )
