#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from netsuitesdk import NetSuiteConnection

from source_netsuite.streams import (
    Accounts,
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


class SourceNetsuiteSoap(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config_map = {
            "account": config["realm"],
            "consumer_key": config["consumer_key"],
            "consumer_secret": config["consumer_secret"],
            "token_key": config["token_id"],
            "token_secret": config["token_secret"],
        }

        try:
            _nc = NetSuiteConnection(**config_map)
        except:
            raise Exception("Connection error")

        return len(_nc.accounts.get_all()) > 0, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config_map = {
            "account": config["realm"],
            "consumer_key": config["consumer_key"],
            "consumer_secret": config["consumer_secret"],
            "token_key": config["token_id"],
            "token_secret": config["token_secret"],
        }

        try:
            _nc = NetSuiteConnection(**config_map)
        except:
            raise Exception("Connection error")

        return [
            Accounts(nc=_nc, config=config),
            Classifications(nc=_nc, config=config),
            Currencies(nc=_nc, config=config),
            Customers(nc=_nc, config=config),
            Departments(nc=_nc, config=config),
            Employees(nc=_nc, config=config),
            ExpenseReports(nc=_nc, config=config),
            ExpenseCategories(nc=_nc, config=config),
            Files(nc=_nc, config=config),
            Folders(nc=_nc, config=config),
            JournalEntries(nc=_nc, config=config),
            Locations(nc=_nc, config=config),
            Projects(nc=_nc, config=config),
            Subsidiaries(nc=_nc, config=config),
            TaxGroups(nc=_nc, config=config),
            TaxItems(nc=_nc, config=config),
            Terms(nc=_nc, config=config),
            VendorBills(nc=_nc, config=config),
            VendorPayments(nc=_nc, config=config),
            Vendors(nc=_nc, config=config),

            # FIXME (ExpensesReport): Trouble: Internal realization is implemented based on some request referring ti Employees table.
            # TODO (BillingAccounts): Getting error from SOAP side
            # TODO: (CustomLists) getting the error: zeep.exceptions.Fault: org.xml.sax.SAXException: customList is not a legal value for
            #  {urn:types.core_2019_1.platform.webservices.netsuite.com}GetAllRecordType
            # TODO: (CustomLists): Getting error from SOAP side
            # TODO: (CustomSegments): Getting error from SOAP side
            # TODO: (CustomRecords): Getting error from SOAP side
            # TODO: (CustomRecordTypes): Getting error from SOAP side
            # TODO: (VendorCredits): It is not implemented Search method for this method
            # TODO: (Usages): It is not implemented Search method for this method

        ]
