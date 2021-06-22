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

import pendulum
from source_freshdesk.api import TicketsAPI


class Test300PageLimit:

    tickets = [
        {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
        {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
        {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
        {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
        {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
        {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
        {"id": 7, "updated_at": "2019-03-03T00:00:00Z"},
    ]

    # Mocking the getter: Callable to produce the server output
    def _getter(self, params, **args):

        tickets_stream = self.tickets
        updated_since = params.get("updated_since")

        if updated_since:
            tickets_stream = filter(lambda ticket: pendulum.parse(ticket["updated_at"]) >= updated_since, self.tickets)

        start_from = (params["page"] - 1) * params["per_page"]
        output = list(tickets_stream)[start_from : start_from + params["per_page"]]

        return output

    """
    TEST 1 - not all records are retrieved

    During test1 the tickets_stream changes the state of parameters on page: 2,
    by updating the params:
    params["order_by"] = "updated_at"
    params["updated_since"] = last_record
    and continues to fetch records from the source, using new cycle, and so on.
    NOTE:
    The record {"id": 7} is not shown in the output result, because of the same "updated_at" with {"id": 6}
    """

    def test_not_all_records(self):
        # INT value of page number where the switch state should be triggered.
        # in this test case values from: 1 - 4, assuming we want to switch state on this page.
        ticket_paginate_limit = 2
        # This parameter mocks the "per_page" parameter in the API Call
        result_return_limit = 1
        # Calling the TicketsAPI.get_tickets method directly from the module
        test1 = list(
            TicketsAPI.get_tickets(
                result_return_limit=result_return_limit, getter=self._getter, ticket_paginate_limit=ticket_paginate_limit
            )
        )
        # We're expecting 6 records to return from the tickets_stream
        assert self.tickets[:-1] == test1

    """
    TEST 2 - fetched all the records
    During test1 the tickets_stream changes the state of parameters on page: 2,
    by updating the params:
    params["order_by"] = "updated_at"
    params["updated_since"] = last_record
    and continues to fetch records from the source, using new cycle, and so on.
    NOTE:
    The test returns all the record in way way it sohuld be, the difference is in the last {"id": 7},
    that has +1 second
    """

    def test_all_records(self):

        self.tickets = [
            {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
            {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
            {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
            {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
            {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
            {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
            {"id": 7, "updated_at": "2019-03-03T00:00:01Z"},  # this record has timedelta of 1 second
        ]

        # INT value of page number where the switch state should be triggered.
        # in this test case values from: 1 - 4, assuming we want to switch state on this page.
        ticket_paginate_limit = 2
        # This parameter mocks the "per_page" parameter in the API Call
        result_return_limit = 1
        # Calling the TicketsAPI.get_tickets method directly from the module
        test2 = list(
            TicketsAPI.get_tickets(
                result_return_limit=result_return_limit, getter=self._getter, ticket_paginate_limit=ticket_paginate_limit
            )
        )
        # We're expecting 7 records to return from the tickets_stream
        assert self.tickets == test2
