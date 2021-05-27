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


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_harvest.streams import (
    BillableRates,
    Clients,
    Company,
    Contacts,
    CostRates,
    EstimateItemCategories,
    EstimateMessages,
    Estimates,
    ExpenseCategories,
    Expenses,
    ExpensesCategories,
    ExpensesClients,
    ExpensesProjects,
    ExpensesTeam,
    InvoiceItemCategories,
    InvoiceMessages,
    InvoicePayments,
    Invoices,
    ProjectAssignments,
    Projects,
    Roles,
    TaskAssignments,
    Tasks,
    TimeEntries,
    UserAssignments,
    Users,
)

from .auth import HarvestTokenAuthenticator


class SourceHarvest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = HarvestTokenAuthenticator(token=config["api_token"], account_id=config["account_id"])
            updated_since = pendulum.parse(config["updated_since"])
            users_gen = Users(authenticator=auth, updated_since=updated_since).read_records(sync_mode=SyncMode.full_refresh)
            next(users_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Harvest API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HarvestTokenAuthenticator(token=config["api_token"], account_id=config["account_id"])
        updated_since = pendulum.parse(config["updated_since"])

        streams = [
            Clients(authenticator=auth, updated_since=updated_since),
            Contacts(authenticator=auth, updated_since=updated_since),
            Company(authenticator=auth),
            Invoices(authenticator=auth, updated_since=updated_since),
            InvoiceMessages(authenticator=auth, updated_since=updated_since),
            InvoicePayments(authenticator=auth, updated_since=updated_since),
            InvoiceItemCategories(authenticator=auth, updated_since=updated_since),
            Estimates(authenticator=auth, updated_since=updated_since),
            EstimateMessages(authenticator=auth, updated_since=updated_since),
            EstimateItemCategories(authenticator=auth, updated_since=updated_since),
            Expenses(authenticator=auth, updated_since=updated_since),
            ExpenseCategories(authenticator=auth, updated_since=updated_since),
            Tasks(authenticator=auth, updated_since=updated_since),
            TimeEntries(authenticator=auth, updated_since=updated_since),
            UserAssignments(authenticator=auth, updated_since=updated_since),
            TaskAssignments(authenticator=auth, updated_since=updated_since),
            Projects(authenticator=auth, updated_since=updated_since),
            Roles(authenticator=auth, updated_since=updated_since),
            Users(authenticator=auth, updated_since=updated_since),
            BillableRates(authenticator=auth, updated_since=updated_since),
            CostRates(authenticator=auth, updated_since=updated_since),
            ProjectAssignments(authenticator=auth, updated_since=updated_since),
            ExpensesClients(authenticator=auth, updated_since=updated_since),
            ExpensesProjects(authenticator=auth, updated_since=updated_since),
            ExpensesCategories(authenticator=auth, updated_since=updated_since),
            ExpensesTeam(authenticator=auth, updated_since=updated_since),
        ]

        return streams
