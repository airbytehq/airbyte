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

import time

from source_freshdesk.utils import CallCredit


def test_consume_one():
    """Multiple consumptions of 1 cred will reach limit"""
    credit = CallCredit(balance=3, reload_period=1)
    ts_1 = time.time()
    for i in range(4):
        credit.consume(1)
    ts_2 = time.time()

    assert 1 <= ts_2 - ts_1 < 2


def test_consume_many():
    """Consumptions of N creds will reach limit and decrease balance"""
    credit = CallCredit(balance=3, reload_period=1)
    ts_1 = time.time()
    credit.consume(1)
    credit.consume(3)
    ts_2 = time.time()
    # the balance decreased already, so single cred will be enough to reach limit
    credit.consume(1)
    ts_3 = time.time()

    assert 1 <= ts_2 - ts_1 < 2
    assert 1 <= ts_3 - ts_2 < 2
