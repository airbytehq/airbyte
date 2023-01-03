#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
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
    ProjectBudget,
    Projects,
    Roles,
    TaskAssignments,
    Tasks,
    TimeClients,
    TimeEntries,
    TimeProjects,
    TimeTasks,
    TimeTeam,
    Uninvoiced,
    UserAssignments,
    Users,
)

from .auth import HarvestOauth2Authenticator, HarvestTokenAuthenticator


class SourceHarvest(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        credentials = config.get("credentials", {})
        if credentials and "client_id" in credentials:
            return HarvestOauth2Authenticator(
                token_refresh_endpoint="https://id.getharvest.com/api/v2/oauth2/token",
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret"),
                refresh_token=credentials.get("refresh_token"),
                account_id=config["account_id"],
            )

        api_token = credentials.get("api_token", config.get("api_token"))
        if not api_token:
            raise Exception("Config validation error: 'api_token' is a required property")
        return HarvestTokenAuthenticator(token=api_token, account_id=config["account_id"])

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            auth = self.get_authenticator(config)
            replication_start_date = pendulum.parse(config["replication_start_date"])
            users_gen = Users(authenticator=auth, replication_start_date=replication_start_date).read_records(
                sync_mode=SyncMode.full_refresh
            )
            next(users_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Harvest API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = self.get_authenticator(config)
        replication_start_date = pendulum.parse(config["replication_start_date"])
        from_date = replication_start_date.date()
        replication_end_date = config.get("replication_end_date")
        replication_end_date = replication_end_date and pendulum.parse(replication_end_date)
        to_date = replication_end_date and replication_end_date.date()
        date_range = {"from_date": from_date, "to_date": to_date}

        streams = [
            Clients(authenticator=auth, replication_start_date=replication_start_date),
            Contacts(authenticator=auth, replication_start_date=replication_start_date),
            Company(authenticator=auth),
            Invoices(authenticator=auth, replication_start_date=replication_start_date),
            InvoiceMessages(authenticator=auth, replication_start_date=replication_start_date),
            InvoicePayments(authenticator=auth, replication_start_date=replication_start_date),
            InvoiceItemCategories(authenticator=auth, replication_start_date=replication_start_date),
            Estimates(authenticator=auth, replication_start_date=replication_start_date),
            EstimateMessages(authenticator=auth, replication_start_date=replication_start_date),
            EstimateItemCategories(authenticator=auth, replication_start_date=replication_start_date),
            Expenses(authenticator=auth, replication_start_date=replication_start_date),
            ExpenseCategories(authenticator=auth, replication_start_date=replication_start_date),
            Tasks(authenticator=auth, replication_start_date=replication_start_date),
            TimeEntries(authenticator=auth, replication_start_date=replication_start_date),
            UserAssignments(authenticator=auth, replication_start_date=replication_start_date),
            TaskAssignments(authenticator=auth, replication_start_date=replication_start_date),
            Projects(authenticator=auth, replication_start_date=replication_start_date),
            Roles(authenticator=auth, replication_start_date=replication_start_date),
            Users(authenticator=auth, replication_start_date=replication_start_date),
            BillableRates(authenticator=auth),
            CostRates(authenticator=auth),
            ProjectAssignments(authenticator=auth, replication_start_date=replication_start_date),
            ExpensesClients(authenticator=auth, **date_range),
            ExpensesProjects(authenticator=auth, **date_range),
            ExpensesCategories(authenticator=auth, **date_range),
            ExpensesTeam(authenticator=auth, **date_range),
            Uninvoiced(authenticator=auth, **date_range),
            TimeClients(authenticator=auth, **date_range),
            TimeProjects(authenticator=auth, **date_range),
            TimeTasks(authenticator=auth, **date_range),
            TimeTeam(authenticator=auth, **date_range),
            ProjectBudget(authenticator=auth, **date_range),
        ]

        return streams
