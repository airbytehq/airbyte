#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from netsuitesdk import NetSuiteConnection
from netsuitesdk.internal.exceptions import NetSuiteLoginError, NetSuiteRequestError

from source_netsuite.streams import (
    Accounts,
    BillingAccounts,
    Classifications,
    Currencies,
    Customers,
    Departments,
    Employees,
    ExpenseCategories,
    ExpenseReports,
    Files,
    Folders,
    JournalEntries,
    Locations,
    Projects,
    Subsidiaries,
    TaxGroups,
    TaxItems,
    Terms,
    VendorBills,
    VendorPayments,
    Vendors,
)


class SourceNetsuite(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        netsuite_con_config_map = {
            "account": config["realm"],
            "consumer_key": config["consumer_key"],
            "consumer_secret": config["consumer_secret"],
            "token_key": config["token_key"],
            "token_secret": config["token_secret"],
        }
        try:
            netsuite_con = NetSuiteConnection(**netsuite_con_config_map)
            if len(netsuite_con.accounts.get_all()) > 0:
                return True, None
        except NetSuiteLoginError or NetSuiteRequestError as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        netsuite_con_config_map = {
            "account": config["realm"],
            "consumer_key": config["consumer_key"],
            "consumer_secret": config["consumer_secret"],
            "token_key": config["token_key"],
            "token_secret": config["token_secret"],
        }
        config["netsuite_con"] = NetSuiteConnection(**netsuite_con_config_map)
        return [
            Accounts(config),
            BillingAccounts(config),
            Classifications(config),
            Currencies(config),
            Customers(config),
            Departments(config),
            Employees(config),
            ExpenseReports(config),
            ExpenseCategories(config),
            Files(config),
            Folders(config),
            JournalEntries(config),
            Locations(config),
            Projects(config),
            Subsidiaries(config),
            TaxGroups(config),
            TaxItems(config),
            Terms(config),
            VendorBills(config),
            VendorPayments(config),
            Vendors(config),
        ]
