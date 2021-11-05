#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum
from source_freshdesk.api import TicketsAPI


class Test300PageLimit:

    tickets_input = [
        {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
        {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
        {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
        {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
        {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
        {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
    ]

    expected_output = [
        {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
        {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
        {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},  # duplicate
        {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
        {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},  # duplicate
        {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
        {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},  # duplicate
        {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
        {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},  # duplicate
        {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
        {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},  # duplicate
    ]

    # Mocking the getter: Callable to produce the server output
    def _getter(self, params, **args):

        tickets_stream = self.tickets_input
        updated_since = params.get("updated_since", None)

        if updated_since:
            tickets_stream = filter(lambda ticket: pendulum.parse(ticket["updated_at"]) >= updated_since, self.tickets_input)

        start_from = (params["page"] - 1) * params["per_page"]
        output = list(tickets_stream)[start_from : start_from + params["per_page"]]

        return output

    def test_not_all_records(self):
        """
        TEST 1 - not all records are retrieved

        During test1 the tickets_stream changes the state of parameters on page: 2,
        by updating the params:
        `params["order_by"] = "updated_at"`
        `params["updated_since"] = last_record`
        continues to fetch records from the source, using new cycle, and so on.

        NOTE:
        After switch of the state on ticket_paginate_limit = 2, is this example, we will experience the
        records duplication, because of the last_record state, starting at the point
        where we stoped causes the duplication of the output. The solution for this is to add at least 1 second to the
        last_record state. The DBT normalization should handle this for the end user, so the duplication issue is not a
        blocker in such cases.
        Main pricipal here is: airbyte is at-least-once delivery, but skipping records is data loss.
        """

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
        assert self.expected_output == test1
