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
    def get_netsuite_connector(self, config: Mapping[str, Any]) -> NetSuiteConnection:
        return NetSuiteConnection(
            account=config["realm"],
            consumer_key=config["consumer_key"],
            consumer_secret=config["consumer_secret"],
            token_key=config["token_id"],
            token_secret=config["token_secret"],
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        _nc = self.get_netsuite_connector(config)
        return len(_nc.accounts.get_all()) > 0, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        _nc = self.get_netsuite_connector(config)
        return [
            Accounts(nc=_nc, name="accounts", config=config),
            Classifications(nc=_nc, name="classifications", config=config),
            Currencies(nc=_nc, name="currencies", config=config),
            Customers(nc=_nc, name="customers", config=config),
            Departments(nc=_nc, name="departments", config=config),
            Employees(nc=_nc, name="employees", config=config),
            ExpenseReports(nc=_nc, name="expense_reports", config=config),
            ExpenseCategories(nc=_nc, name="expense_categories", config=config),
            Files(nc=_nc, name="files", config=config),
            Folders(nc=_nc, name="folders", config=config),
            JournalEntries(nc=_nc, name="journal_entries", config=config),
            Locations(nc=_nc, name="locations", config=config),
            Projects(nc=_nc, name="projects", config=config),
            Subsidiaries(nc=_nc, name="subsidiaries", config=config),
            TaxGroups(nc=_nc, name="tax_groups", config=config),
            TaxItems(nc=_nc, name="tax_items", config=config),
            Terms(nc=_nc, name="terms", config=config),
            VendorBills(nc=_nc, name="vendor_bills", config=config),
            VendorPayments(nc=_nc, name="vendor_bills", config=config),
            Vendors(nc=_nc, name="vendors", config=config),
            # Investigate next issues:
            # 1) ExpensesReport # Trouble: Internal realization is implemented based on some request referring ti Employees table.
            # 2) BillingAccounts(nc=nc, name="billing_accounts", config=config),
            # 3) CustomLists getting the error: zeep.exceptions.Fault: org.xml.sax.SAXException: customList is not a legal value for
            # {urn:types.core_2019_1.platform.webservices.netsuite.com}GetAllRecordType
            # CustomLists(nc=nc, name="custom_lists", config=config),
            # CustomSegments(nc=nc, name="custom_segments", config=config),
            # CustomRecords(nc=nc, name="custom_records", config=config),
            # CustomRecordTypes(nc=nc, name="custom_record_types", config=config),
            # 4) SOAP method does not allow to use Search method (implemented as a default get_all())
            # It is not implemented by the SOAP interface
            # VendorCredits(nc=nc, name="vendor_credits", config=config),
            # Usages(nc=nc, name="usages", config=config),
        ]
