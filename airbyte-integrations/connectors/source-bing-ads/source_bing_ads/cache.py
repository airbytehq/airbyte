#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import contextlib
import tempfile

import vcr


def _matcher(r1: vcr.request.Request, r2: vcr.request.Request) -> None:
    """
    Defines algorithm to compare two bing ads requests.
    Makes sure that uri, body and headers are equal in both requests
    """
    assert r1.uri == r2.uri and r1.body == r2.body and r1.headers == r2.headers


class VcrCache:
    """
    VcrPy wrapper to cache bing ads requests, and to be able to reuse results in other streams
    """

    def __init__(self) -> None:
        self._vcr = vcr.VCR()
        self._vcr.register_matcher("default", _matcher)
        # Register default matcher
        self._vcr.match_on = ["default"]

        self._cache_file = tempfile.NamedTemporaryFile()
        # Init inmemory cache file with empty data
        self._cache_file.write(b"interactions: []")
        self._cache_file.flush()
        self._cache_file.close()

    @contextlib.contextmanager
    def use_cassette(self) -> None:
        """
        Implements use_cassette method wrapper which uses in-memory temporary file for caching and yaml format for serialization
        """
        with self._vcr.use_cassette(self._cache_file.name, record_mode="new_episodes", serializer="yaml"):
            yield
